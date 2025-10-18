from sqlalchemy import Table, Column, Integer, String
from database import meta, engine

Clothes = Table(
    'clothes', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(100)),
    Column('brand', String(100)),
    Column('price', Integer),
    Column('size', String(10))
)

meta.create_all(engine)
