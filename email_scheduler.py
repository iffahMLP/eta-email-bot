from google_sheet_handler import GoogleSheetHandler
from email_handler import EmailHandler

sheet_handler = GoogleSheetHandler()
email_handler = EmailHandler()

def send_scheduled_emails():
    """Send emails for orders with missing 'First Email Sent?'."""
    orders = sheet_handler.get_orders_needing_emails()

    for order in orders:
        if email_handler.send_email(order["customer_email"], order["order_number"]):
            sheet_handler.mark_email_sent(order["row_index"])

if __name__ == "__main__":
    send_scheduled_emails()

