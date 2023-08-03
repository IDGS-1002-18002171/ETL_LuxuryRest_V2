import argparse
import logging
import pandas as pd
from clases import Role,User,UserRoles,Productos,Proveedores,Materias_Primas,Receta,Ventas,Pedidos,PedidosProductos,Inventario,Compras,Merma
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
    if filename_masc=='role':
        for index, row in articles.iterrows():
            logger.info('Cargando el role con uid: {} en la BD'.format(row['id_role']))
            role=Role(row['id_role'],
            row['name'],
            row['description'],)
            session.add(role)

            session.commit()
            session.close()
    elif filename_masc=='user':
        for index, row in articles.iterrows():
            logger.info('Cargando el user con uid: {} en la BD'.format(row['id_usuario']))
            # Convierte la cadena a un objeto datetime antes de insertarlo en la BD
            confirmed_at = datetime.strptime(row['confirmed_at'], '%Y-%m-%d %H:%M:%S')
            user = User(row['id_usuario'],
                        row['name'],
                        row['email'],
                        row['password'],
                        row['active'],
                        confirmed_at)  # Utiliza el objeto datetime aquí
            session.add(user)
            session.commit()
            session.close()
    elif filename_masc=='user_roles':
        for index, row in articles.iterrows():
            logger.info('Cargando el user_role con uid: {} en la BD'.format(row['userId']))
            user_roles = UserRoles(
                        row['userId'],
                        row['roleId'],)  
            session.add(user_roles)
            session.commit()
            session.close()
    elif filename_masc=='productos':
        for index, row in articles.iterrows():
            logger.info('Cargando el producto con uid: {} en la BD'.format(row['id_producto']))
            producto = Productos(
                        row['nombre'],
                        row['descripcion'],
                        row['precio_venta'],
                        row['cantidad_disponible'],
                        row['valoracionT'],
                        row['valoracionC'],
                        row['estatus'],
                        row['imagen'],)  
            session.add(producto)
            session.commit()
            session.close()
    elif filename_masc=='proveedores':
        for index, row in articles.iterrows():
            logger.info('Cargando el proveedor con uid: {} en la BD'.format(row['id_proveedor']))
            proveedor = Proveedores(
                        row['nombre_empresa'],
                        row['nombre_contacto'],
                        row['correo_electronico'],
                        row['telefono'],
                        row['direccion'],
                        row['Active'],)  
            session.add(proveedor)
            session.commit()
            session.close()
    elif filename_masc=='materias_primas':
        for index, row in articles.iterrows():
            logger.info('Cargando la materia_prima con uid: {} en la BD'.format(row['id_materia_prima']))
            materia_prima = Materias_Primas(
                        row['id_proveedor'],
                        row['nombre'],
                        row['unidad_medida'],
                        row['cantidad_minima_requerida'],
                        row['precio_compra'],
                        row['Active'],)  
            session.add(materia_prima)
            session.commit()
            session.close()
    elif filename_masc=='receta':
        for index, row in articles.iterrows():
            logger.info('Cargando la receta con uid: {} en la BD'.format(row['id_receta']))
            receta = Receta(
                        row['id_materia_prima'],
                        row['id_producto'],
                        row['cantidad_requerida'])  
            session.add(receta)
            session.commit()
            session.close()
    elif filename_masc=='ventas':
        for index, row in articles.iterrows():
            logger.info('Cargando la venta con uid: {} en la BD'.format(row['id_venta']))
            # Convierte la cadena a un objeto datetime antes de insertarlo en la BD
            fecha_hora_venta = datetime.strptime(row['fecha_hora_venta'], '%Y-%m-%d %H:%M:%S')
            venta = Ventas(
                        row['id_usuario'],
                        row['precio_total'],
                        fecha_hora_venta)  
            session.add(venta)
            session.commit()
            session.close()
    elif filename_masc=='pedidos':
        for index, row in articles.iterrows():
            logger.info('Cargando el pedido con uid: {} en la BD'.format(row['id_pedido']))
            # Convierte la cadena a un objeto datetime antes de insertarlo en la BD
            fecha_hora_pedido = datetime.strptime(row['fecha_hora_pedido'], '%Y-%m-%d %H:%M:%S')
            fecha_hora_entrega = datetime.strptime(row['fecha_hora_entrega'], '%Y-%m-%d %H:%M:%S')
            pedido = Pedidos(
                        row['id_usuario'],
                        row['estado_pedido'],
                        fecha_hora_pedido,
                        row['domicilio'],
                        row['empleado'],
                        fecha_hora_entrega)  
            session.add(pedido)
            session.commit()
            session.close()
    elif filename_masc=='pedidos_productos':
        for index, row in articles.iterrows():
            logger.info('Cargando el pedido_productos con uid: {} en la BD'.format(row['id_pedido']))
            PedidoProducto = PedidosProductos(
                        row['id_pedido'],
                        row['id_producto'],
                        row['cantidad'],)  
            session.add(PedidoProducto)
            session.commit()
            session.close()
    elif filename_masc=='inventario':
        for index, row in articles.iterrows():
            logger.info('Cargando el inventario con uid: {} en la BD'.format(row['id_inventario']))
            inventario = Inventario(
                        row['id_materia_prima'],
                        row['cantidad_almacenada'],)  
            session.add(inventario)
            session.commit()
            session.close()
    elif filename_masc=='compras':
        for index, row in articles.iterrows():
            logger.info('Cargando la compras con uid: {} en la BD'.format(row['id_compra']))
            # Convierte la cadena a un objeto datetime antes de insertarlo en la BD
            fecha_compra = datetime.strptime(row['fecha_compra'], '%Y-%m-%d %H:%M:%S')
            compra = Compras(
                        row['id_usuario'],
                        row['id_materia_prima'],
                        row['cantidad_comprada'],
                        fecha_compra)  
            session.add(compra)
            session.commit()
            session.close()
    elif filename_masc=='merma':
        for index, row in articles.iterrows():
            logger.info('Cargando la merma con uid: {} en la BD'.format(row['id_perecedero']))
            # Convierte la cadena a un objeto datetime antes de insertarlo en la BD
            fecha_registro = datetime.strptime(row['fecha_registro'], '%Y-%m-%d %H:%M:%S')
            merma = Merma(
                        row['id_producto'],
                        row['cantidad_perdida'],
                        fecha_registro,
                        row['descripcion'],)  
            session.add(merma)
            session.commit()
            session.close()
    

if __name__ == '__main__':
    #Creamos el parser de argumentos
    parser=argparse.ArgumentParser()

    #Creamos un argumento obligatorio
    parser.add_argument('filename',help='El archivo que deseas cargar hacia la BD',type=str)
    args=parser.parse_args()
    main(args.filename)