from pydantic import BaseModel

# Base schema with common attributes
class CustomerBase(BaseModel):
    name: str
    email: str
    status: str
    
class CustomerUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    status: str | None = None
    
# Schema for creating a customer (doesn't need an ID)
class CustomerCreate(CustomerBase):
    pass




# Schema for reading a customer (includes the ID from the database)
class Customer(CustomerBase):
    id: int

    class Config:
        from_attributes = True 