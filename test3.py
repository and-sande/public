import os
import httpx
import logging
import asyncio

def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

async def fetch_faktura_nr(order_number):
    """
    Fetch fakturaNr for the given order number.

    :param order_number: The sales order number to query.
    :return: The fakturaNr if found, otherwise an empty string.
    """
    # Load environment variables
    username = "robot-reskontro"
    password = "vinterIjanuar2019"
    ubw_api_url = os.getenv("UBW_API_URL", "https://prd-svc.ubw.unit.no/UBWHVL-web-api/v1")

    if not username or not password:
        logging.error("AGRESSO_USERNAME or AGRESSO_PASSWORD is not set in the environment.")
        return ""

    external_api_url = f"{ubw_api_url}/query/customer-transactions"

    params = {
        "companyId": "TF",
        "select": "invoiceNumber",
        "filter": f"orderNumber eq {order_number}",
        "unmatchedCustomerInvoices": "true"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(external_api_url, params=params, auth=(username, password))
            response.raise_for_status()
            external_data = response.json()

            # Check if data is a non-empty list
            if isinstance(external_data, list) and external_data:
                faktura_nr = external_data[0].get("invoiceNumber", "")
                logging.info(f"FakturaNr found: {faktura_nr}")
                return faktura_nr
            else:
                logging.warning("No fakturaNr found or unexpected response format.")
                return ""

    except httpx.RequestError as e:
        logging.error(f"HTTP Request failed: {e}")
        return ""

if __name__ == "__main__":
    configure_logging()

    # Input order number for testing
    order_number = input("Enter the sales order number: ").strip()

    if not order_number:
        logging.error("Order number is required.")
    else:
        faktura_nr = asyncio.run(fetch_faktura_nr(order_number))
        if faktura_nr:
            print(f"FakturaNr: {faktura_nr}")
        else:
            print("No fakturaNr found.")
