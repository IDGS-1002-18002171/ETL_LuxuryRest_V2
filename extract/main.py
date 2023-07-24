#Para crear un parseador de argumentos
import argparse
#import news_page_objects as news
#Para mostrar mensajes en pantalla
import logging
from requests.models import HTTPError
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
import re
from os import write
import csv
import datetime
logging.basicConfig(level=logging.INFO)

from common import config
#Obtenemos una referencia al logger
logger=logging.getLogger(__name__)
is_well_formed_link=re.compile(r'^https?://.+/.+$') #https://example.com/hello
is_root_path=re.compile(r'^/.+$') #/some-text

import requests
import pandas as pd


# Función para recuperar los datos desde la API de Mockaroo y guardarlos en un archivo CSV
def _news_scraper(news_site_uid):
    # URL de la API de Mockaroo que devuelve los datos en formato JSON
    api_key = "196dfc30"
    api_url = f"https://my.api.mockaroo.com/{news_site_uid}.json?key={api_key}"

    # Realizar la solicitud HTTP para obtener los datos en formato JSON desde la API de Mockaroo
    response = requests.get(api_url)

    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Obtener los datos en formato JSON
        data_json = response.json()

        # Convertir los datos JSON en un DataFrame de Pandas
        df = pd.DataFrame(data_json)

        # Guardar el DataFrame en un archivo CSV
        csv_file_name = f"{news_site_uid}.csv"
        df.to_csv(csv_file_name, index=False, encoding='utf-8')
        print(f"Datos guardados en '{csv_file_name}'.")
    else:
        print(f"Error al obtener los datos de {news_site_uid} (código de estado: {response.status_code})")

if __name__ == '__main__':
    #Creamos un nuevo parser de argumentos
    parser=argparse.ArgumentParser()

    #Recuperando las claves que se definieron en la configuracion
    news_site_choices=list(config()['news_sites'].keys())
    #Añadiendo argumentos obligatorios al parser
    parser.add_argument('news_sites',help='El sitio de noticias del que quieres obtener articulos',type=str,choices=news_site_choices)
    args=parser.parse_args()
    #Llamamos a la funcion para recuperar las url's
    _news_scraper(args.news_sites)