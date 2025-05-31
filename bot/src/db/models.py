from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class Product(BaseModel):
    id: UUID
    name: str
    description: str
    price: Decimal
    image: str


class Promo(BaseModel):
    id: int
    text: str
    cover: str
    link: str
    text_link: str
