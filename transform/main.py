#Importamos la librería argparse para generar un CLI
import argparse, re
#Importamos la librería loggig para mostrar mensajes al usuario
import logging
logging.basicConfig(level=logging.INFO)
#Importamos la librería hashlib para encriptación
import hashlib
#Importamos la librería urlparse para parsean la forma de las url's
from urllib.parse import urlparse
#Importamos la librería de pandas para análisi de datos
import pandas as pd
#Importamos la librería nltk para extraer tokens del texto
import nltk
from nltk.corpus import stopwords
#Obtenemos una referencia al logger
logger = logging.getLogger(__name__)
#Definimos la Función principal
def main(file_name):
    logger.info('Iniciando Proceso de limpieza de Datos...')
    #Invocamos a la función para leer los datos.
    df = _read_data(file_name)
    #Invocamos a la función para extraer el newspaper uid
    newspaper_uid = _extract_newspaper_uid(file_name)
    #Invocamos a la funcion para agregar la columna newspaper_uid al Data Frame
    df = _add_newspaper_uid_column(df, newspaper_uid)
    #Invocamos a la función para Extraer el host de las url's
    """df = _extract_host(df)
    #Invocamos a la función para Rellenar los títulos faltantes
    df = _fill_missing_titles(df)
    #Invocamos a la fucnión para generar los uids para las filas.
    df = _generate_uids_for_rows(df)
    #Invocamos a la fucnión para remover los caracteres \n \r
    df = _remove_scape_characters_from_body(df)
    #Invocamos a la función para enriquecer el df agregando una columna con los tokens del title y el body.
    df = _data_enrichment(df)
    #Invocamos a la función para eliminar registros duplicados con base al título
    df = _remove_duplicate_entries(df, 'title')
    #Invocamos a la función para eliminar registros con valores faltantes
    df = drop_rows_with_missing_values(df) """
    #Invocamos a la función para guardar el df un archivo csv.
    _save_data_to_csv(df, file_name)
    
    
    return df
####################################################################
# Función para leer los datos del Data Set #
####################################################################
def _read_data(file_name):
    logger.info('Leyendo el archivo {}'.format(file_name))
    #Leemos el archvo csv y lo devolvemos el data frame
    return pd.read_csv(file_name, encoding='latin')
####################################################################
# Función para extraer el newspaper uid del nombre del archivo #
####################################################################
def _extract_newspaper_uid(file_name):
    logger.info('Extrayendo el newspaper uid')
    newspaper_uid = file_name.split('_')[0]
    
    logger.info('Newspaper udi Detectado: {}'.format(newspaper_uid))
    return newspaper_uid
####################################################################
# Función para agregar la columna con el newspaper_uid al df #
####################################################################
def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info('Llenando la columna newspaper_uid con {}'.format(newspaper_uid))
    #Agregamos la nueva columna al df y le pasamos el valor.
    df['newspaper_uid'] = newspaper_uid
    
    return df
####################################################################
# Función para extraer el host de las url's #
####################################################################
def _extract_host(df):
    logger.info('Extrayendo el host de las url')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)
    return df
#######################################################################
# Función para rellenar los títulos faltantes extrayendolos de la url #
#######################################################################
def _fill_missing_titles(df):
    logger.info('Rellenando los títulos faltantes')
    missing_titles_mask = df['title'].isna()
    df.loc[missing_titles_mask, 'title'] = df.loc[missing_titles_mask, 'url'].apply(lambda url: urlparse(url).path.split('/')[-1].replace('-', ' '))
    return df
############################################################################
# Función para generar los uids para las filas generando un hash de la url #
############################################################################
def _generate_uids_for_rows(df):
    logger.info('Generando uids para las filas')
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest())
           )
    df['uid'] = uids
    return df
############################################################################
# Función para remover los caracteres de escape del cuerpo del artículo #
############################################################################
def _remove_scape_characters_from_body(df):
    logger.info('Removiendo caracteres de escape del cuerpo del artículo')
    df['body'] = df['body'].apply(lambda text: re.sub(r'[\n\r]', ' ', text))
    return df
###############################################################################
# Función para enriquecer el df añadiendo una columna que cuente los tokens #
# (palabras significativas) en el título y cuerpo del artículo #
###############################################################################
def _data_enrichment(df):
    logger.info('Enriqueciendo el df con columnas de tokens')
    stop_words = set(stopwords.words('spanish'))
    df['n_tokens_title'] = df['title'].apply(lambda title: len([token for token in nltk.word_tokenize(title) if token.isalpha() and token.lower() not in stop_words]))
    df['n_tokens_body'] = df['body'].apply(lambda body: len([token for token in nltk.word_tokenize(body) if token.isalpha() and token.lower() not in stop_words]))
    return df
###############################################################################
# Función que obtiene los tokens principales para una determinada columna #
############################################################################### 
def _get_main_tokens(df, column):
    logger.info(f'Obteniendo los tokens principales de la columna {column}')
    stop_words = set(stopwords.words('spanish'))
    token_frequency = {}
    for text in df[column]:
        tokens = nltk.word_tokenize(text)
        for token in tokens:
            if token.isalpha() and token.lower() not in stop_words:
                if token in token_frequency:
                    token_frequency[token] += 1
                else:
                    token_frequency[token] = 1
    sorted_tokens = sorted(token_frequency.items(), key=lambda item: item[1], reverse=True)
    return sorted_tokens
##################################################################################
# Función que quita entradas duplicadas del df con el mismo valor en una columna #
##################################################################################
def _remove_duplicate_entries(df, column):
    logger.info(f'Eliminando entradas duplicadas en la columna {column}')
    df.drop_duplicates(subset=[column], inplace=True)
    return df
##################################################################################
# Función que elimina registros con valores faltantes (si es que aún los hay) #
##################################################################################
def drop_rows_with_missing_values(df):
    logger.info('Eliminando registros con valores faltantes')
    df.dropna(inplace=True)
    return df
##################################################################################
# Función que guarda los datos del DataFrame en un archivo csv #
##################################################################################
def _save_data_to_csv(df, filename):
    clean_filename = 'clean_{}'.format(filename)
    logger.info('Guardando los datos limpios en el archivo: {}'.format(clean_filename))
    df.to_csv(clean_filename)
##################################################################################
# Inicio de la aplicación #
##################################################################################
if __name__ == '__main__':
    #Creamos un nuevo parser de argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name',
    help='La ruta al dataset sucio',
    type=str)
    #Parseamos los argumentos.
    args = parser.parse_args()
    df = main(args.file_name)
    
    #Mostramos el Data Frame
    print(df)