from fastapi import APIRouter, status, Depends, HTTPException
from .. import models
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List
from datetime import datetime
from ..oauth2 import get_current_user
from ..body import Repair, TokenData
from ..update import RepairPatch, RepairPut
from ..response import RepairResponse
from ..status_code import validate_customer_exists, validate_service_exists, validate_repair_exists, validate_type_of_service, validate_customer_ownership, exception

router = APIRouter(
    prefix="/customers/{customer_id}/services/{service_id}/repairs",
    tags=["Repairs"]
)

@router.get("/", response_model=List[RepairResponse])
def get_all_by_url(customer_id: int, service_id: int, db: Session = Depends(get_db)):
    # Check if customer exists in database
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    validate_customer_exists(customer, customer_id)

    # Check if service exists and belongs to the given customer
    service = db.query(models.ServiceRequest).filter(
        models.ServiceRequest.id == service_id, 
        models.ServiceRequest.customer_id == customer_id
        ).first()
    validate_service_exists(service, service_id)

    validate_type_of_service(service.type, models.ServiceCreate.repair)

    repair = db.query(models.Repair).filter(
        models.Repair.request_id == service_id).all()

    return repair


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RepairResponse)
def create_post(customer_id: int, service_id: int, repair: Repair, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        # Check if customer exists in database
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)

        # Check if service exists and belongs to the given customer
        service = db.query(models.ServiceRequest).filter(
            models.ServiceRequest.id == service_id,
            models.ServiceRequest.customer_id == customer_id
            ).first()
        validate_service_exists(service, service_id)
        validate_type_of_service(service.type, models.ServiceCreate.repair)

        validate_customer_ownership(service.customer_id, current_user.id)

        #since request_id is not being passed in the postman body, set its value manually
        repair_data = repair.dict()
        repair_data["request_id"] = service_id

        new_repair = models.Repair(**repair_data)

        # Automatically set the finished_date if the repair is marked as completed
        if new_repair.status == models.Status.COMPLETED:
            new_repair.finished_date = datetime.utcnow()

        db.add(new_repair)
        db.commit()
        db.refresh(new_repair)
        return new_repair
    
    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.get("/{repair_id}", response_model=RepairResponse)
def get_one_repair(customer_id: int, service_id: int, repair_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    validate_customer_exists(customer, customer_id)

    service = db.query(models.ServiceRequest).filter(
        models.ServiceRequest.id == service_id,
        models.ServiceRequest.customer_id == customer_id
    ).first()
    validate_service_exists(service, service_id)

    validate_type_of_service(service.type, models.ServiceCreate.repair)
    
    repair = db.query(models.Repair).filter(
        models.Repair.id == repair_id,
        models.Repair.request_id == service_id
        ).first()
    validate_repair_exists(repair, repair_id)

    return repair


@router.delete("/{repair_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(customer_id: int, service_id: int, repair_id: int, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)
        
        service = db.query(models.ServiceRequest).filter(
            models.ServiceRequest.id == service_id,
            models.ServiceRequest.customer_id == customer_id
            ).first()
        validate_service_exists(service, service_id)
        validate_type_of_service(service.type, models.ServiceCreate.repair)

        delete_query = db.query(models.Repair).filter(
            models.Repair.id == repair_id,
            models.Repair.request_id == service_id
            )
        repair = delete_query.first()
        validate_repair_exists(repair, repair_id)

        validate_customer_ownership(service.customer_id, current_user.id)
        
        delete_query.delete(synchronize_session=False)
        db.commit()
        return

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)
    

@router.put("/{repair_id}", response_model=RepairResponse)
def update_repair(customer_id: int, service_id: int, repair_id: int, repair: RepairPut, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)

        service = db.query(models.ServiceRequest).filter(
            models.ServiceRequest.id == service_id,
            models.ServiceRequest.customer_id == customer_id
            ).first()
        validate_service_exists(service, service_id)
        validate_type_of_service(service.type, models.ServiceCreate.repair)

        update_query = db.query(models.Repair).filter(
            models.Repair.id == repair_id,
            models.Repair.request_id == service_id
            )
        new_repair = update_query.first()
        validate_repair_exists(new_repair, repair_id)

        validate_customer_ownership(service.customer_id, current_user.id)
        
        #If the update is marked as IN_PROGRESS or COMPLETED, add the current time to finished date
        repair_data = repair.dict()
        if repair.status == models.Status.IN_PROGRESS:
            repair_data["start_date"] = datetime.utcnow()
        if repair.status == models.Status.COMPLETED:
            repair_data["finished_date"] = datetime.utcnow()

        #Handles if changing from completed to either in_progres or pending (misinput).
        elif new_repair.status == models.Status.COMPLETED and repair.status and repair.status != models.Status.COMPLETED:
            repair_data["finished_date"] = None

        #Handles changes if reverting IN_PROGRESS or COMPLETED back to PENDING
        if new_repair.status != models.Status.PENDING and repair.status == models.Status.PENDING:
            repair_data["start_date"] = None
            
        update_query.update(repair_data, synchronize_session=False)
        db.commit()
        return update_query.first()

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.patch("/{repair_id}", response_model=RepairResponse)
def update_repair(customer_id: int, service_id: int, repair_id: int, repair: RepairPatch, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)
        
        service = db.query(models.ServiceRequest).filter(
            models.ServiceRequest.id == service_id,
            models.ServiceRequest.customer_id == customer_id
            ).first()
        validate_service_exists(service, service_id)
        validate_type_of_service(service.type, models.ServiceCreate.repair)

        update_query = db.query(models.Repair).filter(
            models.Repair.id == repair_id,
            models.Repair.request_id == service_id
            )
        new_repair = update_query.first()
        validate_repair_exists(new_repair, repair_id)

        validate_customer_ownership(service.customer_id, current_user.id)
        
        #If the update is marked as IN_PROGRESS or COMPLETED, add the current time to finished date
        repair_data = repair.dict(exclude_unset=True)
        if repair.status == models.Status.IN_PROGRESS:
            repair_data["start_date"] = datetime.utcnow()
        if repair.status == models.Status.COMPLETED:
            repair_data["finished_date"] = datetime.utcnow()

        #Handles if changing from completed to either in_progres or pending (misinput).
        elif new_repair.status == models.Status.COMPLETED and repair.status and repair.status != models.Status.COMPLETED:
            repair_data["finished_date"] = None

        #Handles changes if reverting IN_PROGRESS or COMPLETED back to PENDING
        if new_repair.status != models.Status.PENDING and repair.status == models.Status.PENDING:
            repair_data["start_date"] = None
            
        update_query.update(repair_data, synchronize_session=False)
        db.commit()
        return update_query.first()
    
    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)