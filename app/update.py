from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .models import ServiceCreate, Status

#PYDANTIC validators

#PUT filtering, not optional
class CustomerPut(BaseModel):
    name: str
    email: EmailStr
    password: str
    address: str

class ServicePut(BaseModel):
    type: ServiceCreate
    total_cost: float = 0

class ValidProductPut(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int = 0

class VariantPut(BaseModel):
    size: str
    color: str
    stock_quantity: int = 0

class RepairPut(BaseModel):
    description: str
    status: Status

class ItemRequestPut(BaseModel):
    product_variant_id: int
    quantity: int
    unit_price: float



#PATCH filtering, optional in the Postman Body
class CustomerPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    address: Optional[str] = None

class ServicePatch(BaseModel):
    type: Optional[ServiceCreate] = None
    total_cost: Optional[float] = None

class ValidProductPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None

class VariantPatch(BaseModel):
    size: Optional[str] = None
    color: Optional[str] = None
    stock_quantity: Optional[int] = None

class RepairPatch(BaseModel):
    description: Optional[str] = None
    status: Optional[Status] = None

class ItemRequestPatch(BaseModel):
    product_variant_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None