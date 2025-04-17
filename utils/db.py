# utils/db.py
import os
import json
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()
metadata = MetaData()

def get_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db = os.getenv("DB_NAME")

    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)
def create_tables_from_schema(schema_json):
    engine = get_engine()
    metadata.bind = engine
    tables = {}
    
    # Track columns that we already defined
    # Instead of tracking column names, track column dictionaries
    defined_columns = {}
    for table in schema_json.get("tables", []):
        table_name = table["name"]
        defined_columns[table_name] = set()
        for column in table["columns"]:
            # Extract column name from the column dict
            if isinstance(column, dict):
                defined_columns[table_name].add(column["name"])
            else:
                defined_columns[table_name].add(column)
    
    # Step 1: Create tables with all columns including FKs
    for table in schema_json.get("tables", []):
        name = table["name"]
        columns = []
        
        for col in table["columns"]:
            # Handle either string columns or dictionary columns
            if isinstance(col, dict):
                col_name = col["name"]
                col_type = col.get("type", "string").lower()
                
                # Handle primary key
                if col_name == "id":
                    columns.append(Column(col_name, Integer, primary_key=True))
                # Handle foreign key
                elif "foreign_key" in col:
                    fk_reference = col["foreign_key"]
                    # Extract table and column names from the foreign key reference
                    # Format is typically "table_name(column_name)"
                    fk_table = fk_reference.split('(')[0]
                    columns.append(Column(col_name, Integer, ForeignKey(fk_reference)))
                # Handle other columns based on type
                else:
                    if col_type == "integer":
                        columns.append(Column(col_name, Integer))
                    else:  # Default to String for all other types
                        columns.append(Column(col_name, String))
            else:
                # If column is just a string (old format)
                if col == "id":
                    columns.append(Column(col, Integer, primary_key=True))
                else:
                    columns.append(Column(col, String))
        
        tables[name] = Table(name, metadata, *columns)
    
    # We no longer need to process relationships separately as they're already included
    # in the column definitions
    
    # Create all tables at once
    metadata.create_all(engine)
    print("✅ Tables created successfully.")