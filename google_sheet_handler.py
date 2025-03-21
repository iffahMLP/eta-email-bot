import gspread
import os
import json
import base64
import sqlite3
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

class GoogleSheetHandler:
    def __init__(self, sheet_name="MLP ETA Sheet", tab_name="Orders UK"):
        self.sheet_name = sheet_name
        self.tab_name = tab_name
        self.credentials = self._load_credentials()
        self.gc = gspread.authorize(self.credentials)
        self.sheet = self.gc.open(sheet_name)
        self.worksheet = self.sheet.worksheet(tab_name)

    def _load_credentials(self):
        json_b64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not json_b64:
            raise ValueError("Missing GOOGLE_SERVICE_ACCOUNT_JSON")
        
        creds_dict = json.loads(base64.b64decode(json_b64))
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        return Credentials.from_service_account_info(creds_dict, scopes=scopes)

    def order_exists_in_sheet(self, order_number):
        """Check if an order already exists in Google Sheets."""
        data = self.worksheet.get_all_records()
        return any(row["Order Number"] == order_number for row in data)

    def write_order(self, order_data):
        """Append order to Google Sheets if it doesn’t already exist."""
        order_number = order_data["order_number"]
        if not self.order_exists_in_sheet(order_number):
            row = [
                order_data["order_number"],
                order_data["customer_name"],
                order_data["customer_email"],
                order_data["order_created"],
                order_data["order_country"]
            ]
            self.worksheet.append_row(row)
            print(f"✅ Order {order_number} written to Google Sheets.")
            return True
        else:
            print(f"⚠️ Order {order_number} already exists in Google Sheets. Skipping.")
            return False
