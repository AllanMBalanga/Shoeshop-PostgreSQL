from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import ServiceCreate, Status

#PYDANTIC validators

#Base response models
class BaseCustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    address: str
    created_at: datetime

    class Config:
        orm_mode = True

class BaseServiceResponse(BaseModel):
    id: int
    customer_id: int
    type: ServiceCreate
    total_cost: Optional[float] = 0
    date: datetime

    class Config:
        orm_mode = True

class BaseProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock_quantity: int
    created_at: datetime

    class Config:
        orm_mode = True

class BaseVariantResponse(BaseModel):
    id: int
    product_id: int
    size: str
    color: str
    stock_quantity: int

    class Config:
        orm_mode = True

class BaseRepairResponse(BaseModel):
    id: int
    request_id: int
    description: str
    status: Status
    created_at: datetime
    start_date: Optional[datetime] = None
    finished_date: Optional[datetime] = None

    class Config:
        orm_mode = True

class BaseItemRequestResponse(BaseModel):
    id: int
    request_id: int
    product_variant_id: int
    quantity: int
    unit_price: float
    created_at: datetime

    class Config:
        orm_mode = True

#Response model filtering
class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    address: str
    created_at: datetime
    services: Optional[List[BaseServiceResponse]] = []

    class Config:
        orm_mode = True

class ServiceResponse(BaseModel):
    id: int
    customer_id: int
    type: ServiceCreate
    total_cost: Optional[float] = 0
    date: datetime
    user: BaseCustomerResponse  #uses Customer Response as a response model
    repairs: Optional[List[BaseRepairResponse]] = []
    items: Optional[List[BaseItemRequestResponse]] = []

    class Config:
        orm_mode = True

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock_quantity: int
    created_at: datetime
    variants: Optional[List[BaseVariantResponse]] = []

    class Config:
        orm_mode = True

class VariantResponse(BaseModel):
    id: int
    product_id: int
    size: str
    color: str
    stock_quantity: int
    product: BaseProductResponse    #uses BaseProductResponse as a response model

    class Config:
        orm_mode = True

class RepairResponse(BaseModel):
    id: int
    request_id: int
    description: str
    status: Status
    created_at: datetime
    start_date: Optional[datetime] = None
    finished_date: Optional[datetime] = None
    service: BaseServiceResponse    #uses BaseServiceResponse as a response model

    class Config:
        orm_mode = True

class ItemRequestResponse(BaseModel):
    id: int
    request_id: int
    product_variant_id: int
    quantity: int
    unit_price: float
    created_at: datetime
    service: BaseServiceResponse    #uses BaseServiceResponse as a response model

    class Config:
        orm_mode = True

