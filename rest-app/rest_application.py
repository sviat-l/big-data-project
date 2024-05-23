from fastapi import FastAPI, HTTPException, Path
from typing import List
import cassandra_processing
import rest_models
import logging
from datetime import date

# Initialize logging
logging.basicConfig(level=logging.INFO, format='|%(asctime)s| - |%(name)s| - |%(levelname)s| - |%(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Define endpoint to get reviews by customer ID
@app.get("/customers/{customer_id}/reviews/", response_model=List[rest_models.CustomersReviewsModel])
async def get_reviews_by_customer_id(customer_id: str = Path(..., title="The ID of the customer")):
    logger.info(f"Getting reviews for customer_id: {customer_id}")
    result = cassandra_processing.find_reviews_by_customer_id(customer_id)
    if not result or result is None:
        raise HTTPException(status_code=404, detail=f"Reviews not found for {customer_id}")
    return result


@app.get("/products/{product_id}/reviews/", response_model=List[rest_models.ProductsReviewsModel])
async def get_reviews_by_product_id(product_id: str = Path(..., title="The ID of the product"), star_rating: int|None = None):
    logger.info(f"Getting reviews for product_id: {product_id}, with star_rating: {star_rating}")

    if star_rating is not None and (star_rating < 1 or star_rating > 5):
        raise HTTPException(status_code=400, detail=f"Invalid star_rating: {star_rating}. Must be int between 1 and 5")

    result = cassandra_processing.find_reviews_by_product_id(product_id, star_rating=star_rating)
    if not result or result is None:
        datail_str = f"Reviews not found for {product_id}"
        if star_rating is not None:
            datail_str += f" with star_rating: {star_rating}"
        raise HTTPException(status_code=404, detail=datail_str)
    return result

@app.get("/products/most-popular/", response_model=List[rest_models.MostReviewedProductsModel])
async def get_most_reviewed_products(from_date: date, to_date: date, limit: int|None = 10):

    logger.info(f"Getting most reviewed products", "from_date: ", from_date, "to_date: ", to_date, "limit: ", limit)
    
    if from_date > to_date:
        raise HTTPException(status_code=400, detail=f"Starting from_date must be less than the Final to_date")
    
    result = cassandra_processing.find_most_reviewed_products(from_date, to_date, limit)
    return result

@app.get("/customers/most-productive/", response_model=List[rest_models.MostProductiveCustomersModel])
def get_most_productive_customers(from_date: date, to_date: date, limit: int = 10, verified_only: bool|None = False,
                                  review_type: str|None = None):
    if from_date > to_date:
        raise HTTPException(status_code=400, detail=f"Starting from_date must be less than the Final to_date")
    
    logger.info(f"Getting most productive customers", "from_date: ", from_date, "to_date: ", to_date, "limit: ", limit, "verified_only: ", verified_only, "review_type: ", review_type)
    result = cassandra_processing.find_most_productive_customers(from_date, to_date, limit, verified_only, review_type)
    return result

# Define root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the reviews API!"}

