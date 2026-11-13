from pathlib import Path
from datetime import date

from pydantic import BaseModel

AZURE_FOUNDRY_ENDPOINT="https://groceries-agent-foundry.cognitiveservices.azure.com/"
GOOGLE_DRIVE_PATH = Path("/mnt/e/My Drive/groceries_data")

if not GOOGLE_DRIVE_PATH.exists():
    raise FileNotFoundError(f"Google Drive path {GOOGLE_DRIVE_PATH} does not exist. Please ensure that the Google Drive is mounted correctly.")

DATE_FORMAT = "YYYY-MM-DD"


class OrderData(BaseModel):
    order_number: str | None
    order_date: date | None
    total_price: float | None
    total_saved: float | None
    item_count: int | None

    def as_dict(self) -> dict:
        dict_ = {
            "order_number": self.order_number,
            "order_date": self.order_date.isoformat(),
            "total_price": self.total_price,
            "total_saved": self.total_saved,
            "item_count": self.item_count
        }
        return dict_


class ItemData(BaseModel):
    name: str
    brand: str | None
    price_per_unit: float | None
    price_total: float | None
    quantity: int | None
    group: str
    weight: float | None
    volume: float | None
    number_per_pack: int | None
    is_substitute: bool = False


class ExtractionResult(BaseModel):
    order: OrderData
    items: list[ItemData]


GROUPS = [
    "Vegetables",
    "Fruits",
    "Meat & Poultry",
    "Fish & Seafood",
    "Dairy & Eggs",
    "Bakery",
    "Soft & Alcoholic Beverages",
    "Food Cupboard",
    "Chocolate, biscuits & sweets",
    "Frozen Foods",
    "Toiletries",
    "Household",
    "Other"
]
