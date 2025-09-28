from typing import Annotated

import datetime as dt
from decimal import Decimal

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)


class Base(DeclarativeBase):
    pass


pk_int = Annotated[int, mapped_column(primary_key=True)]
timestamp = Annotated[
    dt.datetime,
    mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP()),
]


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[pk_int]
    filepath: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[timestamp]
    data: Mapped["InvoiceMetadata"] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Invoice(id={self.id!r})"


class InvoiceMetadata(Base):
    __tablename__ = "invoice_metadatas"

    id: Mapped[pk_int]
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    invoice: Mapped["Invoice"] = relationship(back_populates="data")

    invoice_number: Mapped[str]
    issue_date: Mapped[dt.date]
    customer_id: Mapped[str]
    supplier_id: Mapped[str]
    payable_amount: Mapped[Decimal]

    def __repr__(self) -> str:
        return f"InvoiceMetadata(id={self.id!r})"
