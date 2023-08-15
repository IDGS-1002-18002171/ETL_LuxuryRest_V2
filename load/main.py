import argparse
import logging
import pandas as pd
from clases import Users, Ventas, Compras, Productos, Materias_Primas
from base import Base,engine,Session
from datetime import datetime

#Agregamos la configuracion del logging
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

def main(filename):
    #Generamos el squema de la BD
    Base.metadata.create_all(engine)
    #Iniciamos sesion
    session=Session()
    #Leemos nuestro archivo csv
    articles=pd.read_csv(filename,encoding="ISO-8859-1")

    # Obtenemos la extensión del archivo para identificar el tipo de datos
    filename_parts = filename.split("_")
    filename_masc = filename_parts[1]
    if len(filename_parts) > 2:
        filename_masc += "_" + filename_parts[2]
    filename_masc=filename_masc.split(".")[0]
    if filename_masc=='Users':
        for index, row in articles.iterrows():
            logger.info('Cargando al usuario {} en la BD'.format(row['usuario']))
            users = Users(row['usuario'],
                        row['cantidad_ventas'],)  
            session.add(users)
            session.commit()
            session.close()
    elif filename_masc=='Productos':
        for index, row in articles.iterrows():
            logger.info('Cargando el producto {} en la BD'.format(row['producto']))
            producto = Productos(
                        row['producto'],
                        row['cantidad_disponible'],
                        row['valoracion'],)  
            session.add(producto)
            session.commit()
            session.close()
    elif filename_masc=='Materias_Primas':
        for index, row in articles.iterrows():
            logger.info('Cargando la materia_prima {} en la BD'.format(row['materia_prima']))
            materia_prima = Materias_Primas(
                        row['materia_prima'],
                        row['unidad_medida'],
                        row['cantidad_minima_requerida'],
                        row['cantidad_en_inventario'],)  
            session.add(materia_prima)
            session.commit()
            session.close()
    elif filename_masc=='Ventas':
        for index, row in articles.iterrows():
            logger.info('Cargando la venta de la fecha {} en la BD'.format(row['fecha']))
            # Convierte la cadena a un objeto datetime antes de insertarlo en la BD
            format_with_milliseconds = '%Y-%m-%d'
            fecha_registro = datetime.strptime(row['fecha'], format_with_milliseconds)
            venta = Ventas(
                        row['producto'],
                        fecha_registro,
                        row['cantidad_vendida'],
                        row['precio_venta'],
                        row['total_venta'],)  
            session.add(venta)
            session.commit()
            session.close()
    elif filename_masc=='Compras':
        for index, row in articles.iterrows():
            logger.info('Cargando las compras de la fecha {} en la BD'.format(row['fecha']))
            # Convierte la cadena a un objeto datetime antes de insertarlo en la BD
            format_with_milliseconds = '%Y-%m-%d'
            fecha_registro = datetime.strptime(row['fecha'], format_with_milliseconds)
            compra = Compras(
                        fecha_registro,
                        row['total_compras'],)  
            session.add(compra)
            session.commit()
            session.close()
    

if __name__ == '__main__':
    #Creamos el parser de argumentos
    parser=argparse.ArgumentParser()

    #Creamos un argumento obligatorio
    parser.add_argument('filename',help='El archivo que deseas cargar hacia la BD',type=str)
    args=parser.parse_args()
    main(args.filename)