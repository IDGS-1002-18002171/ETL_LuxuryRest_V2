import yaml

#Definimos una variable global para la configracion
__config = None
#Metodo para verificar y cargar la configuracion
def config():
    global __config
    if not __config:
        #Abrir el archivo yaml
        with open('config.yaml',mode='r') as f:
            __config = yaml.full_load(f)
    return __config