import hashlib
from typing import Optional
from pydantic import BaseModel, Field, computed_field

class Product(BaseModel):
    product_title: str
    product_price: Optional[float] = Field(default=0)
    path_to_image: str

    @computed_field
    @property
    def hash_key(self) -> str:
        value = self.product_title + str(self.product_price) + self.path_to_image
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
