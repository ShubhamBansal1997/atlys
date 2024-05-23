from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, HttpUrl
from app.scraper import Scraper
from app.utils import load_config

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

config = load_config()

def authenticate_token(token: str = Depends(oauth2_scheme)):
    if token != config["auth_token"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

class ScrapeRequest(BaseModel):
    limit: int = 5
    proxy: HttpUrl = None

@app.post("/scrape", dependencies=[Depends(authenticate_token)])
def scrape(scrape_request: ScrapeRequest):
    # TODO: add more parameters to the scraper
    # TODO: Make the task of the scraper async for better performance
    scraper = Scraper(limit=scrape_request.limit, proxy=str(scrape_request.proxy))
    products_scraped, products_saved, failed_requests = scraper.scrape()
    return {"scraped_products": products_scraped, "products_saved": products_saved, "failed_requests": failed_requests}
