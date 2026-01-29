import json
import os
from datetime import datetime

HISTORIAL_FILE = 'historial_reportes.json'

def inicializar_historial():
    """Inicializa el archivo de historial si no existe"""
    if not os.path.exists(HISTORIAL_FILE):
        historial = {
            'reportes': [],
            'fecha_creacion': datetime.now().isoformat()
        }
        guardar_historial(historial)
    return cargar_historial()

def cargar_historial():
    """Carga el historial de reportes"""
    try:
        with open(HISTORIAL_FILE, 'r') as f:
            return json.load(f)
    except:
        return inicializar_historial()

def guardar_historial(historial):
    """Guarda el historial"""
    with open(HISTORIAL_FILE, 'w') as f:
        json.dump(historial, f, indent=2, ensure_ascii=False)

def agregar_reporte(tipo, consecutivo, archivo, usuario='admin'):
    """Agrega un nuevo reporte al historial"""
    historial = cargar_historial()
    
    nuevo_reporte = {
        'id': len(historial['reportes']) + 1,
        'tipo': tipo,  # 'ventas' o 'recaudos'
        'consecutivo': consecutivo,
        'archivo': archivo,
        'usuario': usuario,
        'fecha': datetime.now().isoformat(),
        'descargado': False
    }
    
    historial['reportes'].append(nuevo_reporte)
    guardar_historial(historial)
    
    return nuevo_reporte

def obtener_reportes(tipo=None):
    """Obtiene reportes del historial, opcionalmente filtrados por tipo"""
    historial = cargar_historial()
    reportes = historial.get('reportes', [])
    
    if tipo:
        reportes = [r for r in reportes if r['tipo'] == tipo]
    
    # Ordenar por fecha descendente
    reportes.sort(key=lambda x: x['fecha'], reverse=True)
    
    return reportes

def marcar_descargado(reporte_id):
    """Marca un reporte como descargado"""
    historial = cargar_historial()
    
    for reporte in historial['reportes']:
        if reporte['id'] == reporte_id:
            reporte['descargado'] = True
            break
    
    guardar_historial(historial)

def eliminar_reporte(reporte_id):
    """Elimina un reporte del historial"""
    historial = cargar_historial()
    historial['reportes'] = [r for r in historial['reportes'] if r['id'] != reporte_id]
    guardar_historial(historial)
