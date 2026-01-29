import json
import os
from datetime import datetime


COMENTARIOS_FILE = 'comentarios_consecutivos.json'


def cargar_comentarios():
    """Carga los comentarios desde el archivo JSON"""
    if not os.path.exists(COMENTARIOS_FILE):
        return {'comentarios': []}
    
    try:
        with open(COMENTARIOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'comentarios': []}


def guardar_comentarios(datos):
    """Guarda los comentarios en el archivo JSON"""
    with open(COMENTARIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def agregar_comentario_consecutivo(usuario, prefijo, desde, hasta, salto, comentario):
    """
    Agrega un nuevo comentario sobre un salto de consecutivo
    
    Args:
        usuario: Nombre del usuario que deja el comentario
        prefijo: Prefijo del documento (FEV, NCE, etc.)
        desde: Número del documento anterior
        hasta: Número del documento siguiente
        salto: Cantidad de documentos que faltan
        comentario: Texto del comentario
    """
    datos = cargar_comentarios()
    
    nuevo_comentario = {
        'id': len(datos['comentarios']) + 1,
        'usuario': usuario,
        'prefijo': prefijo,
        'desde': desde,
        'hasta': hasta,
        'salto': salto,
        'comentario': comentario,
        'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'timestamp': datetime.now().isoformat()
    }
    
    datos['comentarios'].append(nuevo_comentario)
    guardar_comentarios(datos)
    
    return nuevo_comentario


def obtener_comentarios_por_salto(prefijo, desde, hasta):
    """Obtiene todos los comentarios para un salto específico"""
    datos = cargar_comentarios()
    
    comentarios = [
        c for c in datos['comentarios'] 
        if c['prefijo'] == prefijo and c['desde'] == desde and c['hasta'] == hasta
    ]
    
    return comentarios


def obtener_todos_comentarios():
    """Obtiene todos los comentarios registrados"""
    datos = cargar_comentarios()
    return datos['comentarios']


def eliminar_comentario(comentario_id):
    """Elimina un comentario específico"""
    datos = cargar_comentarios()
    
    datos['comentarios'] = [
        c for c in datos['comentarios'] 
        if c['id'] != comentario_id
    ]
    
    guardar_comentarios(datos)
