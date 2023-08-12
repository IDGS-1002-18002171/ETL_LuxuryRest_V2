from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, ForeignKey, Date, Float, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from load.base import Base
from sqlalchemy.ext.declarative import declarative_base


# Definimos la clase User que define la entidad de BD
class User(Base):
    __tablename__ = 'User'

    # Definicion de Columnas
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    active = Column(Integer)
    confirmed_at = Column(DateTime)

    # Definimos la relación con la tabla UserRoles
    roles = relationship("User_Roles", back_populates="user")
    # Relación uno a muchos con Pedidos
    pedidos = relationship("Pedidos", foreign_keys="[Pedidos.id_usuario]", back_populates="user")



    def __init__(self, id, name, email, password, active=None, confirmed_at=None):
        self.id=id
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.confirmed_at = confirmed_at

# Definimos la clase Role que define la entidad de BD
class Role(Base):
    __tablename__ = 'Role'

    # Definicion de Columnas
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255))

    def __init__(self, id, name, description):
        self.id=id
        self.name = name
        self.description = description

# Definimos la clase UserRoles que define la entidad de BD
class User_Roles(Base):
    __tablename__ = 'User_Roles'
    userId = Column(Integer, ForeignKey('User.id'), primary_key=True)
    roleId = Column(Integer, ForeignKey('Role.id'), nullable=True)

    # Definimos la relación con la tabla User
    user = relationship("User", back_populates="roles")

    def __init__(self, userId, roleId):
        self.userId = userId
        self.roleId = roleId

# Definimos la clase Productos que define la entidad de BD
class Productos(Base):
    __tablename__ = 'Productos'

    # Definicion de Columnas
    id_producto = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(String(255), nullable=False)
    imagen = Column(String)
    precio_venta = Column(DECIMAL(10, 2), nullable=False)
    cantidad_disponible = Column(Integer, nullable=False)
    valoracionT = Column(Integer)
    valoracionC = Column(Integer)
    estatus = Column(Integer, nullable=False)

    recetas = relationship("Receta", foreign_keys="[Receta.id_producto]", back_populates="producto")
    pedidos = relationship("Pedidos_Productos", back_populates="producto")  # Change "pedido" to "producto"
    
    def __init__(self, nombre, descripcion, precio_venta, cantidad_disponible, valoracionT=None, valoracionC=None, estatus=None, imagen=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio_venta = precio_venta
        self.cantidad_disponible = cantidad_disponible
        self.valoracionT = valoracionT
        self.valoracionC = valoracionC
        self.estatus = estatus
        self.imagen = imagen
# Definimos la clase Proveedores que define la entidad de BD
class Proveedores(Base):
    __tablename__ = 'Proveedores'

    # Definicion de Columnas
    id_proveedor = Column(Integer, primary_key=True)
    nombre_empresa = Column(String(50), nullable=False)
    nombre_contacto = Column(String(50), nullable=False)
    correo_electronico = Column(String(50), nullable=False)
    telefono = Column(String(20), nullable=False)
    direccion = Column(String(255), nullable=False)
    Activo = Column(Integer, nullable=False)

    def __init__(self, nombre_empresa, nombre_contacto, correo_electronico, telefono, direccion, Activo):
        self.nombre_empresa = nombre_empresa
        self.nombre_contacto = nombre_contacto
        self.correo_electronico = correo_electronico
        self.telefono = telefono
        self.direccion = direccion
        self.Activo = Activo

# Definimos la clase Materias_Primas que define la entidad de BD
class Materias_Primas(Base):
    __tablename__ = 'Materias_Primas'

    # Definicion de Columnas
    id_materia_prima = Column(Integer, primary_key=True)
    id_proveedor = Column(Integer, ForeignKey('Proveedores.id_proveedor'), nullable=False)
    nombre = Column(String(50), nullable=False)
    unidad_medida = Column(String(20), nullable=False)
    cantidad_minima_requerida = Column(DECIMAL(10, 2), nullable=False)
    precio_compra = Column(Float, nullable=False)
    Activo = Column(Integer, nullable=False)

    # Definimos la relación con la tabla Proveedores
    proveedor = relationship("Proveedores")

    def __init__(self, id_proveedor, nombre, unidad_medida, cantidad_minima_requerida, precio_compra, Activo):
        self.id_proveedor = id_proveedor
        self.nombre = nombre
        self.unidad_medida = unidad_medida
        self.cantidad_minima_requerida = cantidad_minima_requerida
        self.precio_compra = precio_compra
        self.Activo = Activo

# Definimos la clase Receta que define la entidad de BD
class Receta(Base):
    __tablename__ = 'Receta'

    # Definicion de Columnas
    id_receta = Column(Integer, primary_key=True)
    id_materia_prima = Column(Integer, ForeignKey('Materias_Primas.id_materia_prima'), nullable=False)
    id_producto = Column(Integer, ForeignKey('Productos.id_producto'), nullable=False)
    cantidad_requerida = Column(DECIMAL(12, 5), nullable=False)

    # Definimos las relaciones con las tablas Materias_Primas y Productos
    materia_prima = relationship("Materias_Primas")
    producto = relationship("Productos")

    def __init__(self, id_materia_prima, id_producto, cantidad_requerida):
        self.id_materia_prima = id_materia_prima
        self.id_producto = id_producto
        self.cantidad_requerida = cantidad_requerida
# Definimos la clase Ventas que define la entidad de BD
class Ventas(Base):
    __tablename__ = 'Ventas'

    # Definicion de Columnas
    id_venta = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('User.id'), nullable=False)
    precio_total = Column(Float, nullable=False)
    fecha_hora_venta = Column(DateTime, nullable=False)

    # Definimos la relación con la tabla User
    user = relationship("User")

    def __init__(self, id_usuario, precio_total, fecha_hora_venta):
        self.id_usuario = id_usuario
        self.precio_total = precio_total
        self.fecha_hora_venta = fecha_hora_venta

# Definimos la clase Pedidos que define la entidad de BD
class Pedidos(Base):
    __tablename__ = 'Pedidos'
    __table_args__ = {'extend_existing': True}

    # Definicion de Columnas
    id_pedido = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('User.id'), nullable=False)
    estado_pedido = Column(Integer, nullable=False)
    fecha_hora_pedido = Column(DateTime, nullable=False)
    domicilio = Column(String(70))
    empleado = Column(Integer, ForeignKey('User.id'))
    fecha_hora_entrega = Column(DateTime)

    # Definimos las relaciones con la tabla User
    user_empleado = relationship("User", foreign_keys=[empleado])
    user = relationship("User", foreign_keys=[id_usuario], back_populates="pedidos")

    # Relación con la tabla PedidosProductos
    productos = relationship("Pedidos_Productos", back_populates="pedido")

    def __init__(self, id_usuario, estado_pedido, fecha_hora_pedido, domicilio=None, empleado=None, fecha_hora_entrega=None):
        self.id_usuario = id_usuario
        self.estado_pedido = estado_pedido
        self.fecha_hora_pedido = fecha_hora_pedido
        self.domicilio = domicilio
        self.empleado = empleado
        self.fecha_hora_entrega = fecha_hora_entrega

# Definimos la clase Pedidos_Productos que define la entidad de BD
class Pedidos_Productos(Base):
    __tablename__ = 'Pedidos_Productos'

    id_pedido = Column(Integer, ForeignKey('Pedidos.id_pedido'), nullable=False)
    id_producto = Column(Integer, ForeignKey('Productos.id_producto'), nullable=False)
    cantidad = Column(Integer, nullable=False)

    # Define la relación con la tabla Pedidos (opcional, solo si quieres acceder a los pedidos desde esta tabla)
    pedido = relationship("Pedidos", back_populates="productos")

    # Define la relación con la tabla Productos (opcional, solo si quieres acceder a los productos desde esta tabla)
    producto = relationship("Productos", back_populates="pedidos")  

    # Definir la clave primaria compuesta
    __table_args__ = (
        PrimaryKeyConstraint('id_pedido', 'id_producto'),
    )

    def __init__(self, id_pedido, id_producto, cantidad):
        self.id_pedido = id_pedido
        self.id_producto = id_producto
        self.cantidad = cantidad


# Definimos la clase Inventario que define la entidad de BD
class Inventario(Base):
    __tablename__ = 'Inventario'

    # Definicion de Columnas
    id_inventario = Column(Integer, primary_key=True)
    id_materia_prima = Column(Integer, ForeignKey('Materias_Primas.id_materia_prima'), nullable=False)
    cantidad_almacenada = Column(DECIMAL(15, 5), nullable=False)

    # Definimos la relación con la tabla Materias_Primas
    materia_prima = relationship("Materias_Primas")

    def __init__(self, id_materia_prima, cantidad_almacenada):
        self.id_materia_prima = id_materia_prima
        self.cantidad_almacenada = cantidad_almacenada

# Definimos la clase Compras que define la entidad de BD
class Compras(Base):
    __tablename__ = 'Compras'

    # Definicion de Columnas
    id_compra = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('User.id'), nullable=False)
    id_materia_prima = Column(Integer, ForeignKey('Materias_Primas.id_materia_prima'), nullable=False)
    cantidad_comprada = Column(Integer, nullable=False)
    fecha_compra = Column(DateTime, nullable=False)

    # Definimos las relaciones con las tablas User y Materias_Primas
    user = relationship("User")
    materia_prima = relationship("Materias_Primas")

    def __init__(self, id_usuario, id_materia_prima, cantidad_comprada, fecha_compra):
        self.id_usuario = id_usuario
        self.id_materia_prima = id_materia_prima
        self.cantidad_comprada = cantidad_comprada
        self.fecha_compra = fecha_compra

# Definimos la clase Merma que define la entidad de BD
class Merma(Base):
    __tablename__ = 'Merma'

    # Definicion de Columnas
    id_Merma = Column(Integer, primary_key=True)
    id_producto = Column(Integer, ForeignKey('Productos.id_producto'), nullable=False)
    descripcion = Column(String(50))
    cantidad_perdida = Column(DECIMAL(12, 5), nullable=False)
    fecha_registro = Column(Date, nullable=False)

    # Definimos la relación con la tabla Productos
    producto = relationship("Productos")

    def __init__(self, id_producto, cantidad_perdida, fecha_registro, descripcion=None):
        self.id_producto = id_producto
        self.descripcion = descripcion
        self.cantidad_perdida = cantidad_perdida
        self.fecha_registro = fecha_registro