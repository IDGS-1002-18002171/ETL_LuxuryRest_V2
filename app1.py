import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from flask import Flask, render_template, jsonify, request, Response
import dash
from dash import dcc, html,State
from dash.dependencies import Input, Output
from sqlalchemy import create_engine
from clases import Ventas,PedidosProductos,Pedidos,Productos,Compras,Materias_Primas,Inventario
from sqlalchemy import func
from datetime import datetime, timedelta
import plotly.express as px
from sqlalchemy.orm import aliased
import json
import warnings
from sqlalchemy.exc import SAWarning
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#Declaramos el motor de base de datos a usar.
engine=create_engine('sqlite:///load/LuxuryRestETL.db')
Session=sessionmaker(bind=engine)

Base=declarative_base()

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

def obtener_productos_mas_vendidos_pasteles(start_date, end_date):
    # Convert the start_date and end_date to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Add 1 day to include the end date

    # Create a session to interact with the database
    session = Session()

    # Query to get sales for each product and sum the quantities sold
    ventas_productos = session.query(Productos.nombre, func.sum(PedidosProductos.cantidad)).\
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
    productos_mas_vendidos = [(nombre, cantidad) for nombre, cantidad in ventas_productos]

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
    gauge_graph.update_layout(title_text=f'{producto} - Stock Actual: {stock_actual}')

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
    gauge_graph.update_layout(title_text=f'{producto} - Stock Actual: {stock_actual}')

    return gauge_graph


# Set the initial df_ganancias when the app starts
default_start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
default_end_date = datetime.now().strftime('%Y-%m-%d')
df_ganancias = obtener_ganancias_por_periodo_personalizado(default_start_date, default_end_date)
# Llamar a la función para obtener la capacidad total del almacén
capacidad_almacen = obtener_productos_y_stock_actual()
# Llamar a la función para obtener la cantidad actual de materia prima en el inventario
cantidad_materia_prima_actual = obtener_cantidad_materia_prima_actual()
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
layout_elements.extend([html.Div([
    dcc.Graph(id='pie-chart')  # Pie chart
    ]),
    html.Div([
        # Nueva gráfica para mostrar la valoración actual de los productos
        dcc.Graph(id='valoracion-graphic'),
    ]),
    dcc.Input(id='dummy', style={'display': 'none'}),
    ])
layout_elements.extend([
    html.Div(id='ventas-section', style={'display': 'none'}, children=[
        dcc.Graph(id=f'stock-graphic-{i+1}')
        for i in range(len(capacidad_almacen))
    ]),
    # Second section (materia prima)
    html.Div(id='materia-prima-section', style={'display': 'none'}, children=[
        dcc.Graph(id=f'almacen-graphic-{i+1}')
        for i in range(len(cantidad_materia_prima_actual))
    ]),
    ])
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
     Output('materia-prima-section', 'style'),]+
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
            x_column = 'Día'
            title = f'Ganancias Diarias del {start_date.strftime("%Y-%m-%d")} al {end_date.strftime("%Y-%m-%d")}'
        else:
            # Daily view - Compras
            df_compras = obtener_compras_por_periodo_personalizado(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            x_column = 'Día'
            title = f'Compras Diarias del {start_date.strftime("%Y-%m-%d")} al {end_date.strftime("%Y-%m-%d")}'
    else:
        if current_view_type == 'ventas':
            # Monthly view - Ventas
            df_ganancias = obtener_ganancias_por_mes(start_date.year, start_date.month, end_date.year, end_date.month)
            x_column = 'Mes'
            title = f'Ganancias Mensuales del {start_date.strftime("%Y-%m")} al {end_date.strftime("%Y-%m")}'
            # Adjust the start_date to 1st of the month for the graph
            start_date = start_date.replace(day=1)
        else:
            # Monthly view - Compras
            df_compras = obtener_compras_por_mes(start_date.year, start_date.month, end_date.year, end_date.month)
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

        # Check if the list is empty before accessing its elements
        if not productos_mas_vendidos:
            # Handle the case when no data is available for products sold
            pie_chart = px.pie(title='Productos Más Vendidos')
        else:
            # Crear un nuevo DataFrame con dos columnas: 'nombre' y 'cantidad'
            df_productos_vendidos = pd.DataFrame(productos_mas_vendidos, columns=['nombre', 'cantidad'])

            # Generar la gráfica de pastel con los datos de productos más vendidos
            pie_chart = px.pie(
                df_productos_vendidos,
                values='cantidad',
                names='nombre',
                title='Productos Más Vendidos'
            )

    except ValueError as e:
        print(f"Error: {e}")
    # Actualizar la tabla de valoración de productos
    df_valoracion_actual = obtener_productos_valoracion_actual()
    valoracion_graphic = go.Figure(go.Bar(x=df_valoracion_actual['Nombre'], y=df_valoracion_actual['Valoracion Actual'],
                                            marker_color='#636efa'))
    # Set the title of the graph
    valoracion_graphic.update_layout(title_text="Valoraciones")

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
    
    return [data,figure, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), pie_chart,valoracion_graphic,toggle_button_text,ventas_section_style, materia_prima_section_style] + graphs_almacen+ graphs_almacen1

# Ruta para ejecutar el Dash app
@dash_app.server.route('/dash/')
def render_dashboard():
    return dash_app.index()

# Route to render the front-end HTML layout
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# Iniciar la aplicación Flask
if __name__ == '__main__':
    dash_app.run_server(debug=True)
