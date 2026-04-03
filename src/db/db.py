import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import streamlit as st

load_dotenv()

def get_engine():
    if "database" in st.secrets:
        db = st.secrets["database"]
        connection_string = (
            f"postgresql+psycopg://{db['user']}:{db['password']}"
            f"@{db['host']}:{db['port']}/{db['database']}?sslmode=require"
        )
    else:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")

        connection_string = (
            f"postgresql+psycopg://{db_user}:{db_password}"
            f"@{db_host}:{db_port}/{db_name}?sslmode=require"
        )

    return create_engine(connection_string, pool_pre_ping=True)