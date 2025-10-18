from sqlalchemy import create_engine, MetaData

# Create an SQLite database
engine = create_engine("sqlite:///clothes.db", echo=True)
meta = MetaData()
conn = engine.connect()
