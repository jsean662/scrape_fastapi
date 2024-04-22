# scrape_fastapi

## Assumptions
- Instead of storing data in JSON form I've decided to store it in CSV format since its easier to append data to CSV as compared to CSV.
- Caching is implemented, but the requirement - "If the scraped product price has not changed, we don’t want to update the data of such a product in the DB" is difficult to implemnet since we are not using an proper database (having GET API).


