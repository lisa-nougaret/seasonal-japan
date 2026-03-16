import os
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def get_engine():
    if "database" in st.secrets:
        db = st.secrets["database"]
        connection_string = (
            f"postgresql+psycopg://{db['user']}:{db['password']}"
            f"@{db['host']}:{db['port']}/{db['database']}"
            f"?sslmode=require"
        )
    else:
        db_user = os.getenv("DB_USER", "").strip()
        db_password = os.getenv("DB_PASSWORD", "").strip()
        db_host = os.getenv("DB_HOST", "").strip()
        db_port = os.getenv("DB_PORT", "").strip()
        db_name = os.getenv("DB_NAME", "").strip()

        connection_string = (
            f"postgresql+psycopg://{db_user}:{db_password}"
            f"@{db_host}:{db_port}/{db_name}"
        )

    return create_engine(connection_string)