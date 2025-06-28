from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from typing import List
from ..oauth2 import get_current_user
from ..body import ItemRequest, TokenData
from ..update import ItemRequestPatch, ItemRequestPut
from ..response import ItemRequestResponse
from ..status_code import validate_customer_ownership, validate_item_request_exists, validate_customer_exists, validate_type_of_service, validate_service_exists, exception

#The product_variant_id would be included in the request body when creating/updating item requests.

router = APIRouter(
    prefix="/customers/{customer_id}/services/{service_id}/items",
    tags=["Item Requests"]
) 

@router.get("/", response_model=List[ItemRequestResponse])
def get_items(customer_id: int, service_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    validate_customer_exists(customer, customer_id)
    
    service = db.query(models.ServiceRequest).filter(
        models.ServiceRequest.id == service_id,
        models.ServiceRequest.customer_id == customer_id
        ).first()
    
    validate_service_exists(service, service_id)
    validate_type_of_service(service.type, models.ServiceCreate.sale)
    
    item_request = db.query(models.ItemRequest).filter(models.ItemRequest.request_id == service_id).all()
    return item_request


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ItemRequestResponse)
def post_item_request(customer_id: int, service_id: int, item_request: ItemRequest, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)

        service = db.query(models.ServiceRequest).filter(
            models.ServiceRequest.id == service_id,
            models.ServiceRequest.customer_id == customer_id
            ).first()
        
        validate_service_exists(service, service_id)
        validate_type_of_service(service.type, models.ServiceCreate.sale)
        
        validate_customer_ownership(service.customer_id, current_user.id)

        item_request_data = item_request.dict()
        item_request_data["request_id"] = service_id

        new_item_request = models.ItemRequest(**item_request_data)
        db.add(new_item_request)
        db.commit()
        db.refresh(new_item_request)
        return new_item_request

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.get("/{item_id}", response_model=ItemRequestResponse)
def get_one_item(customer_id: int, service_id: int, item_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    validate_customer_exists(customer, customer_id)
    
    service = db.query(models.ServiceRequest).filter(
        models.ServiceRequest.id == service_id,
        models.ServiceRequest.customer_id == customer_id
        ).first()
    
    validate_service_exists(service, service_id)
    validate_type_of_service(service.type, models.ServiceCreate.sale)

    item_request = db.query(models.ItemRequest).filter(
        models.ItemRequest.id == item_id,
        models.ItemRequest.request_id == service_id
    ).first()

    validate_item_request_exists(item_request, item_id)

    return item_request


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_request(customer_id: int, service_id: int, item_id: int, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)
        
        service = db.query(models.ServiceRequest).filter(
            models.ServiceRequest.id == service_id,
            models.ServiceRequest.customer_id == customer_id
        ).first()
        
        validate_service_exists(service, service_id)
        validate_type_of_service(service.type, models.ServiceCreate.sale)

        validate_customer_ownership(service.customer_id, current_user.id)

        delete_query = db.query(models.ItemRequest).filter(
            models.ItemRequest.id == item_id,
            models.ItemRequest.request_id == service_id
        )
        item_request = delete_query.first()

        validate_item_request_exists(item_request, item_id)

        delete_query.delete(synchronize_session=False)
        db.commit()
        return

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.put("/{item_id}", response_model=ItemRequestResponse)
def put_item_request(customer_id: int, service_id: int, item_id: int, item_request: ItemRequestPut, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)

        service = db.query(models.ServiceRequest).filter(
            models.ServiceRequest.id == service_id,
            models.ServiceRequest.customer_id == customer_id
        ).first()

        validate_service_exists(service, service_id)
        validate_type_of_service(service.type, models.ServiceCreate.sale)

        validate_customer_ownership(service.customer_id, current_user.id)

        put_query = db.query(models.ItemRequest).filter(
            models.ItemRequest.id == item_id, 
            models.ItemRequest.request_id == service_id
        )
        existing_item = put_query.first()

        validate_item_request_exists(existing_item, item_id)

        # Get update data
        update_data = item_request.dict()

        # Prevent product_variant_id updates
        if "product_variant_id" in update_data:
            if update_data["product_variant_id"] != existing_item.product_variant_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product variant cannot be changed after creation"
                )
            update_data.pop("product_variant_id")

        put_query.update(update_data, synchronize_session=False)
        db.commit()
        return put_query.first()

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


#If product_variant_id is the only data in body, it will not be accepted
@router.patch("/{item_id}", response_model=ItemRequestResponse)
def update_item_request(customer_id: int, service_id: int, item_id: int, item_request:ItemRequestPatch, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    try:
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        validate_customer_exists(customer, customer_id)

        service = db.query(models.ServiceRequest).filter(
            models.ServiceRequest.id == service_id,
            models.ServiceRequest.customer_id == customer_id
        ).first()
        validate_service_exists(service, service_id)
        validate_type_of_service(service.type, models.ServiceCreate.sale)

        validate_customer_ownership(service.customer_id, current_user.id)

        patch_query = db.query(models.ItemRequest).filter(
            models.ItemRequest.id == item_id,
            models.ItemRequest.request_id == service_id
        )
        existing_item = patch_query.first()

        validate_item_request_exists(existing_item, item_id)

        # Get update data and exclude product_variant_id to prevent changes
        update_data = item_request.dict(exclude_unset=True)

        # Prevent product_variant_id updates
        if "product_variant_id" in update_data:
            if update_data["product_variant_id"] != existing_item.product_variant_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product variant cannot be changed after creation"
                )
            update_data.pop("product_variant_id")

        # Ensure at least one field is being updated
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update"
            )
        
        patch_query.update(update_data, synchronize_session=False)
        db.commit()
        return patch_query.first()

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)