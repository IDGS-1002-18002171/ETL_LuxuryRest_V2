import subprocess
import logging
import json

# Agregamos la configuración básica del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Definimos una lista con los diferentes sites uids.
news_sites_uids = ['user','role','user_roles','productos','proveedores','materias_primas','receta','ventas','pedidos','pedidos_productos','inventario','compras','merma']
cont=0
# Función para actualizar el progreso en el archivo JSON
def update_progress(progress):
    with open('progress.json', 'r+') as f:
        data = json.load(f)
        data['progress'] = progress
        f.seek(0)  # Mover el puntero al inicio del archivo
        json.dump(data, f)
        f.truncate()  # Truncar el archivo para eliminar cualquier contenido restante

# Función principal que ejecuta las etapas paso a paso
def main():
    progress = {'progress': 0, 'status': 'En progreso'}
    with open('progress.json', 'w') as f:
        json.dump(progress, f)
    subprocess.run(['del', 'LuxuryRestETL.db'], shell=True, cwd='./load')
    global cont
    cont=0
    _extract()
    _transform()
    _load()
    logger.info('...::Proceso ETL Finalizado::...')

# Función encargada de invocar el proceso de extracción
def _extract():
    logger.info('...::Iniciando el Proceso de Extracción::...')
    global cont
    for news_sites_uid in news_sites_uids:
        subprocess.run(['python', 'main.py', news_sites_uid], cwd='./extract')
        cont=cont+2.565
        update_progress(cont)
    subprocess.run(['move', r'extract\*.csv', r'transform'], shell=True)
    # Actualizamos el progreso después de la etapa de extracción
    cont=33
    update_progress(33)

# Función encargada de invocar el proceso de transformación
def _transform():
    logger.info('...::Iniciando el Proceso de Transformación::...')
    global cont
    for news_sites_uid in news_sites_uids:
        dirty_data_filename = '{}.csv'.format(news_sites_uid)
        subprocess.run(['python', 'main.py', dirty_data_filename], cwd='./transform')
        subprocess.run(['del', dirty_data_filename], shell=True, cwd='./transform')
        cont=cont+2.565
        update_progress(cont)
    subprocess.run(['move', r'transform\*.csv', r'load'], shell=True)
    # Actualizamos el progreso después de la etapa de transformación
    cont=66
    update_progress(66)

# Función encargada de invocar el proceso de carga
def _load():
    logger.info('...::Iniciando el Proceso de Carga::...')
    global cont
    for news_sites_uid in news_sites_uids:
        clean_data_filename = 'clean_{}.csv'.format(news_sites_uid)
        subprocess.run(['python', 'main.py', clean_data_filename], cwd='./load')
        subprocess.run(['del', clean_data_filename], shell=True, cwd='./load')
        cont=cont+2.565
        update_progress(cont)
    # Actualizamos el progreso después de la etapa de carga
    cont=100
    update_progress(100)

if __name__ == '__main__':
    main()
