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
import threading
import funciones as funcion

# Usamos warnings
warnings.filterwarnings('ignore', category=SAWarning)
# Crear la aplicación Flask
app = Flask(__name__)
# Crear la aplicación Dash
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')
# Set the initial df_ganancias when the app starts
default_start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
default_end_date = datetime.now().strftime('%Y-%m-%d')
df_ganancias = funcion.obtener_ganancias_por_periodo_personalizado(default_start_date, default_end_date)
# Llamar a la función para obtener la capacidad total del almacén
capacidad_almacen = funcion.obtener_productos_y_stock_actual()
capacidad_almacen1 = funcion.obtener_productos_y_stock_actual1()
capacidad_almacen = pd.concat([capacidad_almacen, capacidad_almacen1], ignore_index=True)
# Llamar a la función para obtener la cantidad actual de materia prima en el inventario
cantidad_materia_prima_actual = funcion.obtener_cantidad_materia_prima_actual()
cantidad_materia_prima_actual1 = funcion.obtener_cantidad_materia_prima_actual1()
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
            df_ganancias = funcion.obtener_ganancias_por_periodo_personalizado(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            df_ganancias1 = funcion.obtener_ganancias_por_periodo_personalizado1(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            # Combina los DataFrames a lo largo del eje de las filas
            df_ganancias = pd.concat([df_ganancias, df_ganancias1], ignore_index=True)
            x_column = 'Día'
            title = f'Ganancias Diarias del {start_date.strftime("%Y-%m-%d")} al {end_date.strftime("%Y-%m-%d")}'
        else:
            # Daily view - Compras
            df_compras = funcion.obtener_compras_por_periodo_personalizado(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            df_compras1 = funcion.obtener_compras_por_periodo_personalizado1(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            df_compras = pd.concat([df_compras, df_compras1], ignore_index=True)
            x_column = 'Día'
            title = f'Compras Diarias del {start_date.strftime("%Y-%m-%d")} al {end_date.strftime("%Y-%m-%d")}'
    else:
        if current_view_type == 'ventas':
            # Monthly view - Ventas
            df_ganancias = funcion.obtener_ganancias_por_mes(start_date.year, start_date.month, end_date.year, end_date.month)
            df_ganancias1 = funcion.obtener_ganancias_por_mes1(start_date.year, start_date.month, end_date.year, end_date.month)
            df_ganancias = pd.concat([df_ganancias, df_ganancias1], ignore_index=True)
            x_column = 'Mes'
            title = f'Ganancias Mensuales del {start_date.strftime("%Y-%m")} al {end_date.strftime("%Y-%m")}'
            # Adjust the start_date to 1st of the month for the graph
            start_date = start_date.replace(day=1)
        else:
            # Monthly view - Compras
            df_compras = funcion.obtener_compras_por_mes(start_date.year, start_date.month, end_date.year, end_date.month)
            df_compras1 = funcion.obtener_compras_por_mes1(start_date.year, start_date.month, end_date.year, end_date.month)
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
        productos_mas_vendidos = funcion.obtener_productos_mas_vendidos_pasteles(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        productos_mas_vendidos1 = funcion.obtener_productos_mas_vendidos_pasteles1(
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
    df_valoracion_actual = funcion.obtener_productos_valoracion_actual()
    df_valoracion_actual1 = funcion.obtener_productos_valoracion_actual1()
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
        graph = funcion.generate_gauge_graph(capacidad_almacen['Nombre'][i],capacidad_almacen['Stock Actual'][i])  # Esta función es hipotética, deberías crearla según tus necesidades
        graphs_almacen.append(graph)
    for i in range(len(cantidad_materia_prima_actual)):
        # Aquí iría el código para generar los gráficos de almacen-graphic para cada elemento en capacidad_almacen
        # Se asume que existirá una función llamada 'generate_almacen_graph' que generará los gráficos para cada elemento de capacidad_almacen
        graph = funcion.generate_gauge_graph1(cantidad_materia_prima_actual['Materia Prima'][i],int(cantidad_materia_prima_actual['Cantidad Almacenada'][i]))  # Esta función es hipotética, deberías crearla según tus necesidades
        graphs_almacen1.append(graph)
    if current_view_type == 'ventas':
        # Mostrar la sección de ventas y ocultar la sección de materia prima
        ventas_section_style = {'display': 'block'}
        materia_prima_section_style = {'display': 'none'}
    else:
        # Mostrar la sección de materia prima y ocultar la sección de ventas
        ventas_section_style = {'display': 'none'}
        materia_prima_section_style = {'display': 'block'}
    df_usuarios_ventas = funcion.obtener_usuarios_y_ventas_top_10()
    df_usuarios_ventas1 = funcion.obtener_usuarios_y_ventas_top_101()
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