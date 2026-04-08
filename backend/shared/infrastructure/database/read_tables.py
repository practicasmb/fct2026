from sqlalchemy import Column, Integer, MetaData, String, Table

# Read-only SQL table references used across modules to avoid direct
# imports between module entities at infrastructure query time.
READ_METADATA = MetaData()

clients_table = Table(
    "clients",
    READ_METADATA,
    Column("client_id", Integer, primary_key=True),
    Column("name", String),
)
