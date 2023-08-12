import pandas as pd
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from clases import Ventas, Pedidos_Productos, Pedidos, Productos, Compras, Materias_Primas, Inventario, User, Role, Merma, Proveedores, Receta, User_Roles

# Define the connection string
connection_string = 'mssql+pyodbc://LAPTOP-H1G95B7K\\2022@LAPTOP-H1G95B7K\\SQLEXPRESS/LuxuryRest?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'

# Function to get a session for the SQL Server database
def get_sql_server_session():
    engine = create_engine(connection_string)
    return sessionmaker(bind=engine)()

def export_user_table_to_csv(pipeline_name):
    try:
        # Create a session for database interaction
        session = get_sql_server_session()

        # Get the ORM class dynamically based on the pipeline name
        table_class = globals()[pipeline_name]

        # Query the table and fetch all data
        table_data = session.query(table_class).all()

        # Close the session
        session.close()

        # Create a DataFrame from the query results
        df_table = pd.DataFrame([item.__dict__ for item in table_data])

        # Export the DataFrame to a CSV file
        csv_file_name = f'{pipeline_name}.csv'
        df_table.to_csv(csv_file_name, index=False, encoding='utf-8')

        print(f"Data from '{pipeline_name}' table exported to '{csv_file_name}' successfully.")
    except Exception as e:
        print(f"Error exporting '{pipeline_name}' table data: {str(e)}")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('news_site', help='Name of the pipeline you want to process', type=str)
    args = parser.parse_args()

    pipeline_name = args.news_site
    export_user_table_to_csv(pipeline_name)
