from pydantic import BaseModel, Field
from datetime import date

    
class CustomersReviewsModel(BaseModel):
    customer_id: str = Field(..., alias="customer_id", primary_key=True)
    review_id: str = Field(..., alias="review_id", primary_key=True)
    review_headline: str = Field(None, alias="review_headline")
    review_date: date = Field(None, alias="review_date")
    star_rating: int = Field(..., alias="star_rating")


class ProductsReviewsModel(BaseModel):
    product_id: str = Field(..., alias="product_id", partition_key=True)
    star_rating: int = Field(..., alias="star_rating", partition_key=True)
    review_id: str = Field(..., alias="review_id", primary_key=True)
    review_headline: str = Field(None, alias="review_headline")
    verified_purchase: bool = Field(None, alias="verified_purchase")


class MostReviewedProductsModel(BaseModel):
    product_id: str = Field(..., alias="product_id")
    product_title: str = Field(None, alias="product_title")
    reviews_number: int = Field(None, alias="reviews_number")


class MostProductiveCustomersModel(BaseModel):
    customer_id: str = Field(..., alias="customer_id")
    reviews_number: int = Field(None, alias="reviews_number")
