from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#Declaramos el motor de base de datos a usar.
engine=create_engine('sqlite:///load/LuxuryRestETL.db')

Session=sessionmaker(bind=engine)

Base=declarative_base()
