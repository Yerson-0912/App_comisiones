"""
Configuración de vendedores y sus estructuras de comisión
"""

VENDEDORES_CONFIG = {
    'KAREN TORRADO': {
        'nombre': 'KAREN TORRADO',
        'tramos_comision': [
            {
                'desde': 0,
                'hasta': 199999999,
                'porcentaje': 1.5,
                'descripcion': 'De 0 a 199,999,999'
            },
            {
                'desde': 200000000,
                'hasta': 249999999,
                'porcentaje': 2,
                'descripcion': 'De 200,000,000 a 249,999,999'
            },
            {
                'desde': 250000000,
                'hasta': 300000000,
                'porcentaje': 2.5,
                'descripcion': 'De 250,000,000 a 300,000,000'
            },
            {
                'desde': 300000001,
                'hasta': float('inf'),
                'porcentaje': 2.5,
                'descripcion': 'Más de 300,000,000'
            }
        ],
        'tiene_descuento_mensual': True,
        'descuento_mensual': 950000
    },
    'NATALIA REYES': {
        'nombre': 'NATALIA REYES',
        'tramos_comision': [
            {
                'desde': 0,
                'hasta': 5000000,
                'porcentaje': 0,
                'descripcion': 'Hasta 5,000,000'
            },
            {
                'desde': 5000001,
                'hasta': 10000000,
                'porcentaje': 2,
                'descripcion': 'De 5,000,001 a 10,000,000'
            },
            {
                'desde': 10000001,
                'hasta': 20000000,
                'porcentaje': 3,
                'descripcion': 'De 10,000,001 a 20,000,000'
            },
            {
                'desde': 20000001,
                'hasta': 30000000,
                'porcentaje': 4,
                'descripcion': 'De 20,000,001 a 30,000,000'
            },
            {
                'desde': 30000001,
                'hasta': float('inf'),
                'porcentaje': 5,
                'descripcion': 'De 30,000,001 en adelante'
            }
        ],
        'clientes_especiales': {
            '900429730': 2,  # GRUPO OPTICO S.A.S (todas sus sedes)
            '830027558': 2,  # IMEVI S.A.S
            '901789148': 2,  # OPTICA SOL Y GAFAS DR COL S.A.S
            '901807613': 2,  # OPTICAS SOL Y GAFAS S.A.S
            '91287282': 2,   # RUEDA MAYORGA JORGE (todas sus sedes)
            '37837035': 2,   # RUEDA MOLINA LUZ MARINA
            '1098771591': 2, # RUEDA SANCHEZ DANIELA STEPHANIA
            '900431956': 2,  # UMI SALUD VISUAL S.A.S
            '830094312': 2,  # VISUAL POINT S.A.S
            '900628197': 2   # VISUALDENT SALUD S.A.S
        },
        'tiene_retencion': True,
        'porcentaje_retencion': 4
    },
    'JOSE ALFREDO FAJARDO': {
        'nombre': 'JOSE ALFREDO FAJARDO',
        'tramos_comision': [
            {
                'desde': 0,
                'hasta': 74999999,
                'porcentaje': 0,
                'descripcion': 'De 0 a 74,999,999'
            },
            {
                'desde': 75000000,
                'hasta': float('inf'),
                'porcentaje': 2,
                'descripcion': 'De 75,000,000 en adelante'
            }
        ]
    },
    'JHONATAN VASQUEZ': {
        'nombre': 'JHONATAN VASQUEZ',
        'tramos_comision': [
            {
                'desde': 0,
                'hasta': 74999999,
                'porcentaje': 0,
                'descripcion': 'De 0 a 74,999,999'
            },
            {
                'desde': 75000000,
                'hasta': float('inf'),
                'porcentaje': 2,
                'descripcion': 'De 75,000,000 en adelante'
            }
        ]
    },
    'JONATHAN VASQUEZ': {
        'nombre': 'JONATHAN VASQUEZ',
        'tramos_comision': [
            {
                'desde': 0,
                'hasta': 74999999,
                'porcentaje': 0,
                'descripcion': 'De 0 a 74,999,999'
            },
            {
                'desde': 75000000,
                'hasta': float('inf'),
                'porcentaje': 2,
                'descripcion': 'De 75,000,000 en adelante'
            }
        ]
    },
    'JORGE PERNIA': {
        'nombre': 'JORGE PERNIA',
        'tramos_comision': [
            {
                'desde': 0,
                'hasta': 94999999,
                'porcentaje': 0,
                'descripcion': 'De 0 a 94,999,999'
            },
            {
                'desde': 95000000,
                'hasta': float('inf'),
                'porcentaje': 3,
                'descripcion': 'De 95,000,000 en adelante'
            }
        ]
    }
}


def obtener_porcentaje_comision(vendedor, monto, cliente_nombre=None, cliente_id=None):
    """
    Obtiene el porcentaje de comisión según el vendedor, monto y cliente
    
    Args:
        vendedor: Nombre del vendedor
        monto: Monto de la venta
        cliente_nombre: Nombre del cliente (opcional, para clientes especiales)
        cliente_id: ID del cliente (opcional, para clientes especiales)
        
    Returns:
        Porcentaje de comisión o None si no existe configuración
    """
    # Buscar vendedor (case-insensitive)
    for nombre_config, config in VENDEDORES_CONFIG.items():
        if vendedor.upper() == nombre_config.upper():
            # Verificar clientes especiales primero (por ID para NATALIA REYES)
            if cliente_id and 'clientes_especiales' in config:
                cliente_id_str = str(cliente_id).strip()
                if cliente_id_str in config['clientes_especiales']:
                    return config['clientes_especiales'][cliente_id_str]
            
            # Buscar en tramos normales de comisión por ventas
            tramos = config.get('tramos_comision', [])
            for tramo in tramos:
                if tramo['desde'] <= monto <= tramo['hasta']:
                    return tramo['porcentaje']
            
            return None
    
    return None


def calcular_comision_vendedor(vendedor, monto_total, cliente_nombre=None, cliente_id=None):
    """
    Calcula la comisión total para un vendedor
    
    Args:
        vendedor: Nombre del vendedor
        monto_total: Monto total de ventas
        cliente_nombre: Nombre del cliente (opcional)
        cliente_id: ID del cliente (opcional)
        
    Returns:
        Dict con detalles de la comisión
    """
    porcentaje = obtener_porcentaje_comision(vendedor, monto_total, cliente_nombre, cliente_id)
    
    if porcentaje is None:
        return None
    
    comision_bruta = monto_total * (porcentaje / 100)
    
    # Buscar configuración del vendedor
    config = None
    for nombre_config, cfg in VENDEDORES_CONFIG.items():
        if vendedor.upper() == nombre_config.upper():
            config = cfg
            break
    
    resultado = {
        'vendedor': vendedor,
        'monto_venta': monto_total,
        'porcentaje': porcentaje,
        'comision_bruta': comision_bruta,
        'descuento_mensual': 0,
        'retencion': 0,
        'comision_neta': comision_bruta
    }
    
    # Aplicar descuento mensual si aplica
    if config and config.get('tiene_descuento_mensual'):
        descuento = config.get('descuento_mensual', 0)
        resultado['descuento_mensual'] = descuento
        resultado['comision_neta'] -= descuento
    
    # Aplicar retención si aplica
    if config and config.get('tiene_retencion'):
        porcentaje_retencion = config.get('porcentaje_retencion', 0)
        retencion = comision_bruta * (porcentaje_retencion / 100)
        resultado['retencion'] = retencion
        resultado['comision_neta'] -= retencion
    
    return resultado
