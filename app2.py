from flask_cors import CORS
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from flask import Flask, render_template, jsonify, request, Response
from clases import Ventas, Pedidos_Productos, Pedidos, Productos, Compras, Materias_Primas, Inventario, User
from datetime import datetime, timedelta
import json
import warnings
from sqlalchemy.exc import SAWarning
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, aliased
from sqlalchemy import text, func, create_engine
import threading
import funciones as funcion
import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})

@app.route('/generate_bar_chart', methods=['POST'])
def generate_bar_chart():
    # Obtener los datos de la solicitud
    data = request.json
    # Llamar a la función de generación de gráficas con los datos
    figure = px.scatter(data, x="id_venta", y='id_usuario', title="Gol")
     # Convertir el objeto Figure a una cadena JSON
    figure_json = figure.to_json()

    # Enviar la cadena JSON como respuesta
    return jsonify(figure_json)

@app.route('/generate_pie_chart', methods=['POST'])
def generate_pie_chart():
    # Obtener los datos de la solicitud
    data = request.json
    # Llamar a la función de generación de gráficas con los datos
    pie_chart = go.Figure(go.Pie(
        labels=data['id_venta'],
        values=data['id_usuario'],
        title="Productos Más Vendidos",
        hoverinfo='label+percent+value'
    ))
    figure_json = pie_chart.to_json()

    # Enviar la cadena JSON como respuesta
    return jsonify(figure_json)

@app.route('/generate_valoracion_graphic', methods=['POST'])
def generate_valoracion_graphic():
    # Obtener los datos de la solicitud
    data = request.json
    # Llamar a la función de generación de gráficas con los datos
    custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                     '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    valoracion_graphic = go.Figure(go.Bar(
        x=data['id_venta'],
        y=data['id_usuario'],
        marker_color=custom_colors
    ))
    valoracion_graphic.update_layout(
        title_text="Valoraciones de Productos",
        xaxis_title="Producto",
        yaxis_title="Valoración",
        title_font=dict(size=24),
        xaxis_tickangle=-45,
        yaxis=dict(tickvals=list(range(1, 6))),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    figure_json = valoracion_graphic.to_json()

    # Enviar la cadena JSON como respuesta
    return jsonify(figure_json)

@app.route('/generate_gauge_graph', methods=['POST'])
def generate_gauge_graph():
    # Obtener los datos de la solicitud
    data = request.json
    # Llamar a la función de generación de gráficas con los datos
    gauge_graph = go.Figure(go.Indicator(
        mode="gauge+number",
        value=data['id_venta'][0],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Stock de {data['id_usuario'][0]}"}
    ))
    figure_json = gauge_graph.to_json()

    # Enviar la cadena JSON como respuesta
    return jsonify(figure_json)

@app.route('/generate_gauge_graph1', methods=['POST'])
def generate_gauge_graph1():
    # Obtener los datos de la solicitud
    data = request.json
    # Llamar a la función de generación de gráficas con los datos
    gauge_graph = go.Figure(go.Indicator(
        mode="gauge+number",
        value=data['id_venta'][0],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Stock de {data['id_usuario'][0]}"}
    ))
    figure_json = gauge_graph.to_json()

    # Enviar la cadena JSON como respuesta
    return jsonify(figure_json)

# Iniciar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
