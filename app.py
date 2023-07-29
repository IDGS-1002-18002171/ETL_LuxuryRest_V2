import os
import subprocess
import logging
import json
import sqlite3

from flask import Flask, render_template, jsonify


app = Flask(__name__)

# Agregamos la configuración básica del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Ruta para iniciar el proceso ETL y obtener el progreso
@app.route('/start_etl')
def start_etl():
    # Creamos un proceso en segundo plano para ejecutar el ETL
    process = subprocess.Popen(['python', 'pipeline.py'], cwd=os.getcwd(), shell=True)

    return 'Proceso ETL iniciado.'

# Ruta para obtener el progreso del proceso ETL
@app.route('/progress')
def get_progress():
    try:
        with open('progress.json', 'r') as f:
            progress_data = json.load(f)
            return jsonify(progress_data)
    except FileNotFoundError:
        return jsonify({'progress': 0, 'status': 'No se encontró el progreso'})

if __name__ == '__main__':
    app.run(debug=True)
