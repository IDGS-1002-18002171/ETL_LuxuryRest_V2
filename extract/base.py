from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#Declaramos el motor de base de datos a usar.
engine = create_engine('mssql+pyodbc://LAPTOP-H1G95B7K/2022@LAPTOP-H1G95B7K/SQLEXPRESS/LuxuryRest?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
#Declaramos el motor de base de datos a usar.
#engine=create_engine('sqlite:///load/LuxuryRestETL.db')
Session=sessionmaker(bind=engine)

Base=declarative_base()
