import datetime
import subprocess
import logging

#Agregamos la configuracion basica del logging
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

#Definimos una lista con los diferentes sites uids. 
news_sites_uids=['productos','merma']

#Funcion principal que ejecuta las etapas paso a paso
def main():
    _extract()
    _transform()
    _load()
    logger.info('...::Proceso ETL Finalizado::...')

#Funcion encargada de invocar el proceso de extraccion
def _extract():
    logger.info('...::Iniciando el Proceso de Extraccion::...')

    #Iteramos por cada uno de los newssites que tenemos en la configuracion.
    for news_sites_uid in news_sites_uids:
        #Ejecutamos la etapa de extraccion en la carpeta /extract
        subprocess.run(['python','main.py',news_sites_uid], cwd='./extract')

        #Movemos el archivo .csv a la carpeta / en modo seguro
    subprocess.run(['move',r'extract\*.csv',r'transform'],shell=True)

#Funcion encargada de invocar el proceso de transformacion
def _transform():
    logger.info('...::Iniciando el Proceso de Transformacion::...')

    #Iteramos por cada uno de los newssites que tenemos en la configuracion.
    for news_sites_uid in news_sites_uids:
        dirty_data_filename = '{}.csv'.format(news_sites_uid)

        #Ejecutamos la etapa de transformacion en la carpeta /extract
        subprocess.run(['python','main.py',dirty_data_filename], cwd='./transform')
        #Eliminamos el archivo .csv sucio
        subprocess.run(['del',dirty_data_filename],shell=True,cwd='./transform')
        #Movemos el archivo .csv limpio a la carpeta load.
    subprocess.run(['move',r'transform\*.csv',r'load'],shell=True)

#Funcion encargada de invocar el proceso de carga
def _load():
    logger.info('...::Iniciando el Proceso de Carga::...')

    #Iteramos por cada uno de los newssites que tenemos en la configuracion.
    for news_sites_uid in news_sites_uids:
        clean_data_filename = 'clean_{}.csv'.format(news_sites_uid)

        #Ejecutamos la etapa de carga en la carpeta /load
        subprocess.run(['python','main.py',clean_data_filename], cwd='./load')
        #Eliminamos el archivo .csv limpio
        subprocess.run(['del',clean_data_filename],shell=True,cwd='./load')

if __name__ == '__main__':
    main()