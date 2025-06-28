from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, utils
from ..body import Customer, TokenData
from ..update import CustomerPatch, CustomerPut
from ..response import CustomerResponse
from typing import List
from ..oauth2 import get_current_user
from ..status_code import validate_customer_exists, validate_customer_ownership, exception

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

@router.get("/", response_model=List[CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    post = db.query(models.Customer).all()
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CustomerResponse)
def create_customer(customer: Customer, db: Session = Depends(get_db)):
    try:
        #hash password
        customer.password = utils.hash(customer.password)
        
        customer = models.Customer(**customer.dict())
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.get("/{id}", response_model=CustomerResponse)
def get_customer(id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == id).first()

    validate_customer_exists(customer, id)
    
    return customer


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(id: int, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        delete_query = db.query(models.Customer).filter(models.Customer.id == id)
        customer = delete_query.first()
        validate_customer_exists(customer, id)
        validate_customer_ownership(customer.id, current_user.id)

        delete_query.delete(synchronize_session=False)
        db.commit()
        return
    
    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.put("/{id}", response_model=CustomerResponse)
def update_customer(id: int, customer:CustomerPut, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        update_query = db.query(models.Customer).filter(models.Customer.id == id)
        new_customer = update_query.first()
        validate_customer_exists(new_customer, id)
        validate_customer_ownership(new_customer.id, current_user.id)
        
        update_query.update(customer.dict(), synchronize_session=False)
        db.commit()

        return update_query.first()

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.patch("/{id}", response_model=CustomerResponse)
def patch_customer(id: int, customer:CustomerPatch, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        patch_query = db.query(models.Customer).filter(models.Customer.id == id)
        new_customer = patch_query.first()
        validate_customer_exists(new_customer, id)
        validate_customer_ownership(new_customer.id, current_user.id)

        #exclude_unset - skips missing fields in updates
        patch_query.update(customer.dict(exclude_unset=True), synchronize_session=False)
        db.commit()

        return patch_query.first()
    
    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)