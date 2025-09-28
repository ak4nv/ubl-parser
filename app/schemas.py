import datetime as dt
from decimal import Decimal

from typing import Annotated
from pydantic import BaseModel, Field


class InvoiceCreate(BaseModel):
    id: int
    message: str = "Invoice saved successfully"


class InvoiceMetadata(BaseModel):
    invoice_number: str
    issue_date: dt.date
    customer_id: str
    supplier_id: str
    payable_amount: Annotated[Decimal, Field(decimal_places=2)]

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class InvoiceResponse(BaseModel):
    id: int
    created_at: dt.datetime
    metadata: InvoiceMetadata
