from lxml import etree


class UBLInvoiceParser:

    def __init__(self, namespaces: list, fields: dict) -> None:
        self.namespaces =namespaces
        self.fields = fields

    def _get_element(
        self,
        root: etree._Element,
        xpath: str,
        xpath_fallback: str
    ) -> str | None:
        element = root.find(xpath, self.namespaces)
        if element is None and xpath_fallback:
            element = root.find(xpath_fallback, self.namespaces)
        return element.text if element is not None else None

    def parse(self, raw: bytes) -> dict:
        root = etree.fromstring(raw)
        invoice_data = {
            field: self._get_element(root, *pathes)
            for field, pathes in self.fields.items()
        }
        return invoice_data
