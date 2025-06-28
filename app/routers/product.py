from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from typing import List
from ..body import ValidProduct
from ..update import ValidProductPatch, ValidProductPut
from ..response import ProductResponse
from ..status_code import validate_product_exists, exception

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    product = db.query(models.Product).all()
    return product


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def create_product(product:ValidProduct, db: Session = Depends(get_db)):
    try:
        query = models.Product(**product.dict())
        db.add(query)
        db.commit()
        db.refresh(query)
        return query

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.get("/{id}", response_model=ProductResponse)
def get_one(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    validate_product_exists(product, id)

    return product


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: int, db: Session = Depends(get_db)):
    try:
        delete_query = db.query(models.Product).filter(models.Product.id == id)
        new_product = delete_query.first()
        validate_product_exists(new_product, id)
        
        delete_query.delete(synchronize_session=False)
        db.commit()
        return

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.put("/{id}", response_model=ProductResponse)
def update_product(id: int, product: ValidProductPut, db: Session = Depends(get_db)):
    try:
        update_query = db.query(models.Product).filter(models.Product.id == id)
        new_product = update_query.first()
        validate_product_exists(new_product, id)
        
        update_query.update(product.dict(), synchronize_session=False)
        db.commit()
        return update_query.first()

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.patch("/{id}", response_model=ProductResponse)
def update_product(id: int, product: ValidProductPatch, db: Session = Depends(get_db)):
    try:
        update_query = db.query(models.Product).filter(models.Product.id == id)
        new_product = update_query.first()
        validate_product_exists(new_product, id)
        
        update_query.update(product.dict(exclude_unset=True), synchronize_session=False)
        db.commit()
        return update_query.first()
    
    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)