import datetime
import uuid


def generate_cust_code(customer_id: str) -> str:
    """
    Generate a unique order code based on the customer ID and the current date.

    The code is composed of:
    - The first three characters of the customer ID
    - The current date in the format YYMMDD
    - A unique 8-character identifier

    Args:
        customer_id (str): The ID of the customer.

    Returns:
        str: The generated unique order code.
    """
    today = datetime.date.today()

    unique_id = str(uuid.uuid4())[:8]

    order_code = (
        f"{customer_id[:3]}-" f"{today.strftime('%y%m%d')}-{unique_id}"
    )

    return order_code
