# Scrape fastapi
- Scrape data from [Dentalstall](https://dentalstall.com/shop) using FastAPI and lxml libraries
- Following data points are scraped:
    - Product name
    - Product URL
    - Product image(URL)
    - Product price


## API
- `get-products` - GET request to get products from Dentalstall website
- Params:
    - `limit` - Used to specify the number of records to return. Optional, default is 1
    - `offset` - Skips the offset rows before beginning to return the rows. Optional, default is 1
    - `proxy` - Dictionary mapping protocol to the URL of the proxy. Optional, default is empty
- Auth:
    - Static token based authentication using Bearer token
- Returns:
    - `message` - str
    - `total_products` - int
    - `products_created` - int
    - `products_updated` - int
    - `products_unchanged` - int
    - `params` - dict
- Logs:
    - INFO level logs for start and end of operation
    - INFO level logs for total products scraped
    - INFO level logs for summary of created, updated and unchanged products
    - INFO level logs for total time taken in seconds to scrape
    - INFO level logs for params used - Limit, Offset, Proxy
    - ERROR level logs for failed requests


## Assumptions
- Instead of storing data in JSON form I've decided to store it in CSV format since its easier to append data to CSV as compared to CSV.
- Caching is implemented, but the requirement - "If the scraped product price has not changed, we don’t want to update the data of such a product in the DB" is difficult to implemnet since we are not using an proper database (having GET API).

