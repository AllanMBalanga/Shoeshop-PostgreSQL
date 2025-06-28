
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from typing import List
from ..oauth2 import get_current_user
from ..body import Service, TokenData
from ..update import ServicePatch, ServicePut
from ..response import ServiceResponse
from ..status_code import validate_customer_exists, validate_customer_ownership, validate_service_exists, exception

router = APIRouter(
    prefix="/customers/{customer_id}/services",
    tags=["Services"]
)

@router.get("/", response_model=List[ServiceResponse])
def get_service_by_customer(customer_id: int, db: Session = Depends(get_db)):
    #verify if customer exists by checking if models.Customer.id == customer_id, 
    #where Customer.id is the id from customers table, and customer_id comes from the URL
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    validate_customer_exists(customer, customer_id)

    #filter by customer_id
    service = db.query(models.ServiceRequest).filter(models.ServiceRequest.customer_id == customer_id).all()
    return service


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ServiceResponse)
def create_service(customer_id: int, service: Service, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        #verify if customer exists
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)
        validate_customer_ownership(customer.id, current_user.id)

        #since customer_id is not being passed in the postman body, set its value manually
        service_data = service.dict()
        service_data["customer_id"] = customer_id

        user = models.ServiceRequest(**service_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(customer_id: int, service_id: int, db: Session = Depends(get_db)):
    #verify if customer exists
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    validate_customer_exists(customer, customer_id)
    
    #gets the row based on ServiceRequest id and customer_id coming from service_id and customer_id (URL)
    #(SELECT * FROM service_requests WHERE id = service_id AND customer_id = customer_id)
    service = db.query(models.ServiceRequest).filter(
        models.ServiceRequest.id == service_id,
        models.ServiceRequest.customer_id == customer_id
        ).first()
    validate_service_exists(service, service_id)

    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(customer_id: int, service_id: int, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        #verify if customer exists
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)
        
        #(SELECT * FROM service_requests WHERE id = service_id AND customer_id = customer_id)
        delete_query = db.query(models.ServiceRequest).filter(
            models.ServiceRequest.id == service_id,
            models.ServiceRequest.customer_id == customer_id
            )
        
        service = delete_query.first()
        validate_service_exists(service, service_id)
        validate_customer_ownership(service.customer_id, current_user.id)

        delete_query.delete(synchronize_session=False)
        db.commit()
        return

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(customer_id: int, service_id: int, service: ServicePut, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        #verify if customer exists
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)
        
        put_query = db.query(models.ServiceRequest).filter(
            models.ServiceRequest.id == service_id,
            models.ServiceRequest.customer_id == customer_id
        )

        new_service = put_query.first()
        validate_service_exists(new_service, service_id)
        validate_customer_ownership(new_service.customer_id, current_user.id)
        
        put_query.update(service.dict(), synchronize_session=False)
        db.commit()

        return put_query.first()

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service(customer_id: int, service_id: int, service:ServicePatch, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        #verify if customer exists
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)
        
        #(SELECT * FROM service_requests WHERE id = service_id AND customer_id = customer_id)
        patch_query = db.query(models.ServiceRequest).filter(
            models.ServiceRequest.id == service_id,
            models.ServiceRequest.customer_id == customer_id
            )
        
        new_service = patch_query.first()
        validate_service_exists(new_service, service_id)
        validate_customer_ownership(new_service.customer_id, current_user.id)
        
        patch_query.update(service.dict(exclude_unset=True), synchronize_session=False)
        db.commit()

        return patch_query.first()

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)

