import logging
import pathlib

from collections import namedtuple

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse

from sqlalchemy import select

import schemas as s

from database import init_db, session
from models import Invoice, InvoiceMetadata
from config import config
from parser import UBLInvoiceParser


app = FastAPI()
logger = logging.getLogger(__name__)
ubl_parser = UBLInvoiceParser(
    config.UBL_INVOICE_SCHEMA["namespaces"],
    config.UBL_INVOICE_SCHEMA["fields"]
)
Metadata = namedtuple(
    "Metadata",
    "invoice_number,issue_date,supplier_id,customer_id,payable_amount"
)


@app.on_event("startup")
async def startup_event():
    await init_db()
    upload = pathlib.Path(config.UPLOAD_DIR)
    upload.mkdir(exist_ok=True)


@app.post(
    "/invoices",
    response_model=s.InvoiceCreate,
    status_code=201,
    tags=["Invoices"]
)
async def create_invoice(file: UploadFile, session: session):
    data = bytearray()
    while chunk := await file.read(1024):
        data.extend(chunk)
        if len(data) > config.MAX_UPLOAD_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too big")

    try:
        metadata = ubl_parser.parse(bytes(data))
    except Exception:
        logger.exception("Failed parsing xml", exc_info=True)
        metadata = None
    if not metadata:
        raise HTTPException(status_code=400, detail="Error parsing file")

    filename = "_".join([
        metadata[x] for x in ("customer_id", "supplier_id", "invoice_number")
    ]).lower()
    filepath = f"{config.UPLOAD_DIR}/{filename}.xml"
    with open(filepath, "wb") as f:
        f.write(data)

    try:
        metadata = s.InvoiceMetadata(**metadata)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    invoice = Invoice(filepath=filepath)
    invoice_metadata = InvoiceMetadata(**metadata.model_dump())

    async with session.begin_nested():
        try:
            session.add(invoice)
            await session.flush()
            invoice_metadata.invoice_id =invoice.id
            session.add(invoice_metadata)
            await session.commit()
        except Exception:
            await session.rollback()

    return invoice


@app.get(
    "/invoices",
    response_model=list[s.InvoiceResponse],
    tags=["Invoices"]
)
async def list_invoices(session: session, limit: int = 100):
    q = select(
        Invoice.id,
        Invoice.created_at,
        *[getattr(InvoiceMetadata, x) for x in Metadata._fields]
    ).join(Invoice.data).limit(limit)

    result = await session.execute(q)
    resp = [{
        "id": id_,
        "created_at": created_at,
        "metadata": Metadata(*metadata)._asdict()
    } for id_, created_at, *metadata in result.fetchall()]
    return resp


@app.get("/invoices/{invoice_id}/xml", tags=["Invoices"])
async def get_invoice_xml(invoice_id: int, session: session):
    result = await session.execute(
        select(Invoice.filepath).where(Invoice.id == invoice_id)
    )
    invoice = result.first()

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice with ID {invoice_id} not found."
        )

    return FileResponse(
        path=invoice.filepath,
        filename=pathlib.Path(invoice.filepath).name,
        media_type="application/xml"
    )
