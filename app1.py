import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from flask import Flask, render_template, jsonify, request, Response
import dash
from dash import dcc, html,State
from dash.dependencies import Input, Output
from clases import Ventas, PedidosProductos, Pedidos, Productos, Compras, Materias_Primas, Inventario, User
from datetime import datetime, timedelta
import json
import warnings
from sqlalchemy.exc import SAWarning
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, aliased
from sqlalchemy import text, func, create_engine
import matplotlib.pyplot as plt
#Declaramos el motor de base de datos SQLite.
engine=create_engine('sqlite:///load/LuxuryRestETL.db')
Session=sessionmaker(bind=engine)
Base=declarative_base()
# Declaramos la cadena de conexión para SQL Server con autenticación de Windows
connection_string = 'mssql+pyodbc://LAPTOP-H1G95B7K\\2022@LAPTOP-H1G95B7K\\SQLEXPRESS/LuxuryRest?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
engine1 = create_engine(connection_string)
Session1 = sessionmaker(bind=engine1)
# Usamos warnings
warnings.filterwarnings('ignore', category=SAWarning)
# Crear la aplicación Flask
app = Flask(__name__)
# Crear la aplicación Dash
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')
# Función para obtener las ganancias por un período personalizado
def obtener_ganancias_por_periodo_personalizado(start_date, end_date):
    # Convertir las fechas de inicio y fin a objetos datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    # Crear una lista para almacenar los resultados por día
    results = []
    # Crear una sesión para interactuar con la base de datos
    session = Session()
    # Obtener las fechas y ganancias por día dentro del período seleccionado
    current_date = start_date
    while current_date <= end_date:
        # Consulta para obtener las ganancias del día actual
        ganancias_periodo = session.query(func.sum(Ventas.precio_total)).filter(Ventas.fecha_hora_venta >= current_date, Ventas.fecha_hora_venta < current_date + timedelta(days=1)).scalar()
        # Agregar los resultados a la lista
        results.append({
            'Día': current_date.strftime('%Y-%m-%d'),
            'Ganancias': ganancias_periodo or 0
        })
        # Moverse al siguiente día
        current_date += timedelta(days=1)
    # Cerrar la sesión
    session.close()
    # Crear un DataFrame para mostrar el resultado
    df_ganancias = pd.DataFrame(results)
    return df_ganancias

# Función para obtener las ganancias por un período personalizado usando SQL Server
def obtener_ganancias_por_periodo_personalizado1(start_date, end_date):
    # Convertir las fechas de inicio y fin a objetos datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    # Crear una lista para almacenar los resultados por día
    results = []
    # Crear una sesión para interactuar con la base de datos
    session1 = Session1()
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

# Función para obtener el gasto total en compras por un período personalizado
def obtener_compras_por_periodo_personalizado(start_date, end_date):
    # Convertir las fechas de inicio y fin a objetos datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    # Crear una lista para almacenar los resultados por día
    results = []
    # Crear una sesión para interactuar con la base de datos
    session = Session()
    # Obtener las fechas y gasto total en compras por día dentro del período seleccionado
    current_date = start_date
    while current_date < end_date:
        # Calcular el día siguiente al día actual
        next_date = current_date + timedelta(days=1)
        # Consulta para obtener el gasto total en compras del día actual
        gasto_total_compras_periodo = session.query(func.sum(Compras.cantidad_comprada * Materias_Primas.precio_compra)).join(Materias_Primas).filter(
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
    session.close()
    # Crear un DataFrame para mostrar el resultado
    df_gasto_total_compras = pd.DataFrame(results)
    return df_gasto_total_compras

# Función para obtener el gasto total en compras por un período personalizado
def obtener_compras_por_periodo_personalizado1(start_date, end_date):
    # Convertir las fechas de inicio y fin a objetos datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    # Crear una lista para almacenar los resultados por día
    results = []
    # Crear una sesión para interactuar con la base de datos
    session1 = Session1()
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

# Función para obtener las ganancias por un rango de meses
def obtener_ganancias_por_mes(start_year, start_month, end_year, end_month):
    # Convertir los valores de año y mes a objetos datetime
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 1) + pd.offsets.MonthEnd(0)
    # Crear una lista para almacenar los resultados por mes
    results = []
    # Crear una sesión para interactuar con la base de datos
    session = Session()
    # Obtener las fechas y ganancias por mes dentro del rango seleccionado
    current_date = start_date
    while current_date <= end_date:
        # Calcular el primer día del mes actual
        first_day_of_month = current_date.replace(day=1)
        # Calcular el último día del mes actual
        last_day_of_month = first_day_of_month + pd.offsets.MonthEnd(0)
        # Consulta para obtener las ganancias del mes actual
        ganancias_mes = session.query(func.sum(Ventas.precio_total)).filter(
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
    session.close()
    # Crear un DataFrame para mostrar el resultado
    df_ganancias = pd.DataFrame(results)
    return df_ganancias

# Función para obtener las ganancias por un rango de meses
def obtener_ganancias_por_mes1(start_year, start_month, end_year, end_month):
    # Convertir los valores de año y mes a objetos datetime
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 1) + pd.offsets.MonthEnd(0)
    # Crear una lista para almacenar los resultados por mes
    results = []
    # Crear una sesión para interactuar con la base de datos
    session1 = Session1()
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

# Función para obtener el gasto en compras por un rango de meses
def obtener_compras_por_mes(start_year, start_month, end_year, end_month):
    # Convertir los valores de año y mes a objetos datetime
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 1) + pd.offsets.MonthEnd(0)
    # Crear una lista para almacenar los resultados por mes
    results = []
    # Crear una sesión para interactuar con la base de datos
    session = Session()
    # Obtener el gasto en compras por mes dentro del rango seleccionado
    current_date = start_date
    while current_date <= end_date:
        # Calcular el primer día del mes actual
        first_day_of_month = current_date.replace(day=1)
        # Calcular el último día del mes actual
        last_day_of_month = first_day_of_month + pd.offsets.MonthEnd(0)
        # Consulta para obtener el gasto en compras del mes actual
        gasto_compras_mes = session.query(func.sum(Materias_Primas.precio_compra)).filter(
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
    session.close()
    # Crear un DataFrame para mostrar el resultado
    df_gasto_compras = pd.DataFrame(results)
    return df_gasto_compras

# Función para obtener el gasto en compras por un rango de meses
def obtener_compras_por_mes1(start_year, start_month, end_year, end_month):
    # Convertir los valores de año y mes a objetos datetime
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 1) + pd.offsets.MonthEnd(0)
    # Crear una lista para almacenar los resultados por mes
    results = []
    # Crear una sesión para interactuar con la base de datos
    session1 = Session1()
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

def obtener_productos_mas_vendidos_pasteles(start_date, end_date):
    # Convert the start_date and end_date to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Add 1 day to include the end date
    # Create a session to interact with the database
    session = Session()
    # Query to get sales for each product and sum the quantities sold
    ventas_productos = session.query(Productos.nombre,Productos.precio_venta, func.sum(PedidosProductos.cantidad)).\
        join(PedidosProductos, Productos.id_producto == PedidosProductos.id_producto).\
        join(Pedidos, PedidosProductos.id_pedido == Pedidos.id_pedido).\
        filter(Pedidos.fecha_hora_pedido >= start_date, Pedidos.fecha_hora_pedido < end_date).\
        group_by(Productos.nombre).\
        order_by(func.sum(PedidosProductos.cantidad).desc()).\
        all()
    # Close the session
    session.close()
    # Check if the list is empty before accessing its elements
    if not ventas_productos:
        # Return an empty list if there are no sales data
        return [], []
    # Create a list of tuples (product name, quantity sold) for the pie chart
    productos_mas_vendidos = [(nombre,precio_venta, cantidad) for nombre,precio_venta, cantidad in ventas_productos]
    return productos_mas_vendidos

def obtener_productos_mas_vendidos_pasteles1(start_date, end_date):
    # Convert the start_date and end_date to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Add 1 day to include the end date
    # Create a session to interact with the database
    session1 = Session1()
    # Query to get sales for each product and sum the quantities sold
    ventas_productos = session1.query(
    Productos.nombre, Productos.precio_venta, func.sum(PedidosProductos.cantidad)
    ).\
    join(PedidosProductos, Productos.id_producto == PedidosProductos.id_producto).\
    join(Pedidos, PedidosProductos.id_pedido == Pedidos.id_pedido).\
    filter(Pedidos.fecha_hora_pedido >= start_date, Pedidos.fecha_hora_pedido < end_date).\
    group_by(Productos.nombre, Productos.precio_venta).\
    order_by(func.sum(PedidosProductos.cantidad).desc()).\
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

def obtener_productos_valoracion_actual():
    # Crear una lista para almacenar los resultados
    results = []
    # Crear una sesión para interactuar con la base de datos
    session = Session()
    # Consulta para obtener los productos y su valoración actual
    productos_valoracion = session.query(Productos.nombre, Productos.valoracionT, Productos.valoracionC).all()
    # Cerrar la sesión
    session.close()
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

def obtener_productos_valoracion_actual1():
    # Crear una lista para almacenar los resultados
    results = []
    # Crear una sesión para interactuar con la base de datos
    session1 = Session1()
    # Consulta para obtener los productos y su valoración actual
    productos_valoracion = session1.query(Productos.nombre, Productos.valoracionT, Productos.valoracionC).all()
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

def obtener_productos_y_stock_actual():
    # Create a session to interact with the database
    session = Session()
    # Query to get product names and their current stock quantities
    productos_stock_actual = session.query(Productos.nombre, Productos.cantidad_disponible).all()
    # Close the session
    session.close()
    # Check if the list is empty before accessing its elements
    if not productos_stock_actual:
        # Return an empty list if there are no products or stock data
        return []
    # Create a list of dictionaries containing product name and current stock quantity
    results = [{'Nombre': nombre, 'Stock Actual': stock} for nombre, stock in productos_stock_actual]
    # Crear un DataFrame para mostrar el resultado
    df_stock = pd.DataFrame(results)
    return df_stock

def obtener_productos_y_stock_actual1():
    # Create a session to interact with the database
    session1 = Session1()
    # Query to get product names and their current stock quantities
    productos_stock_actual = session1.query(Productos.nombre, Productos.cantidad_disponible).all()
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

def obtener_cantidad_materia_prima_actual():
    session = Session()
    try:
        # Consulta para obtener la cantidad actual de materia prima almacenada en el inventario
        materias_primas_inventario = session.query(Materias_Primas.nombre, Inventario.cantidad_almacenada).\
            join(Inventario, Materias_Primas.id_materia_prima == Inventario.id_materia_prima).all()
        # Cerramos la sesión
        session.close()
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

def obtener_cantidad_materia_prima_actual1():
    session1 = Session1()
    try:
        # Consulta para obtener la cantidad actual de materia prima almacenada en el inventario
        materias_primas_inventario = session1.query(Materias_Primas.nombre, Inventario.cantidad_almacenada).\
            join(Inventario, Materias_Primas.id_materia_prima == Inventario.id_materia_prima).all()
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
    gauge_graph.update_layout(title_text=f'{producto} - Stock Actual: {stock_actual}', width=400, height=300)
    return gauge_graph

def generate_gauge_graph1(producto, stock_actual):
    # Create the gauge graph
    gauge_graph = go.Figure(go.Indicator(
        mode='gauge+number',
        value=stock_actual,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 500]},
            'bar': {'color': '#636efa'},
            'steps': [
                {'range': [0, 100], 'color': 'red'},
                {'range': [100, 200], 'color': 'yellow'},
                {'range': [400, 500], 'color': 'green'}
            ],
        }
    ))
    # Set the title of the gauge graph
    gauge_graph.update_layout(title_text=f'{producto} - Inventario Actual: {stock_actual}', width=400, height=300)
    return gauge_graph

def obtener_usuarios_y_ventas_top_10():
    # Create a session to interact with the database
    session = Session()
    # Query to get user names and the count of their sales
    usuarios_y_ventas = (
        session.query(User.name, func.count(Ventas.id_venta).label('cantidad_ventas'))
        .join(Ventas, User.id == Ventas.id_usuario)
        .group_by(User.name)
        .order_by(func.count(Ventas.id_venta).desc())
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
    session1 = Session1()
    # Query to get user names and the count of their sales
    usuarios_y_ventas = (
        session1.query(User.name, func.count(Ventas.id_venta).label('cantidad_ventas'))
        .join(Ventas, User.id == Ventas.id_usuario)
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

# Set the initial df_ganancias when the app starts
default_start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
default_end_date = datetime.now().strftime('%Y-%m-%d')
df_ganancias = obtener_ganancias_por_periodo_personalizado(default_start_date, default_end_date)
# Llamar a la función para obtener la capacidad total del almacén
capacidad_almacen = obtener_productos_y_stock_actual()
capacidad_almacen1 = obtener_productos_y_stock_actual1()
capacidad_almacen = pd.concat([capacidad_almacen, capacidad_almacen1], ignore_index=True)
# Llamar a la función para obtener la cantidad actual de materia prima en el inventario
cantidad_materia_prima_actual = obtener_cantidad_materia_prima_actual()
cantidad_materia_prima_actual1 = obtener_cantidad_materia_prima_actual1()
cantidad_materia_prima_actual = pd.concat([cantidad_materia_prima_actual, cantidad_materia_prima_actual1], ignore_index=True)
current_view_type='ventas'
# Set the initial button state when the app starts
initial_button_state = {'daily-clicks': 0, 'monthly-clicks': 0, 'view-type': 'ventas', 'view-toggle-button': 0}
# Layout del Dash app
layout_elements = [
    html.H1('Dashboard de Compras y Ventas mediante período personalizado'),
    # Date Picker para seleccionar el rango de fechas
    html.Button('Cambiar a Compras', id='view-toggle-button', n_clicks=0),
    dcc.DatePickerRange(
        id='date-picker',
        display_format='Y-MM-DD',  # Use the desired format
        start_date=default_start_date,
        end_date=default_end_date,
        style={'margin-bottom': '20px'}
    ),
    # Buttons for daily and monthly view
    dcc.Store(id='data-store', data={'df_ganancias': None, 'df_compras': None, 'button-state': initial_button_state}),
    html.Div([
        html.Button('Update Graph', id='update-button', n_clicks=0, style={'margin-top': '20px'}),
        html.Button('Vista Diaria', id='daily-button', n_clicks=0, style={'margin-right': '10px'}),
        html.Button('Vista Mensual', id='monthly-button', n_clicks=0, style={'margin-right': '10px'})
    ], style={'margin-bottom': '20px'}),
    html.Div([
        dcc.Graph(id='bar-graph')  # Bar chart
    ]),]
layout_elements.extend([
    html.Div([
    dcc.Graph(id='pie-chart')  # Pie chart
    ]),
    html.Div([
    dcc.Graph(id='usu-top')  # Usu chart
    ]),
    html.Div([
        # Nueva gráfica para mostrar la valoración actual de los productos
        dcc.Graph(id='valoracion-graphic'),
    ]),
    dcc.Input(id='dummy', style={'display': 'none'}),
    ])
# Antes del layout_elements.extend, define un nuevo div contenedor que utilizará el estilo 'display: flex'
ventas_materia_prima_container = html.Div(
    style={'display': 'flex', 'flex-wrap': 'wrap'}
)

# Luego, agrega las gráficas de ventas (stock-graphic) al contenedor ventas_materia_prima_container
ventas_materia_prima_container_children = [
    dcc.Graph(id=f'stock-graphic-{i+1}')
    for i in range(len(capacidad_almacen))
]
ventas_materia_prima_container.children = ventas_materia_prima_container_children
# Agrega el contenedor de ventas (stock-graphic) al layout_elements
layout_elements.append(html.Div(id='ventas-section', style={'display': 'none'}, children=ventas_materia_prima_container))
# Después, agrega un nuevo div contenedor para las gráficas de materia prima (almacen-graphic)
materia_prima_container = html.Div(
    style={'display': 'flex', 'flex-wrap': 'wrap'}
)
# Agrega las gráficas de materia prima (almacen-graphic) al contenedor materia_prima_container
materia_prima_container_children = [
    dcc.Graph(id=f'almacen-graphic-{i+1}')
    for i in range(len(cantidad_materia_prima_actual))
]
materia_prima_container.children = materia_prima_container_children
# Agrega el contenedor de materia prima (almacen-graphic) al layout_elements
layout_elements.append(html.Div(id='materia-prima-section', style={'display': 'none'}, children=materia_prima_container))
# Finalmente, asignar el layout a la app
dash_app.layout = html.Div(layout_elements)
# Callback para el botón "Vista Diaria"
@dash_app.callback(
    [Output('data-store', 'data'),
     Output('bar-graph', 'figure'),
     Output('date-picker', 'start_date'),
     Output('date-picker', 'end_date'),
     Output('pie-chart', 'figure'),
     Output('valoracion-graphic', 'figure'),
     Output('view-toggle-button', 'children'),
     Output('ventas-section', 'style'),
     Output('materia-prima-section', 'style'),
     Output('usu-top', 'figure'),]+
     [Output(f'stock-graphic-{i+1}', 'figure') for i in range(len(capacidad_almacen))],
     [Output(f'almacen-graphic-{i+1}', 'figure') for i in range(len(cantidad_materia_prima_actual))],
    [Input('daily-button', 'n_clicks'),
     Input('monthly-button', 'n_clicks'),
     Input('view-toggle-button', 'n_clicks'),
     Input('update-button', 'n_clicks')],
    [State('data-store', 'data'),
     State('date-picker', 'start_date'),
     State('date-picker', 'end_date')]
)
def update_graph(daily_clicks, monthly_clicks, toggle_clicks, n_clicks, data, start_date, end_date):
    global df_ganancias, df_compras, capacidad_almacen, current_view_type,cantidad_materia_prima_actual
    # Use the dash.callback_context to get the ID of the triggered button
    triggered_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    # Check if start_date and end_date are None and provide default values
    if not start_date:
        start_date = datetime.now() - timedelta(days=6)
    if not end_date:
        end_date = datetime.now()
    # Convert the dates to datetime objects (if they are strings)
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    # Determine the view type (ventas or compras) based on the toggle button click
    current_view_type = 'ventas' if toggle_clicks % 2 == 0 else 'compras'
    # Update the data store with button clicks
    data['button-state']['daily-clicks'] = daily_clicks
    data['button-state']['monthly-clicks'] = monthly_clicks
    # Determine the view mode (daily or monthly) based on button clicks
    is_daily_view = daily_clicks > monthly_clicks
    # Update the table body and graph data based on the view mode and view type
    if is_daily_view:
        if current_view_type == 'ventas':
            # Daily view - Ventas
            df_ganancias = obtener_ganancias_por_periodo_personalizado(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            df_ganancias1 = obtener_ganancias_por_periodo_personalizado1(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            # Combina los DataFrames a lo largo del eje de las filas
            df_ganancias = pd.concat([df_ganancias, df_ganancias1], ignore_index=True)
            x_column = 'Día'
            title = f'Ganancias Diarias del {start_date.strftime("%Y-%m-%d")} al {end_date.strftime("%Y-%m-%d")}'
        else:
            # Daily view - Compras
            df_compras = obtener_compras_por_periodo_personalizado(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            df_compras1 = obtener_compras_por_periodo_personalizado1(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            df_compras = pd.concat([df_compras, df_compras1], ignore_index=True)
            x_column = 'Día'
            title = f'Compras Diarias del {start_date.strftime("%Y-%m-%d")} al {end_date.strftime("%Y-%m-%d")}'
    else:
        if current_view_type == 'ventas':
            # Monthly view - Ventas
            df_ganancias = obtener_ganancias_por_mes(start_date.year, start_date.month, end_date.year, end_date.month)
            df_ganancias1 = obtener_ganancias_por_mes1(start_date.year, start_date.month, end_date.year, end_date.month)
            df_ganancias = pd.concat([df_ganancias, df_ganancias1], ignore_index=True)
            x_column = 'Mes'
            title = f'Ganancias Mensuales del {start_date.strftime("%Y-%m")} al {end_date.strftime("%Y-%m")}'
            # Adjust the start_date to 1st of the month for the graph
            start_date = start_date.replace(day=1)
        else:
            # Monthly view - Compras
            df_compras = obtener_compras_por_mes(start_date.year, start_date.month, end_date.year, end_date.month)
            df_compras1 = obtener_compras_por_mes1(start_date.year, start_date.month, end_date.year, end_date.month)
            df_compras = pd.concat([df_compras, df_compras1], ignore_index=True)
            x_column = 'Mes'
            title = f'Compras Mensuales del {start_date.strftime("%Y-%m")} al {end_date.strftime("%Y-%m")}'
            # Adjust the start_date to 1st of the month for the graph
            start_date = start_date.replace(day=1)

    # Check if the expected x_column is present in the DataFrame
    if x_column not in df_ganancias.columns and current_view_type == 'ventas':
        # If the expected x_column is not present, return an empty bar chart
        figure = px.scatter(title=title)
    else:
        # Generate the bar chart with the updated data and title
        if is_daily_view:
            if current_view_type == 'ventas':
                figure = px.scatter(df_ganancias, x=x_column, y='Ganancias', title=title)
            else:
                # Check if the expected y_column is present in df_compras
                if 'Compras' in df_compras.columns:
                    figure = px.scatter(df_compras, x=x_column, y='Compras', title=title)
                else:
                    # If the expected y_column is not present, return an empty bar chart
                    figure = px.scatter(title=title)
        else:
            if current_view_type == 'ventas':
                figure = px.bar(df_ganancias, x=x_column, y='Ganancias', title=title)
            else:
                # Check if the expected y_column is present in df_compras
                if 'Compras' in df_compras.columns:
                    figure = px.bar(df_compras, x=x_column, y='Compras', title=title)
                else:
                    # If the expected y_column is not present, return an empty bar chart
                    figure = px.bar(title=title)
    # Determine the text of the view toggle button based on the current view type
    toggle_button_text = 'Cambiar a Ventas' if current_view_type == 'compras' else 'Cambiar a Compras'
    # Assign a default value to pie_chart in case no data is available
    pie_chart = px.pie(title='Productos Más Vendidos')
    try:
        # Agregar el código para obtener los nombres de los productos más vendidos y sus cantidades
        productos_mas_vendidos = obtener_productos_mas_vendidos_pasteles(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        productos_mas_vendidos1 = obtener_productos_mas_vendidos_pasteles1(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        # Check if the list is empty before accessing its elements
        if not productos_mas_vendidos:
            # Handle the case when no data is available for products sold
            pie_chart = px.pie(title='No ahy productos Vendidos')
        else:
            # Crear un nuevo DataFrame con dos columnas: 'nombre' y 'cantidad'
            df_productos_vendidos = pd.DataFrame(productos_mas_vendidos, columns=['nombre', 'precio_venta','cantidad'])
            df_productos_vendidos1 = pd.DataFrame(productos_mas_vendidos1, columns=['nombre', 'precio_venta','cantidad'])
            df_productos_vendidos = pd.concat([df_productos_vendidos, df_productos_vendidos1], ignore_index=True)
            df_copy=df_productos_vendidos.copy()
            # Calcular el total de ventas para cada producto
            df_productos_vendidos['total'] = df_productos_vendidos['precio_venta'] * df_productos_vendidos['cantidad']
            # Convertir las columnas 'precio_venta' y 'total' a cadenas y combinarlas para la leyenda
            df_productos_vendidos['leyenda'] = 'Total: ' + df_productos_vendidos['total'].astype(str)
            # Generar la gráfica de pastel con los datos de productos más vendidos
            pie_chart = px.pie(
                df_productos_vendidos,
                values='cantidad',
                names='nombre',
                title='Productos Más Vendidos',
                hover_data=['precio_venta'] , # Agregar cantidad y precio_venta como información adicional en el hover
                hover_name='leyenda',
            )
    except ValueError as e:
        print(f"Error: {e}")
    # Actualizar la tabla de valoración de productos
    df_valoracion_actual = obtener_productos_valoracion_actual()
    df_valoracion_actual1 = obtener_productos_valoracion_actual1()
    df_valoracion_actual = pd.concat([df_valoracion_actual, df_valoracion_actual1], ignore_index=True)
    # Paleta de colores personalizada con 20 colores diferentes
    custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                    '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
                    '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5']
    valoracion_graphic = go.Figure(go.Bar(
        x=df_valoracion_actual['Nombre'],
        y=df_valoracion_actual['Valoracion Actual'],
        marker_color=custom_colors  # Asignamos colores diferentes a cada barra
    ))
    # Mejoras en el diseño del gráfico
    valoracion_graphic.update_layout(
        title_text="Valoraciones de Productos",  # Título del gráfico
        xaxis_title="Producto",  # Etiqueta del eje X
        yaxis_title="Valoración",  # Etiqueta del eje Y
        title_font=dict(size=24),  # Tamaño del título
        xaxis_tickangle=-45,  # Rotación de las etiquetas del eje X para mejorar la legibilidad
        yaxis=dict(tickvals=list(range(1, 6))),  # Asegurar que las etiquetas del eje Y sean enteros del 1 al 5
        margin=dict(l=50, r=50, t=80, b=50)  # Ajustar márgenes para evitar recorte de elementos
    )
    # Luego, para los gráficos de almacen-graphic
    graphs_almacen = []
    graphs_almacen1 = []
    for i in range(len(capacidad_almacen)):
        # Aquí iría el código para generar los gráficos de almacen-graphic para cada elemento en capacidad_almacen
        # Se asume que existirá una función llamada 'generate_almacen_graph' que generará los gráficos para cada elemento de capacidad_almacen
        graph = generate_gauge_graph(capacidad_almacen['Nombre'][i],capacidad_almacen['Stock Actual'][i])  # Esta función es hipotética, deberías crearla según tus necesidades
        graphs_almacen.append(graph)
    for i in range(len(cantidad_materia_prima_actual)):
        # Aquí iría el código para generar los gráficos de almacen-graphic para cada elemento en capacidad_almacen
        # Se asume que existirá una función llamada 'generate_almacen_graph' que generará los gráficos para cada elemento de capacidad_almacen
        graph = generate_gauge_graph1(cantidad_materia_prima_actual['Materia Prima'][i],int(cantidad_materia_prima_actual['Cantidad Almacenada'][i]))  # Esta función es hipotética, deberías crearla según tus necesidades
        graphs_almacen1.append(graph)
    if current_view_type == 'ventas':
        # Mostrar la sección de ventas y ocultar la sección de materia prima
        ventas_section_style = {'display': 'block'}
        materia_prima_section_style = {'display': 'none'}
    else:
        # Mostrar la sección de materia prima y ocultar la sección de ventas
        ventas_section_style = {'display': 'none'}
        materia_prima_section_style = {'display': 'block'}
    df_usuarios_ventas = obtener_usuarios_y_ventas_top_10()
    df_usuarios_ventas1 = obtener_usuarios_y_ventas_top_101()
    df_usuarios_ventas = pd.concat([df_usuarios_ventas, df_usuarios_ventas1], ignore_index=True)
    # Crear el gráfico de líneas
    usuarios_grafico = go.Figure(go.Scatter(x=df_usuarios_ventas['Usuario'], y=df_usuarios_ventas['No. de Ventas'],
                                             mode='lines+markers',
                                             line=dict(color='#636efa', width=2),
                                             marker=dict(size=8, symbol='circle', color='#636efa')))
    # Establecer el título del gráfico
    usuarios_grafico.update_layout(title_text="Top Usuarios - Ventas",
                                     xaxis_title="Nombre del Usuarios",
                                     yaxis_title="Ventas por el Usuario")
    return [data,figure, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), pie_chart,valoracion_graphic,toggle_button_text,ventas_section_style, materia_prima_section_style,usuarios_grafico] + graphs_almacen+ graphs_almacen1
# Ruta para ejecutar el Dash app
@dash_app.server.route('/dash/')
def render_dashboard():
    return dash_app.index()
# Iniciar la aplicación Flask
if __name__ == '__main__':
    dash_app.run_server(debug=True)