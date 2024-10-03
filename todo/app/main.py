from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from fastapi import FastAPI, Depends,HTTPException
from typing import AsyncGenerator
from app.models import Todo, Parent, ParentRequest, ParentResponse ,ChildrenRequest,Child,ChildResponse,ParentResponseWithChildren
from app import crud



# Replace postgresql with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

# Recycle connections after 5 minutes to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Hello World API with DB",
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8000",  # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
    ]
)

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/")
def read_root():
    return {"Hello": "World kanwar dev container changes k hnn"}

@app.post("/todos/", response_model=Todo)
def create_todo(
    todo: Todo,
    session: Annotated[Session, Depends(get_session)]
) -> Todo:
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos


# Parent APIS
@app.post("/parent/create", response_model=ParentResponse)
def create_Parent(
    parent_req: ParentRequest,
    session: Annotated[Session, Depends(get_session)]
) -> ParentResponse:
    """
    Create new Parent without the need to be logged in.
    """
    parent = crud.checkExistParent(session=session, cnic_number=parent_req.cnic_number)
    if parent:
        raise HTTPException(
            status_code=400,
            detail="The parent with this cnic_number already exists in the system",
        )

    # Create a new Parent instance from the validated request
    parent_obj = Parent(
        father_name=parent_req.father_name,
        mother_name=parent_req.mother_name,
        cnic_number=parent_req.cnic_number
    )

    # Use the create_parent function from crud
    parent = crud.create_parent(session=session, parentObj=parent_obj)
    return parent

@app.get("/parent/{parent_id}", response_model=ParentResponseWithChildren)
def get_parent_by_id(
    parent_id: int,
    session: Annotated[Session, Depends(get_session)]
) -> ParentResponseWithChildren:
    """
    Get a specific parent by their ID and include a list of children.
    """
    # Fetch the parent by ID
    parent = session.exec(select(Parent).where(Parent.id == parent_id)).first()
    
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    
    # Fetch the children associated with the parent
    children = session.exec(select(Child).where(Child.parent_id == parent_id)).all()
    
    # Convert each Child ORM instance to ChildResponse
    children_responses = [ChildResponse.from_orm(child) for child in children]
    
    # Create a ParentResponseWithChildren object and populate it
    return ParentResponseWithChildren(
        id=parent.id,
        father_name=parent.father_name,
        mother_name=parent.mother_name,
        cnic_number=parent.cnic_number,
        children=children_responses  # Use the converted child responses here
    )



# Children APIS

@app.post("/children/create", response_model=ChildResponse)
def create_child(
    child_req: ChildrenRequest,
    session: Annotated[Session, Depends(get_session)]
):
    # Check if the parent exists with the provided CNIC number
    parent = crud.checkExistParent(session=session, cnic_number=child_req.cnic_number)
    if not parent:
        raise HTTPException(
            status_code=400,
            detail="The parent with this cnic_number does not exist in the system",
        )
    
    # Create a new Child instance, ensuring the parent_id and father_name are set
    create_row_child = Child(
        child_name=child_req.child_name,
        parent_id=parent.id,  # Link the child to the correct parent
        father_name=parent.father_name  # Copy father_name from the parent
    )

    # Insert the child record into the database
    insert_table_child = crud.create_child(session=session, childRow=create_row_child)
    
    
    # Return the inserted child record with father_name correctly mapped to father_names
    return insert_table_child