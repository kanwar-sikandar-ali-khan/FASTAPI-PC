from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel

# Todo Model
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)

# Parent Models
class ParentBase(SQLModel):
    father_name: Optional[str] = Field(default=None, max_length=255)
    mother_name: Optional[str] = Field(default=None, max_length=255)

class Parent(ParentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cnic_number: str = Field(min_length=4, max_length=40)
    childRef: List["Child"] = Relationship(back_populates="parentRef")

    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types

class ParentRequest(SQLModel):
    father_name: Optional[str] = Field(default=None, max_length=255)
    mother_name: Optional[str] = Field(default=None, max_length=255)
    cnic_number: str = Field(min_length=4, max_length=40)

# Update ParentResponse to use BaseModel instead
class ParentResponse(BaseModel):
    id: Optional[int]
    father_name: Optional[str]
    mother_name: Optional[str]
    cnic_number: str

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLModel ORM



    
# Child Models
class ChildBase(SQLModel):
    child_name: Optional[str] = Field(default=None, max_length=255)

class ChildrenRequest(SQLModel):
    child_name: Optional[str] = Field(default=None, max_length=255)
    cnic_number: str = Field(min_length=4, max_length=40)

class Child(ChildBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(foreign_key="parent.id", nullable=False)
    father_name: Optional[str] = Field(max_length=255, nullable=False)  # Add father_name here
    parentRef: Optional[Parent] = Relationship(back_populates="childRef")  # Make parentRef Optional to avoid issues

    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types

class ChildResponse(BaseModel):
    id: Optional[int]
    child_name: Optional[str]
    parent_id: Optional[int]
    father_name: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True  # This allows the use of from_orm



class ParentResponseWithChildren(BaseModel):
    id: Optional[int]
    father_name: Optional[str]
    mother_name: Optional[str]
    cnic_number: str
    children: List[ChildResponse]  # Add children list here

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLModel ORM     