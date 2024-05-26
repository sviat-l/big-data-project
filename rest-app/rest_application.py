from fastapi import FastAPI, HTTPException, Path, Query
from typing import List
import cassandra_processing
import rest_models
import logging
from datetime import date
from mongo_processing import MongoDBClient

# Initialize logging
logging.basicConfig(level=logging.INFO, format='|%(asctime)s| - |%(name)s| - |%(levelname)s| - |%(message)s|')
logger = logging.getLogger(__name__)

CassandraService : cassandra_processing.CassandraService = None
    
# Initialize FastAPI app
app = FastAPI(title="Wikipedia Created Pages API", description="API to get information about Wikipedia created pages", version="1.0.0")
CassandraService = cassandra_processing.CassandraService()
mongo_client = MongoDBClient()

@app.post("/reconect-to-cassandra/")
def reconnect_to_cassandra():
    logger.info(f"Reconnecting to Cassandra")
    CassandraService.connect_to_db()
    return {"message": "Reconnected to Cassandra"}
    
@app.get("/domains/all/", response_model=rest_models.DomainModel)
def get_all_domains():
    logger.info(f"Getting all domains")
    result = CassandraService.find_all_domains()
    if not result or result is None:
        raise HTTPException(status_code=404, detail="Domains not found")
    return result

@app.get("/users/{user_id}/pages/", response_model=List[rest_models.UserPageModel])
def get_user_pages(user_id: int = Path(..., title="The ID of the user")):
    logger.info(f"Getting pages for user_id: {user_id}")
    result = CassandraService.find_user_pages(user_id)
    if not result or result is None:
        raise HTTPException(status_code=404, detail=f"Pages not found for {user_id}")
    return result

@app.get("/pages/{page_id}/", response_model=rest_models.PageModel)
def get_page(page_id: int = Path(..., title="The ID of the page")):
    logger.info(f"Getting page for page_id: {page_id}")
    result = CassandraService.find_page_info(page_id)
    if not result or result is None:
        raise HTTPException(status_code=404, detail=f"Page not found for {page_id}")
    return result

@app.get("/domains/{domain}/total/", response_model=rest_models.DomainPageModel)
def get_domain_pages(domain: str = Path(..., title="The domain")):
    logger.info(f"Getting pages for domain: {domain}")
    result = CassandraService.find_domain_pages(domain)
    if not result or result is None:
        raise HTTPException(status_code=404, detail=f"Pages not found for domain: {domain}")
    return result

@app.get("/pages-by-users/", response_model=List[rest_models.PagesByUsersModel])
def get_pages_by_users(from_dt: date = Query(..., title="The starting date"), 
                       to_dt: date = Query(..., title="The final date")):
    if from_dt > to_dt:
        raise HTTPException(status_code=400, detail=f"Starting from_date must be less than the Final to_date")
    logger.info(f"Getting pages by users", "from_date: ", from_dt, "to_date: ", to_dt)
    result = CassandraService.find_pages_by_users_in_timerange(from_dt, to_dt)
    if not result or result is None:
        raise HTTPException(status_code=404, detail="Pages not found")
    return result


# Category A (precomputed reports)
@app.get("/domains/stats/", response_model=List[rest_models.HourlyDomainStatsModel])
def get_domain_stats():
    result = mongo_client.get_domain_stats()
    if not result:
        raise HTTPException(status_code=404, detail="No hourly stats found")
    return result


@app.get("/domains/stats/by_bots/", response_model=List[rest_models.BotCreationStatsModel])
def get_bot_creation_stats():
    result = mongo_client.get_bot_creation_stats()
    if not result:
        raise HTTPException(status_code=404, detail="No bot creation stats found")
    return result


@app.get("/users/most-productive/", response_model=List[rest_models.TopUsersModel])
def get_top_users():
    result = mongo_client.get_most_productive()
    if not result:
        raise HTTPException(status_code=404, detail="No user data found")
    return result


# Define root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Wikipedia Created Pages API!"}
