from starlette.config import Config as _Config

cfg = _Config(env_file=".env")


class Config:
    DB_USER = cfg("DATABASE_USER", default="postgres")
    DB_PASSWORD: str = cfg("DATABASE_PASSWORD", default="postgres")
    DB_HOST: str = cfg("DATABASE_HOST", default="localhost")
    DB_PORT: int = cfg("DATABASE_PORT", default=5432)
    DB_NAME: str = cfg("DATABASE_NAME", default="postgres")

    UPLOAD_DIR: str = cfg("UPLOAD_DIR", default="resources")
    MAX_UPLOAD_FILE_SIZE: int = 1024 * 1024

    UBL_INVOICE_SCHEMA = {
        "namespaces": {
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "ubl": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
        },
        "fields": {
            "invoice_number": ("cbc:ID", None),
            "issue_date": ("cbc:IssueDate", None),
            "supplier_id": ("cac:AccountingSupplierParty//cbc:EndpointID",
                            "cac:AccountingSupplierParty//cac:PartyIdentification//cbc:ID"),
            "customer_id": ("cac:AccountingCustomerParty//cbc:EndpointID",
                            "cac:AccountingCustomerParty//cac:PartyIdentification//cbc:ID"),
            "payable_amount": ("cac:LegalMonetaryTotal//cbc:PayableAmount", None),
        }
    }

    @property
    def DB_URL(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:"
            f"{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

config = Config()
