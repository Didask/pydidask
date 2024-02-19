from sqlalchemy import create_engine
from utils import load_config

CONFIG = load_config()["snowflake"]


def create_snowflake_engine(
    database,
    schema,
    user=CONFIG["username"],
    password=CONFIG["password"],
    account=CONFIG["account"],
    warehouse=CONFIG["warehouse"],
    role=CONFIG["role"],
):
    engine = create_engine(
        f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}"
    )
    return engine
