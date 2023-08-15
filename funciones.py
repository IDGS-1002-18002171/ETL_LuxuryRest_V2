import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from flask import Flask, render_template, jsonify, request, Response
from clases import Users, Ventas, Compras, Productos, Materias_Primas
from datetime import datetime, timedelta, date
import json
import warnings
from sqlalchemy.exc import SAWarning
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, aliased
from sqlalchemy import text, func, create_engine
import threading
import logging
from decimal import Decimal
import dash_table
import dash.html as html

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
# Función para obtener una sesión para la base de datos SQLite
def get_sqlite_session():
    engine = create_engine('sqlite:///load/LuxuryRestETL.db')
    return sessionmaker(bind=engine)()

# Función para obtener una sesión para la base de datos SQL Server
def get_sql_server_session():
    connection_string = 'mssql+pyodbc://LAPTOP-H1G95B7K\\2022@LAPTOP-H1G95B7K\\SQLEXPRESS/LuxuryRest?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    engine1 = create_engine(connection_string)
    return sessionmaker(bind=engine1)()
# Función para obtener las ganancias por un período personalizado
def obtener_ganancias_por_periodo_personalizado(start_date, end_date):
    try:
        # Convertir las fechas de inicio y fin a objetos datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        # Crear una lista para almacenar los resultados por día
        results = []
        # Crear una sesión para interactuar con la base de datos
        session = get_sqlite_session()
        # Obtener las fechas y ganancias por día dentro del período seleccionado
        current_date = start_date
        while current_date <= end_date:
            current_date_date = current_date.date()
            # Consulta para obtener las ganancias del día actual
            ganancias_periodo = session.query(func.sum(Ventas.total_venta)).filter(
                Ventas.fecha >= current_date_date,
                Ventas.fecha < current_date_date + timedelta(days=1)
            ).scalar()
            # Handle the result based on its type
            if ganancias_periodo is not None:
                if isinstance(ganancias_periodo, Decimal):
                    total_ganancias = float(ganancias_periodo)  # Convert decimal to float
                else:
                    total_ganancias = ganancias_periodo
            else:
                total_ganancias = 0
            # Agregar los resultados a la lista
            results.append({
                'Día': current_date_date,
                'Ganancias': total_ganancias 
            })
            # Moverse al siguiente día
            current_date += timedelta(days=1)
        # Cerrar la sesión
        session.close()
        # Crear un DataFrame para mostrar el resultado
        df_ganancias = pd.DataFrame(results)
        return df_ganancias
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de ventas: {str(e)}")
        return []

# Función para obtener las ganancias por un período personalizado usando SQL Server
def obtener_ganancias_por_periodo_personalizado1(start_date, end_date):
    try:
        # Convertir las fechas de inicio y fin a objetos datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        # Crear una lista para almacenar los resultados por día
        results = []
        # Crear una sesión para interactuar con la base de datos
        session1 = get_sql_server_session()
        # Consulta para obtener las fechas y ganancias por día dentro del período seleccionado
        current_date = start_date
        while current_date <= end_date:
            # Consulta para obtener las ganancias del día actual usando el motor de base de datos y la sesión
            query = text("SELECT SUM(precio_total) FROM ventas WHERE fecha_hora_venta >= :current_date AND fecha_hora_venta < :next_date")
            ganancias_periodo = session1.execute(query, {"current_date": current_date, "next_date": current_date + timedelta(days=1)}).scalar()

            # Agregar los resultados a la lista
            results.append({
                'Día': current_date.strftime('%Y-%m-%d'),
                'Ganancias': ganancias_periodo or 0
            })
            # Moverse al siguiente día
            current_date += timedelta(days=1)
        # Cerrar la sesión
        session1.close()
        # Crear un DataFrame para mostrar el resultado
        df_ganancias = pd.DataFrame(results)
        return df_ganancias
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de ventas: {str(e)}")
        return []

# Función para obtener el gasto total en compras por un período personalizado
def obtener_compras_por_periodo_personalizado(start_date, end_date):
    try:
        # Convertir las fechas de inicio y fin a objetos datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        # Crear una lista para almacenar los resultados por día
        results = []
        # Crear una sesión para interactuar con la base de datos
        session = get_sqlite_session()
        # Obtener las fechas y gasto total en compras por día dentro del período seleccionado
        current_date = start_date
        while current_date < end_date:
            current_date_date = current_date.date()
            # Consulta para obtener el gasto total en compras del día actual
            gasto_total_compras_periodo = session.query(func.sum(Compras.total_compras)).filter(
                Compras.fecha >= current_date_date,
                Compras.fecha < current_date_date + timedelta(days=1)
            ).scalar()
            # Handle the result based on its type
            if gasto_total_compras_periodo is not None:
                if isinstance(gasto_total_compras_periodo, Decimal):
                    total_compras = float(gasto_total_compras_periodo)  # Convert decimal to float
                else:
                    total_compras = gasto_total_compras_periodo
            else:
                total_compras = 0
            # Agregar los resultados a la lista
            results.append({
                'Día': current_date_date,
                'Compras': total_compras
            })
            # Moverse al siguiente día
            current_date += timedelta(days=1)
        # Cerrar la sesión
        session.close()
        # Crear un DataFrame para mostrar el resultado
        df_gasto_total_compras = pd.DataFrame(results)
        return df_gasto_total_compras
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de compras: {str(e)}")
        return []

# Función para obtener el gasto total en compras por un período personalizado
def obtener_compras_por_periodo_personalizado1(start_date, end_date):
    try:
        # Convertir las fechas de inicio y fin a objetos datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        # Crear una lista para almacenar los resultados por día
        results = []
        # Crear una sesión para interactuar con la base de datos
        session1 = get_sql_server_session()
        # Obtener las fechas y gasto total en compras por día dentro del período seleccionado
        current_date = start_date
        while current_date < end_date:
            # Calcular el día siguiente al día actual
            next_date = current_date + timedelta(days=1)
            # Consulta para obtener el gasto total en compras del día actual
            gasto_total_compras_periodo = session1.query(func.sum(Compras.cantidad_comprada * Materias_Primas.precio_compra)).join(Materias_Primas).filter(
                Compras.fecha_compra >= current_date,
                Compras.fecha_compra < next_date
            ).scalar()
            # Agregar los resultados a la lista
            results.append({
                'Día': current_date.strftime('%Y-%m-%d'),
                'Compras': gasto_total_compras_periodo or 0
            })
            # Moverse al siguiente día
            current_date = next_date
        # Cerrar la sesión
        session1.close()
        # Crear un DataFrame para mostrar el resultado
        df_gasto_total_compras = pd.DataFrame(results)
        return df_gasto_total_compras
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de compras: {str(e)}")
        return []

# Función para obtener las ganancias por un rango de meses
def obtener_ganancias_por_mes(start_year, start_month, end_year, end_month):
    try:
        # Convertir los valores de año y mes a objetos datetime
        start_date = datetime(start_year, start_month, 1)
        end_date = datetime(end_year, end_month, 1) + pd.offsets.MonthEnd(0)
        # Crear una lista para almacenar los resultados por mes
        results = []
        # Crear una sesión para interactuar con la base de datos
        session = get_sqlite_session()
        # Obtener las fechas y ganancias por mes dentro del rango seleccionado
        current_date = start_date
        while current_date <= end_date:
            # Calcular el primer día del mes actual
            first_day_of_month = current_date.replace(day=1)
            # Calcular el último día del mes actual
            last_day_of_month = first_day_of_month + pd.offsets.MonthEnd(0)
            # Consulta para obtener las ganancias del mes actual
            ganancias_mes = session.query(func.sum(Ventas.total_venta)).filter(
                Ventas.fecha >= first_day_of_month,
                Ventas.fecha <= last_day_of_month
            ).scalar()
            # Agregar los resultados a la lista
            results.append({
                'Mes': current_date.strftime('%Y-%m'),
                'Ganancias': ganancias_mes or 0
            })
            # Moverse al siguiente mes
            current_date = last_day_of_month + timedelta(days=1)
        # Cerrar la sesión
        session.close()
        # Crear un DataFrame para mostrar el resultado
        df_ganancias = pd.DataFrame(results)
        return df_ganancias
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de ventas: {str(e)}")
        return []

# Función para obtener las ganancias por un rango de meses
def obtener_ganancias_por_mes1(start_year, start_month, end_year, end_month):
    try:
        # Convertir los valores de año y mes a objetos datetime
        start_date = datetime(start_year, start_month, 1)
        end_date = datetime(end_year, end_month, 1) + pd.offsets.MonthEnd(0)
        # Crear una lista para almacenar los resultados por mes
        results = []
        # Crear una sesión para interactuar con la base de datos
        session1 = get_sql_server_session()
        # Obtener las fechas y ganancias por mes dentro del rango seleccionado
        current_date = start_date
        while current_date <= end_date:
            # Calcular el primer día del mes actual
            first_day_of_month = current_date.replace(day=1)
            # Calcular el último día del mes actual
            last_day_of_month = first_day_of_month + pd.offsets.MonthEnd(0)
            # Consulta para obtener las ganancias del mes actual
            ganancias_mes = session1.query(func.sum(Ventas.precio_total)).filter(
                Ventas.fecha_hora_venta >= first_day_of_month,
                Ventas.fecha_hora_venta <= last_day_of_month
            ).scalar()
            # Agregar los resultados a la lista
            results.append({
                'Mes': current_date.strftime('%Y-%m'),
                'Ganancias': ganancias_mes or 0
            })
            # Moverse al siguiente mes
            current_date = last_day_of_month + timedelta(days=1)
        # Cerrar la sesión
        session1.close()
        # Crear un DataFrame para mostrar el resultado
        df_ganancias = pd.DataFrame(results)
        return df_ganancias
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de ventas: {str(e)}")
        return []

# Función para obtener el gasto en compras por un rango de meses
def obtener_compras_por_mes(start_year, start_month, end_year, end_month):
    try:
        # Convertir los valores de año y mes a objetos datetime
        start_date = datetime(start_year, start_month, 1)
        end_date = datetime(end_year, end_month, 1) + pd.offsets.MonthEnd(0)
        # Crear una lista para almacenar los resultados por mes
        results = []
        # Crear una sesión para interactuar con la base de datos
        session = get_sqlite_session()
        # Obtener el gasto en compras por mes dentro del rango seleccionado
        current_date = start_date
        while current_date <= end_date:
            # Calcular el primer día del mes actual
            first_day_of_month = current_date.replace(day=1)
            # Calcular el último día del mes actual
            last_day_of_month = first_day_of_month + pd.offsets.MonthEnd(0)
            # Consulta para obtener el gasto en compras del mes actual
            gasto_compras_mes = session.query(func.sum(Compras.total_compras)).filter(
                Compras.fecha >= first_day_of_month,
                Compras.fecha <= last_day_of_month
            ).scalar()
            # Agregar los resultados a la lista
            results.append({
                'Mes': current_date.strftime('%Y-%m'),
                'Compras': gasto_compras_mes or 0
            })
            # Moverse al siguiente mes
            current_date = last_day_of_month + timedelta(days=1)
        # Cerrar la sesión
        session.close()
        # Crear un DataFrame para mostrar el resultado
        df_gasto_compras = pd.DataFrame(results)
        return df_gasto_compras
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de compras: {str(e)}")
        return []

# Función para obtener el gasto en compras por un rango de meses
def obtener_compras_por_mes1(start_year, start_month, end_year, end_month):
    try:
        # Convertir los valores de año y mes a objetos datetime
        start_date = datetime(start_year, start_month, 1)
        end_date = datetime(end_year, end_month, 1) + pd.offsets.MonthEnd(0)
        # Crear una lista para almacenar los resultados por mes
        results = []
        # Crear una sesión para interactuar con la base de datos
        session1 = get_sql_server_session()
        # Obtener el gasto en compras por mes dentro del rango seleccionado
        current_date = start_date
        while current_date <= end_date:
            # Calcular el primer día del mes actual
            first_day_of_month = current_date.replace(day=1)
            # Calcular el último día del mes actual
            last_day_of_month = first_day_of_month + pd.offsets.MonthEnd(0)
            # Consulta para obtener el gasto en compras del mes actual
            gasto_compras_mes = session1.query(func.sum(Materias_Primas.precio_compra)).filter(
                Compras.fecha_compra >= first_day_of_month,
                Compras.fecha_compra <= last_day_of_month
            ).scalar()
            # Agregar los resultados a la lista
            results.append({
                'Mes': current_date.strftime('%Y-%m'),
                'Compras': gasto_compras_mes or 0
            })
            # Moverse al siguiente mes
            current_date = last_day_of_month + timedelta(days=1)
        # Cerrar la sesión
        session1.close()
        # Crear un DataFrame para mostrar el resultado
        df_gasto_compras = pd.DataFrame(results)
        return df_gasto_compras
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de compras: {str(e)}")
        return []

def obtener_productos_mas_vendidos_pasteles(start_date, end_date):
    try:
        # Convert the start_date and end_date to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        start_date_date = start_date.date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Add 1 day to include the end date
        end_date_date = end_date.date()
        # Create a session to interact with the database
        session = get_sqlite_session()
        # Query to get sales for each product and sum the quantities sold
        ventas_productos = session.query(Ventas.producto, Ventas.precio_venta,func.sum(Ventas.cantidad_vendida),func.sum(Ventas.total_venta)).\
            filter(Ventas.fecha >= start_date_date, Ventas.fecha < end_date_date).\
            group_by(Ventas.producto, Ventas.precio_venta).\
            order_by(Ventas.cantidad_vendida.desc()).\
            all()
        # Close the session
        session.close()
        # Check if the list is empty before accessing its elements
        if not ventas_productos:
            # Return an empty list if there are no sales data
            results = [{'Nombre': 'none','Precio_venta': 0.0,'Cantidad': 0,'Total_venta': 0.0 }]
            productos_mas_vendidos = pd.DataFrame(results)
            return productos_mas_vendidos
        # Create a list of tuples (product name, quantity sold) for the pie chart
        results = [{'Nombre': nombre,'Precio_venta': precio_venta,'Cantidad': cantidad,'Total_venta': total_venta } for nombre,precio_venta, cantidad, total_venta in ventas_productos]
        # Creamos un DataFrame para mostrar los resultados
        productos_mas_vendidos = pd.DataFrame(results)
        return productos_mas_vendidos
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de productos: {str(e)}")
        results = [{'Nombre': 'none','Precio_venta': 0.0,'Cantidad': 0,'Total_venta': 0.0 }]
        productos_mas_vendidos = pd.DataFrame(results)
        return productos_mas_vendidos

def obtener_productos_mas_vendidos_pasteles1(start_date, end_date):
    try:
        # Convert the start_date and end_date to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Add 1 day to include the end date
        # Create a session to interact with the database
        session1 = get_sql_server_session()
        # Query to get sales for each product and sum the quantities sold
        ventas_productos = session1.query(Productos.nombre, Productos.precio_venta, func.sum(Pedidos_Productos.cantidad)).\
            join(Pedidos_Productos, Productos.id_producto == Pedidos_Productos.id_producto).\
            join(Pedidos, Pedidos_Productos.id_pedido == Pedidos.id_pedido).\
            filter(Pedidos.fecha_hora_pedido >= start_date, Pedidos.fecha_hora_pedido < end_date,Productos.estatus == 1).\
            group_by(Productos.nombre).\
            order_by(func.sum(Pedidos_Productos.cantidad).desc()).\
            all()
        # Close the session
        session1.close()
        # Check if the list is empty before accessing its elements
        if not ventas_productos:
            # Return an empty list if there are no sales data
            return [], []
        # Create a list of tuples (product name, quantity sold) for the pie chart
        productos_mas_vendidos = [(nombre,precio_venta, cantidad) for nombre,precio_venta, cantidad in ventas_productos]
        return productos_mas_vendidos
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de productos: {str(e)}")
        return []

def obtener_productos_valoracion_actual():
    try:
        # Crear una lista para almacenar los resultados
        results = []
        # Crear una sesión para interactuar con la base de datos
        session = get_sqlite_session()
        # Consulta para obtener los productos y su valoración actual
        productos_valoracion = session.query(Productos.producto, Productos.valoracion).all()
        # Cerrar la sesión
        session.close()
        # Verificar si la lista está vacía antes de acceder a sus elementos
        if not productos_valoracion:
            # Retornar una lista vacía si no hay datos de productos
            return []
        # Calcular la valoración actual y agregar los resultados a la lista
        for producto, valoracion in productos_valoracion:
            
            results.append({
                'Nombre': producto,
                'Valoracion Actual': valoracion
            })
        # Crear un DataFrame para mostrar el resultado
        df_valoracion_actual = pd.DataFrame(results)
        return df_valoracion_actual
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la valoracion de productos: {str(e)}")
        return []

def obtener_productos_valoracion_actual1():
    try:
        # Crear una lista para almacenar los resultados
        results = []
        # Crear una sesión para interactuar con la base de datos
        session1 = get_sql_server_session()
        # Consulta para obtener los productos y su valoración actual
        productos_valoracion = session1.query(Productos.nombre, Productos.valoracionT, Productos.valoracionC).\
        filter(Productos.estatus == 1).\
        all()
        # Cerrar la sesión
        session1.close()
        # Verificar si la lista está vacía antes de acceder a sus elementos
        if not productos_valoracion:
            # Retornar una lista vacía si no hay datos de productos
            return []
        # Calcular la valoración actual y agregar los resultados a la lista
        for nombre, valoracionT, valoracionC in productos_valoracion:
            valoracion_actual = valoracionT / valoracionC if valoracionC != 0 else 0
            results.append({
                'Nombre': nombre,
                'Valoracion Actual': valoracion_actual
            })
        # Crear un DataFrame para mostrar el resultado
        df_valoracion_actual = pd.DataFrame(results)
        return df_valoracion_actual
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la valoracion de productos: {str(e)}")
        return []

def obtener_productos_y_stock_actual():
    try:
        # Create a session to interact with the database
        session = get_sqlite_session()
        # Query to get product names and their current stock quantities
        productos_stock_actual = session.query(Productos.producto, Productos.cantidad_disponible).all()
        # Close the session
        session.close()
        # Check if the list is empty before accessing its elements
        if not productos_stock_actual:
            # Return an empty list if there are no products or stock data
            return []
        # Create a list of dictionaries containing product name and current stock quantity
        results = [{'Nombre': producto, 'Stock Actual': cantidad_disponible} for producto, cantidad_disponible in productos_stock_actual]
        # Crear un DataFrame para mostrar el resultado
        df_stock = pd.DataFrame(results)
        return df_stock
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de productos: {str(e)}")
        return []

def obtener_productos_y_stock_actual1():
    try:
        # Create a session to interact with the database
        session1 = get_sql_server_session()
        # Query to get product names and their current stock quantities
        productos_stock_actual = session1.query(Productos.nombre, Productos.cantidad_disponible).\
            filter(Productos.estatus == 1).\
                all()
        # Close the session
        session1.close()
        # Check if the list is empty before accessing its elements
        if not productos_stock_actual:
            # Return an empty list if there are no products or stock data
            return []
        # Create a list of dictionaries containing product name and current stock quantity
        results = [{'Nombre': nombre, 'Stock Actual': stock} for nombre, stock in productos_stock_actual]
        # Crear un DataFrame para mostrar el resultado
        df_stock = pd.DataFrame(results)
        return df_stock
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de productos: {str(e)}")
        return []

def obtener_cantidad_materia_prima_actual():
    try:
        session = get_sqlite_session()
        # Consulta para obtener la cantidad actual de materia prima almacenada en el inventario
        materias_primas_inventario = session.query(
            Materias_Primas.materia_prima, Materias_Primas.cantidad_en_inventario, 
            Materias_Primas.unidad_medida, Materias_Primas.cantidad_minima_requerida).all()
        # Cerramos la sesión
        session.close()
        # Verificamos si la lista está vacía antes de acceder a sus elementos
        if not materias_primas_inventario:
            # Devolvemos una lista vacía si no hay datos en el inventario
            return []
        # Creamos una lista de diccionarios que contiene el nombre de la materia prima y su cantidad almacenada
        results = [{'Materia Prima': nom, 'Cantidad Almacenada': cant, 'Unidad Medida': uni, 'Cantidad Minima': mini} for nom, cant, uni, mini in materias_primas_inventario]
        # Creamos un DataFrame para mostrar los resultados
        df_materia_prima = pd.DataFrame(results)
        return df_materia_prima
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de materia prima: {str(e)}")
        return []

def obtener_cantidad_materia_prima_actual1():
    try:
        session1 = get_sql_server_session()
        # Consulta para obtener la cantidad actual de materia prima almacenada en el inventario
        materias_primas_inventario = session1.query(Materias_Primas.nombre, Inventario.cantidad_almacenada).\
            join(Inventario, Materias_Primas.id_materia_prima == Inventario.id_materia_prima).\
                filter(Materias_Primas.Activo == 1).\
                    all()
        # Cerramos la sesión
        session1.close()
        # Verificamos si la lista está vacía antes de acceder a sus elementos
        if not materias_primas_inventario:
            # Devolvemos una lista vacía si no hay datos en el inventario
            return []
        # Creamos una lista de diccionarios que contiene el nombre de la materia prima y su cantidad almacenada
        results = [{'Materia Prima': nombre, 'Cantidad Almacenada': cantidad} for nombre, cantidad in materias_primas_inventario]
        # Creamos un DataFrame para mostrar los resultados
        df_materia_prima = pd.DataFrame(results)
        return df_materia_prima
    except Exception as e:
        # En caso de que ocurra un error, mostramos el mensaje y devolvemos una lista vacía
        print(f"Error al obtener la cantidad de materia prima: {str(e)}")
        return []

def generate_gauge_graph(producto, stock_actual):
    # Create the gauge graph
    gauge_graph = go.Figure(go.Indicator(
        mode='gauge+number',
        value=stock_actual,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 20]},
            'bar': {'color': '#636efa'},
            'steps': [
                {'range': [0, 5], 'color': 'red'},
                {'range': [5, 10], 'color': 'yellow'},
                {'range': [15, 20], 'color': 'green'}
            ],
        }
    ))
    # Set the title of the gauge graph
    gauge_graph.update_layout(title_text=f'{producto}: {stock_actual}', width=400, height=300)
    return gauge_graph

def generate_gauge_graph1(producto, stock_actual, mini, uni):
    # Create the gauge graph
    gauge_graph = go.Figure(go.Indicator(
        mode='gauge+number',
        value=stock_actual,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, mini]},
            'bar': {'color': '#636efa'},
            'steps': [
                {'range': [0, mini/5*1], 'color': 'red'},
                {'range': [mini/5*1, mini/5*2], 'color': 'yellow'},
                {'range': [mini/5*4, mini], 'color': 'green'}
            ],
        }
    ))
    # Set the title of the gauge graph
    gauge_graph.update_layout(title_text=f'{producto}: {stock_actual} {uni}s', width=400, height=300)
    return gauge_graph

def obtener_usuarios_y_ventas_top_10():
    # Create a session to interact with the database
    session = get_sqlite_session()
    # Query to get user names and the count of their sales
    usuarios_y_ventas = (
        session.query(Users.usuario, Users.cantidad_ventas)
        .group_by(Users.usuario)
        .order_by(Users.cantidad_ventas.desc())
        .limit(10)
        .all()
    )
    # Close the session
    session.close()
    # Create a list of dictionaries containing user name and their sales count
    results = [{'Usuario': nombre, 'No. de Ventas': ventas} for nombre, ventas in usuarios_y_ventas]
    # Create a DataFrame to show the result
    df_usuarios_ventas = pd.DataFrame(results)
    return df_usuarios_ventas

def obtener_usuarios_y_ventas_top_101():
    # Create a session to interact with the database
    session1 = get_sql_server_session()
    # Query to get user names and the count of their sales
    usuarios_y_ventas = (
        session1.query(User.name, func.count(Ventas.id_venta).label('cantidad_ventas'))
        .join(Ventas, User.id == Ventas.id_usuario)
        .filter(User.active==1)
        .group_by(User.name)
        .order_by(func.count(Ventas.id_venta).desc())
        .limit(10)
        .all()
    )
    # Close the session
    session1.close()
    # Create a list of dictionaries containing user name and their sales count
    results = [{'Usuario': nombre, 'No. de Ventas': ventas} for nombre, ventas in usuarios_y_ventas]
    # Create a DataFrame to show the result
    df_usuarios_ventas = pd.DataFrame(results)
    return df_usuarios_ventas

def generate_table(dataframe, max_rows=10):
    try: 
        table = html.Table(
            # Agrega clases de estilo Bootstrap a la tabla
            className='table table-striped table-bordered table-hover',
            children=[
                # Encabezados de la tabla
                html.Thead(
                    html.Tr([
                        html.Th(col) for col in dataframe.columns
                    ])
                ),
                # Contenido de la tabla
                html.Tbody([
                    html.Tr([
                        html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                    ]) for i in range(len(dataframe))
                ])
            ]
        )
        return table
    except:
        # If no products sold data, generate an empty table with a message
        return html.Table([
                html.Tr([html.Td('No hay productos vendidos en este período', colSpan='4', className='empty-table-message')])
            ])