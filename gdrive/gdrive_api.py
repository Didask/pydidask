import sys

sys.path.append("..")
from pathlib import Path
from typing import Optional

import gspread
import pandas as pd
from dev.utils import load_config
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

GDRIVE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
DEFAULT_FOLDER_ID = "12uz-Jmi9FEk-V5_7bZ63q41Ytg1IatUX"  # EQUIPE_DATA_TO_MIGRATE


class GDrive:

    def __init__(self):
        self.service_account_file = Path(
            load_config()["gdrive"]["service_account_key_path"]
        ).expanduser()
        self.credentials = Credentials.from_service_account_file(
            self.service_account_file, scopes=GDRIVE_SCOPES
        )
        self.gdrive_service = build("drive", "v3", credentials=self.credentials)
        self.gsheet_service = build("sheets", "v4", credentials=self.credentials)

        # gspread
        gspread_creds = ServiceAccountCredentials.from_json_keyfile_name(
            self.service_account_file, GDRIVE_SCOPES
        )
        self.gspread_client = gspread.authorize(gspread_creds)

    def ls(self, folder_id: str = DEFAULT_FOLDER_ID):
        results = (
            self.gdrive_service.files()
            .list(
                q=f"'{folder_id}' in parents",
                pageSize=100,
                fields="nextPageToken, files(id, name)",
            )
            .execute()
        )
        items = results.get("files", [])
        return items

    def create_gsheet(self, title: str, folder_id: str = DEFAULT_FOLDER_ID) -> str:
        """Returns the ID of the google sheet created"""

        sheet_metadata = {"properties": {"title": title}}
        sheet = (
            self.gsheet_service.spreadsheets()
            .create(body=sheet_metadata, fields="spreadsheetId")
            .execute()
        )
        sheet_id = sheet.get("spreadsheetId")

        # Move the new Google Sheet to the specified folder
        file_metadata = {"addParents": folder_id, "removeParents": "root"}
        self.gdrive_service.files().update(
            fileId=sheet_id,
            addParents=folder_id,
            removeParents="root",
            fields="id, parents",
        ).execute()
        return sheet_id

    def load_gsheet(self, gsheet_id: str, worksheet_num: int = 0):

        worksheet = self.gspread_client.open_by_key(gsheet_id).get_worksheet(
            worksheet_num
        )

        # Get all the records of the data
        records = worksheet.get_all_records()

        # Convert to a DataFrame
        df = pd.DataFrame.from_records(records)

        return df

    def get_worksheets(self, gsheet_id: str):
        gsheet = self.gspread_client.open_by_key(gsheet_id)
        return gsheet.worksheets()

    def dump_df_in_gsheet(self, df: pd.DataFrame, gsheet_id: str, worksheet_num: int):

        gsheet = self.gspread_client.open_by_key(gsheet_id)
        worksheet = gsheet.get_worksheet(worksheet_num)
        set_with_dataframe(worksheet, df)
