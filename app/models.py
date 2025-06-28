from .database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, Boolean, String, Enum, Float, CheckConstraint, UniqueConstraint
from sqlalchemy.sql.expression import text
import enum
from sqlalchemy.orm import relationship

#CREATE TABLE

#class variable is from postgresql, variable value from postman body. Based from observation, if for some reason the enum from postgresql is in uppercase, 
# the class variable must be in uppercase. This in turn converts the uppercase value in row into lowercase in postman.
class ServiceCreate(enum.Enum):
    sale = "sale"
    repair = "repair"

class Status(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

#/customers
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    address = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    #references ServiceRequest class and user attribute
    services = relationship("ServiceRequest", back_populates="user")

#/customers/{customer_id}/service
class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, nullable=False, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    total_cost = Column(Float, default=0)
    date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    type = Column(Enum(ServiceCreate, name="service_enum", create_constraint=False), nullable=False)
    
    #references the Customer class and services attribute
    user = relationship("Customer", back_populates="services")

    #references Repair and ItemRequest class and service attributes
    repairs = relationship("Repair", back_populates="service")
    items = relationship("ItemRequest", back_populates="service")

#/product" 
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False) 
    stock_quantity = Column(Integer, nullable=False, server_default=text("0"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    #references ProductVariant class and product attribute
    variants = relationship("ProductVariant", back_populates="product")

    #changes on price and stock must not be < 0
    __table_args__ = (
        CheckConstraint('price >= 0', name="check_positive_price"),
        CheckConstraint('stock_quantity >= 0', name="check_stock_positive")
    )

#product/{product_id}/variant
class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, nullable=False, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    size = Column(String, nullable=False)
    color = Column(String, nullable=False)
    stock_quantity = Column(Integer, nullable=False, server_default=text("0"))
    
    #references the Product class and variants attribute
    product = relationship("Product", back_populates="variants")

    __table_args__ = (
        CheckConstraint('stock_quantity >= 0', name="check_variant_stock_positive"),
    )

#/customers/customer_id/services/service_id/repairs
class Repair(Base):
    __tablename__ = "repairs"

    id = Column(Integer, primary_key=True, nullable=False)
    request_id = Column(Integer, ForeignKey("service_requests.id", ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(Status, name="repair_enum"), default="pending")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    start_date = Column(TIMESTAMP(timezone=True), nullable=True)
    finished_date = Column(TIMESTAMP(timezone=True), nullable=True)
    
    #references ServiceRequest class and repairs attribute
    service = relationship("ServiceRequest", back_populates="repairs")

#"/customers/customer_id/services/service_id/items"
class ItemRequest(Base):
    __tablename__ = "item_requests"

    id = Column(Integer, primary_key=True, nullable=False)
    request_id = Column(Integer, ForeignKey("service_requests.id", ondelete="CASCADE"), nullable=False)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    #references ServiceRequest class and items attribute
    service = relationship("ServiceRequest", back_populates="items")

    __table_args__ = (
        UniqueConstraint('request_id', 'product_variant_id', name='unique_request_variant'),    #each combination will only appear once
        CheckConstraint('quantity > 0', name="check_positive_quantity"),
        CheckConstraint('unit_price >= 0', name="check_positive_price")
    )