import json
import os
from datetime import datetime

CONTADOR_FILE = 'contador.json'

def inicializar_contador():
    """Inicializa el archivo de contador si no existe"""
    if not os.path.exists(CONTADOR_FILE):
        contador = {
            'ventas': 1,
            'recaudos': 1,
            'fecha_creacion': datetime.now().isoformat()
        }
        guardar_contador(contador)
    return cargar_contador()

def cargar_contador():
    """Carga el contador actual"""
    try:
        with open(CONTADOR_FILE, 'r') as f:
            return json.load(f)
    except:
        return inicializar_contador()

def guardar_contador(contador):
    """Guarda el contador"""
    with open(CONTADOR_FILE, 'w') as f:
        json.dump(contador, f, indent=2)

def obtener_siguiente_consecutivo(tipo):
    """Obtiene el siguiente consecutivo y lo incrementa"""
    contador = cargar_contador()
    
    if tipo not in contador:
        contador[tipo] = 1
    
    actual = contador[tipo]
    contador[tipo] += 1
    guardar_contador(contador)
    
    return actual

def obtener_consecutivo_formateado(tipo):
    """Obtiene el consecutivo con formato: TIPO-000001"""
    num = obtener_siguiente_consecutivo(tipo)
    tipo_formato = tipo.upper()[:3]
    return f"{tipo_formato}-{num:06d}"
