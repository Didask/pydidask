from pathlib import Path

import gspread
import pandas as pd
import snowflake.connector
from oauth2client.service_account import ServiceAccountCredentials
from snowflake.connector.pandas_tools import write_pandas
from utils import load_config

PATH_GSHEET_CREDS = Path("/Users/selimrbd/.gsheet/mock-data-412317-cd4e142a8ff3.json")

# Set up the credentials
scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = ServiceAccountCredentials.from_json_keyfile_name(PATH_GSHEET_CREDS, scope)
client = gspread.authorize(creds)

# Google Sheets config
sheet_url = "https://docs.google.com/spreadsheets/d/1OEe9yHiqlQXbCzP6JA7HkBOdBOpuw6RtNHmyqRF4lUI/edit#gid=808477594"
spreadsheet_id = sheet_url.split("/d/")[1].split("/")[0]
spreadsheet = client.open_by_key(spreadsheet_id)


cfg = load_config()["snowflake"]

# Snowflake config
DATABASE = "RAW"
SCHEMA = "MOCK"


def load_mock_data():
    snow_ctx = snowflake.connector.connect(
        user=cfg["username"],
        password=cfg["password"],
        account=cfg["account"],
        warehouse=cfg["warehouse"],
        database=DATABASE,
        schema=SCHEMA,
    )

    for sheet in spreadsheet.worksheets():
        # Read data into a pandas DataFrame
        data = sheet.get_all_values()
        df = pd.DataFrame(data)
        df.columns = df.iloc[0]  # Set the first row as column headers
        df = df.drop(0).reset_index(drop=True)

        # Convert column names to uppercase to align with Snowflake's default behavior
        df.columns = [column.upper() for column in df.columns]

        # attempt to convert column to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # Define the Snowflake table name
        table_name = f"{sheet.title}"

        # Load DataFrame into Snowflake
        write_pandas(
            snow_ctx, df, table_name.upper(), auto_create_table=True, overwrite=True
        )

    # Close Snowflake connection
    snow_ctx.close()


if __name__ == "__main__":
    load_mock_data()
