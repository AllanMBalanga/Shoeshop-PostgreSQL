from fastapi import status, HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from typing import List
from ..body import Variant
from ..update import VariantPatch, VariantPut
from ..response import VariantResponse
from ..status_code import validate_product_exists, validate_variant_exists, exception


router = APIRouter(
    prefix="/products/{product_id}/variants",
    tags=["Product Variants"]
)


@router.get("/", response_model=List[VariantResponse])
def get_variants_by_product(product_id: int, db: Session = Depends(get_db)):
    # verify if product exists by checking if models.Product.id == product_id, 
    # where Product.id is the id from products table, and product_id comes from the URL
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    validate_product_exists(product, product_id)
    
    #filter by product_id
    query = db.query(models.ProductVariant).filter(models.ProductVariant.product_id == product_id).all()
    return query


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VariantResponse)
def post_variant(product_id: int, variant: Variant, db: Session = Depends(get_db)):
    try:
        #verify if product exists
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        validate_product_exists(product, product_id)
        
        #since product_id is not being passed in the postman body, set its value manually
        variant_data = variant.dict()
        variant_data["product_id"] = product_id

        variant = models.ProductVariant(**variant_data)
        db.add(variant)
        db.commit()
        db.refresh(variant)
        return variant

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.get("/{variant_id}", response_model=VariantResponse)
def get_one_variant(product_id: int, variant_id: int, db: Session = Depends(get_db)):
    #verify if product exists
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    validate_product_exists(product, product_id)
    
    #gets the row based on productvariant id and product_id coming from variant_id and product_id (URL)
    #(SELECT * FROM product_variants WHERE id = variant_id AND product_id = product_id)
    variant = db.query(models.ProductVariant).filter(
        models.ProductVariant.id == variant_id,
        models.ProductVariant.product_id == product_id
        ).first()
    validate_variant_exists(variant, variant_id)
    
    return variant


@router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variant(product_id: int, variant_id: int, db: Session = Depends(get_db)):
    try:
        #verify if product exists
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        validate_product_exists(product, product_id)
        
        #(SELECT * FROM product_variants WHERE id = variant_id AND product_id = product_id)
        delete_query = db.query(models.ProductVariant).filter(
            models.ProductVariant.id == variant_id,
            models.ProductVariant.product_id == product_id
            )
        variant = delete_query.first()
        validate_variant_exists(variant, variant_id)
        
        delete_query.delete(synchronize_session=False)
        db.commit()
        return

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.put("/{variant_id}", response_model=VariantResponse)
def update_variant(product_id: int, variant_id: int, variant: VariantPut, db: Session = Depends(get_db)):
    try:
        #verify if product exists
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        validate_product_exists(product, product_id)
        
        #(SELECT * FROM product_variants WHERE id = variant_id AND product_id = product_id)
        update_query = db.query(models.ProductVariant).filter(
            models.ProductVariant.id == variant_id,
            models.ProductVariant.product_id == product_id
            )
        new_variant = update_query.first()
        validate_variant_exists(new_variant, variant_id)
        
        update_query.update(variant.dict(), synchronize_session=False)
        db.commit()
        return update_query.first()

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)


@router.patch("/{variant_id}", response_model=VariantResponse)
def update_variant(product_id: int, variant_id: int, variant: VariantPatch, db: Session = Depends(get_db)):
    try:
        #verify if product exists
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        validate_product_exists(product, product_id)
        
        #(SELECT * FROM product_variants WHERE id = variant_id AND product_id = product_id)
        update_query = db.query(models.ProductVariant).filter(
            models.ProductVariant.id == variant_id,
            models.ProductVariant.product_id == product_id
            )
        new_variant = update_query.first()
        validate_variant_exists(new_variant, variant_id)
        
        update_query.update(variant.dict(exclude_unset=True), synchronize_session=False)
        db.commit()
        return update_query.first()

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        db.rollback()
        exception(e)