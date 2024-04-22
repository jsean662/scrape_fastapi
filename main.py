from datetime import datetime
from typing import Optional
import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cachetools import TTLCache

from handlers.dentalstall import DentalStallHandler
from logging.config import dictConfig
from config import LogConfig


app = FastAPI()

cache = TTLCache(maxsize=100, ttl=86400)

# Static token
API_TOKEN = "your_static_token_here"

# Validate the token
def authenticate(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    if token.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return True


dictConfig(LogConfig().model_dump())
logger = logging.getLogger("scrape_fastapi")



@app.get("/get-products")
async def get_products(
    offset: Optional[int] = 1, 
    proxy: Optional[str] = "", 
    limit: int = 1,
    auth: bool = Depends(authenticate)
):
    if offset > limit:
        raise HTTPException(status_code=400, detail="Offset cannot be greater than limit")

    created_cnt = updated_cnt = unchanged_cnt = 0
    start_time = datetime.now()
    logger.info(f'Operation start time: {start_time.strftime("%Y-%m-%d %H:%M:%S")}.')
    
    handler = DentalStallHandler(limit=limit, offset=offset, proxy=proxy)
    product_pages = handler.get_products()

    for products in product_pages:
        for key in products:
            if cache.get(key) and cache.get(key) == products[key]["product_price"]:
                unchanged_cnt += 1
                continue
            if cache.get(key) and cache.get(key) != products[key]["product_price"]:
                updated_cnt += 1
                cache[key] = products[key]["product_price"]
                # logger.info(f'Product {products[key]["code"]} updated with new price {products[key]["product_price"]}')
            else:
                created_cnt += 1
                cache[key] = products[key]["product_price"]
                # logger.info(f'New product {products[key]["code"]} added with price {products[key]["product_price"]}')
            with open("data/dentalstall.csv", "a") as file:
                # Note: Since we are appending to the file, CSV file makes more sense than JSON
                # In case of JSON, we would have to read the file, update the data and write it back
                file.write(
                    f'{products[key]["code"]},{products[key]["product_title"]},{products[key]["short_title"]},{products[key]["product_price"]},{products[key]["path_to_image"]},{products[key]["product_url"]},{products[key]["product_price"]},{products[key]["scraped_at"]}\n'
                )

    logger.info(f"Operation completed successfully.")
    logger.info(f'Total products scraped: {created_cnt + updated_cnt + unchanged_cnt}.')
    logger.info(f'Summary: created: {created_cnt}; updated: {updated_cnt}; unchanged: {unchanged_cnt}.')
    logger.info(f'Total time taken in seconds to scrape: {(datetime.now() - start_time).seconds}.')
    logger.info(f'Operation end time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.')
    logger.info(f'Params used - Limit: {limit}; Offset: {offset}; Proxy: {proxy}.')
    
    return {
        "message": "Products scraped successfully",
        "total_products": created_cnt + updated_cnt + unchanged_cnt,
        "products_created": created_cnt, 
        "products_updated": updated_cnt, 
        "products_unchanged": unchanged_cnt,
        "params": {
            "limit": limit,
            "offset": offset,
            "proxy": proxy
        }
    }
    
    
# XPATHs for Dentalstall website
# /html/body/div[1]/div[2]/div/div/div/div[4]/ul/li[1] -> main card
# /html/body/div[1]/div[2]/div/div/div/div[4]/ul/li[1]/div/div[1]/a/img -> image
# /html/body/div[1]/div[2]/div/div/div/div[4]/ul/li[1]/div/div[2]/div[1]/h2/a   -> product url
# /html/body/div[1]/div[2]/div/div/div/div[4]/ul/li[1]/div/div[2]/div[2]/span[1]/ins/span/bdi   -> price v1
# /html/body/div[1]/div[2]/div/div/div/div[4]/ul/li[2]/div/div[2]/div[2]/span[1]/span[2]/bdi    -> price v2
# /html/body/div[1]/div[2]/div/div/div/div[4]/ul/li[15]/div/div[2]/div[2]/span/span/bdi         -> price v3