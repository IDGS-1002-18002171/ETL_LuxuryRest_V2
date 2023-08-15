import pandas as pd
import argparse
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Date
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
        if pipeline_name == 'Ventas':
            #Query the table and fetch all data
            productos_vendidos_por_dia = session.query(
                Productos.nombre,
                cast(Pedidos.fecha_hora_pedido, Date).label('fecha'),
                func.sum(Pedidos_Productos.cantidad).label('cantidad_vendida'),
                Productos.precio_venta  # Agregamos el precio de venta
            ).select_from(Pedidos).join(Pedidos_Productos).join(Productos).group_by(
                cast(Pedidos.fecha_hora_pedido, Date),
                Productos.nombre,
                Productos.precio_venta  # Agregamos el precio de venta a los campos de agrupación
            ).all()
            # Create a list of dictionaries from the query results, including total de venta
            data_list = [
                {
                    'producto': producto.nombre,
                    'fecha': producto.fecha,
                    'cantidad_vendida': producto.cantidad_vendida,
                    'precio_venta': producto.precio_venta,
                    'total_venta': producto.cantidad_vendida * producto.precio_venta  # Calculamos el total de venta
                }
                for producto in productos_vendidos_por_dia
            ]
        elif pipeline_name == 'Compras':
            # Query the table and fetch all data
            compras_por_dia = session.query(
                cast(Compras.fecha_compra, Date).label('fecha'),
                func.sum(Compras.cantidad_comprada * Materias_Primas.precio_compra).label('total_compras')
            ).join(Materias_Primas).group_by(cast(Compras.fecha_compra, Date)).all()
            # Create a list of dictionaries from the query results
            data_list = [{'fecha': compra.fecha, 'total_compras': compra.total_compras} for compra in compras_por_dia]
        elif pipeline_name=='Productos':
            # Query the table and fetch all data
            productos_en_stock = session.query(
                Productos.nombre,
                Productos.cantidad_disponible,
                Productos.valoracionC,
                Productos.valoracionT
            ).filter(Productos.estatus == 1).all()
            # Create a list of dictionaries from the query results, including total de venta
            data_list = [
                {
                    'producto': producto.nombre,
                    'cantidad_disponible': producto.cantidad_disponible,
                    'valoracion': producto.valoracionT/producto.valoracionC
                }
                for producto in productos_en_stock
            ]
        elif pipeline_name=='Materias_Primas':
            # Query the table and fetch all data
            materias_primas_en_inventario = session.query(
                Materias_Primas.nombre,
                Materias_Primas.unidad_medida,
                Materias_Primas.cantidad_minima_requerida,
                func.sum(Inventario.cantidad_almacenada).label('cantidad_en_inventario')
                ).join(Inventario).filter(Materias_Primas.Activo == 1).group_by(
                    Materias_Primas.nombre,
                    Materias_Primas.unidad_medida,
                    Materias_Primas.cantidad_minima_requerida
                ).all()
            # Create a list of dictionaries from the query results, including total de venta
            data_list = [
                {
                    'materia_prima': materia_prima.nombre,
                    'unidad_medida': materia_prima.unidad_medida,
                    'cantidad_minima_requerida': materia_prima.cantidad_minima_requerida,
                    'cantidad_en_inventario' : materia_prima.cantidad_en_inventario
                }
                for materia_prima in materias_primas_en_inventario
            ]
        elif pipeline_name=='Users':
            # Query the table and fetch all data
            top10_users = session.query(
                User.name,
                func.count(Ventas.id_venta).label('cantidad_ventas')
            ).join(Ventas, User.id == Ventas.id_usuario).filter(User.active == 1).group_by(User.name).order_by(func.count(Ventas.id_venta).desc()).limit(10).all()
            # Create a list of dictionaries from the query results, including total de venta
            data_list = [
                {
                    'usuario': user.name,
                    'cantidad_ventas': user.cantidad_ventas
                }
                for user in top10_users
            ]
        # Close the session
        session.close()
        # Create a DataFrame from the list of dictionaries
        df_table = pd.DataFrame(data_list)
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
