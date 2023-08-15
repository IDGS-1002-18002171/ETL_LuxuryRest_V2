from base import Base
from sqlalchemy import Column, String, Integer, Date, DECIMAL

class Users(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario = Column(String(100), nullable=False)
    cantidad_ventas = Column(Integer, nullable=False)

    def __init__(self, usuario, cantidad_ventas):
        self.usuario = usuario
        self.cantidad_ventas = cantidad_ventas

class Compras(Base):
    __tablename__ = 'Compras'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    total_compras = Column(DECIMAL(10, 2), nullable=False)

    def __init__(self, fecha, total_compras):
        self.fecha = fecha
        self.total_compras = total_compras

class Materias_Primas(Base):
    __tablename__ = 'Materias_Primas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    materia_prima = Column(String(50), nullable=False)
    unidad_medida = Column(String(50), nullable=False)
    cantidad_minima_requerida = Column(DECIMAL(10, 2), nullable=False)
    cantidad_en_inventario = Column(DECIMAL(10, 2), nullable=False)

    def __init__(self, materia_prima, unidad_medida, cantidad_minima_requerida, cantidad_en_inventario):
        self.materia_prima = materia_prima
        self.unidad_medida = unidad_medida
        self.cantidad_minima_requerida = cantidad_minima_requerida
        self.cantidad_en_inventario = cantidad_en_inventario

class Productos(Base):
    __tablename__ = 'Productos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto = Column(String(50), nullable=False)
    cantidad_disponible = Column(Integer, nullable=False)
    valoracion = Column(DECIMAL(10, 2), nullable=False)
    
    def __init__(self, producto, cantidad_disponible, valoracion):
        self.producto = producto
        self.cantidad_disponible = cantidad_disponible
        self.valoracion = valoracion

class Ventas(Base):
    __tablename__ = 'Ventas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto = Column(String(50), nullable=False)
    fecha = Column(Date, nullable=False)
    cantidad_vendida = Column(Integer, nullable=False)
    precio_venta = Column(DECIMAL(10, 2), nullable=False)
    total_venta = Column(DECIMAL(10, 2), nullable=False)

    def __init__(self, producto, fecha, cantidad_vendida, precio_venta, total_venta):
        self.producto = producto
        self.fecha = fecha
        self.cantidad_vendida = cantidad_vendida
        self.precio_venta = precio_venta
        self.total_venta = total_venta
