import pandas as pd
from vendedores import obtener_porcentaje_comision, VENDEDORES_CONFIG


def _preparar_ventas(df):
    """
    Normaliza y prepara datos de ventas con cálculo de comisión por fila.
    Retorna un DataFrame con columnas estándar y comisiones calculadas.
    """
    df = df.copy()
    
    # Normalizar nombres de columnas
    columnas_map = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        columnas_map[col] = col_lower
    
    df_temp = df.copy()
    df_temp.columns = [columnas_map[col] for col in df.columns]
    
    # === BUSCAR COLUMNAS CLAVE ===
    
    # 1. Buscar columna DOCUMENTO
    documento_col = None
    for col in df_temp.columns:
        if 'documento' in col and 'identidad' not in col:
            documento_col = col
            break
    
    if documento_col:
        df_temp['tipo_documento'] = df_temp[documento_col].astype(str).str.upper().str.strip()
    else:
        # Si no hay columna documento, asumir que todas son facturas (FEV)
        df_temp['tipo_documento'] = 'FEV'
    
    # 2. Buscar columna VENDEDOR NOMBRE
    vendedor_col = None
    for col in df_temp.columns:
        if 'vendedor' in col and 'nombre' in col:
            vendedor_col = col
            break
    
    # Si no encuentra "vendedor nombre", buscar solo "vendedor"
    if not vendedor_col:
        for col in df_temp.columns:
            if 'vendedor' in col and 'identidad' not in col:
                vendedor_col = col
                break
    
    if not vendedor_col:
        raise ValueError("No se encontró columna de vendedor (debe contener 'vendedor')")
    
    df_temp['vendedor'] = df_temp[vendedor_col].astype(str).str.strip()
    
    # 3. Buscar columna VR. BRUTO
    monto_col = None
    for col in df_temp.columns:
        if 'bruto' in col:
            monto_col = col
            break
    
    if not monto_col:
        raise ValueError("No se encontró columna 'Vr. bruto'")
    
    df_temp['monto'] = pd.to_numeric(df_temp[monto_col], errors='coerce').fillna(0)
    
    # 4. Buscar columna VR. DESCUENTO
    descuento_col = None
    for col in df_temp.columns:
        if 'descuento' in col:
            descuento_col = col
            break
    
    if descuento_col:
        df_temp['descuento'] = pd.to_numeric(df_temp[descuento_col], errors='coerce').fillna(0)
    else:
        df_temp['descuento'] = 0
    
    # 5. Buscar columna NOMBRE CONCEPTO
    concepto_col = None
    for col in df_temp.columns:
        if 'concepto' in col or 'producto' in col:
            concepto_col = col
            break
    
    if concepto_col:
        df_temp['producto'] = df_temp[concepto_col].astype(str).str.upper().str.strip()
    else:
        df_temp['producto'] = ''
    
    # 6. Buscar columna CANTIDAD
    if 'cantidad' not in df_temp.columns:
        df_temp['cantidad'] = 1
    else:
        df_temp['cantidad'] = pd.to_numeric(df_temp['cantidad'], errors='coerce').fillna(1)
    
    # 7. Buscar columna BENEFICIARIO NOMBRE (cliente)
    cliente_col = None
    for col in df_temp.columns:
        if 'beneficiario' in col and 'nombre' in col:
            cliente_col = col
            break
    
    if cliente_col:
        df_temp['cliente'] = df_temp[cliente_col].astype(str).str.strip()
    else:
        df_temp['cliente'] = ''
    
    # 8. Buscar columna BENEFICIARIO IDENTIDAD (cliente ID)
    cliente_id_col = None
    for col in df_temp.columns:
        if 'beneficiario' in col and 'identidad' in col:
            cliente_id_col = col
            break
    
    if cliente_id_col:
        df_temp['cliente_id'] = df_temp[cliente_id_col].astype(str).str.strip()
    else:
        df_temp['cliente_id'] = ''
    
    # === FILTRAR DOCUMENTOS ===
    # EXCLUIR productos con FLETE
    df_temp['es_flete'] = df_temp['producto'].str.contains('FLETE', na=False)
    df_temp = df_temp[~df_temp['es_flete']].copy()
    
    # Identificar tipo de documento
    # FEV, FEP (facturas) y RCE (recibos) -> SUMAN (+)
    # NCE, NCEL (notas crédito) -> RESTAN (-)
    df_temp['es_nota_credito'] = df_temp['tipo_documento'].isin(['NCE', 'NCEL'])
    
    # Calcular SUBTOTAL = Vr. bruto - vr. descuento
    df_temp['subtotal'] = df_temp['monto'] - df_temp['descuento']
    
    # Si es nota de crédito, el subtotal es negativo
    df_temp.loc[df_temp['es_nota_credito'], 'subtotal'] = -df_temp.loc[df_temp['es_nota_credito'], 'subtotal']
    df_temp.loc[df_temp['es_nota_credito'], 'monto'] = -df_temp.loc[df_temp['es_nota_credito'], 'monto']
    df_temp.loc[df_temp['es_nota_credito'], 'descuento'] = -df_temp.loc[df_temp['es_nota_credito'], 'descuento']
    
    # === PRIMERO: CALCULAR TOTAL POR VENDEDOR PARA VERIFICAR UMBRALES ===
    # Agrupar temporalmente para saber el total de cada vendedor
    totales_por_vendedor = df_temp.groupby('vendedor')['subtotal'].sum().to_dict()

    # === CALCULAR COMISIONES ===
    # Obtener porcentaje de comisión según vendedor y TOTAL de ventas (no individual)
    # Usar diccionario para lookup rápido por vendedor
    df_temp['comision_porcentaje'] = 0.0

    # Para cada vendedor, obtener el porcentaje FIJO una sola vez (salvo casos especiales)
    vendedores_unicos = df_temp['vendedor'].unique()

    for vendedor in vendedores_unicos:
        mask_vendedor = df_temp['vendedor'] == vendedor

        # Reglas especiales para NATALIA REYES:
        # - Clientes normales: comisión por tramos según total de ventas normales
        # - Clientes especiales: comisión fija (sumada a la de normales si aplica)
        if vendedor.upper() == 'NATALIA REYES':
            config = None
            for nombre_config, cfg in VENDEDORES_CONFIG.items():
                if nombre_config.upper() == vendedor.upper():
                    config = cfg
                    break

            clientes_especiales = set()
            if config and 'clientes_especiales' in config:
                clientes_especiales = set(config['clientes_especiales'].keys())

            # Identificar ventas de clientes especiales por ID
            cliente_ids = df_temp.loc[mask_vendedor, 'cliente_id'].astype(str).str.strip()
            mask_especial = cliente_ids.isin(clientes_especiales)

            # Total de ventas normales (sin especiales)
            total_normales = df_temp.loc[mask_vendedor & ~mask_especial, 'subtotal'].sum()

            # Porcentaje normal por tramos (sin cliente_id para evitar regla especial)
            porcentaje_normal = obtener_porcentaje_comision(vendedor, total_normales, cliente_id=None)

            # Porcentaje fijo para especiales (si existe configuración)
            porcentaje_especial = None
            if config and 'clientes_especiales' in config and len(clientes_especiales) > 0:
                # Tomar el porcentaje de cualquier cliente especial (todos comparten el mismo valor)
                porcentaje_especial = list(config['clientes_especiales'].values())[0]

            # Aplicar porcentajes por fila
            df_temp.loc[mask_vendedor & ~mask_especial & (df_temp['subtotal'] > 0), 'comision_porcentaje'] = porcentaje_normal
            if porcentaje_especial is not None:
                df_temp.loc[mask_vendedor & mask_especial & (df_temp['subtotal'] > 0), 'comision_porcentaje'] = porcentaje_especial
            df_temp.loc[mask_vendedor & (df_temp['subtotal'] <= 0), 'comision_porcentaje'] = 0

            continue

        # Resto de vendedores: porcentaje único por total de ventas
        total_vendedor = totales_por_vendedor.get(vendedor, 0)
        porcentaje = obtener_porcentaje_comision(vendedor, total_vendedor, cliente_id=None)

        # Aplicar el porcentaje a todas las filas del vendedor (solo si subtotal > 0)
        df_temp.loc[mask_vendedor & (df_temp['subtotal'] > 0), 'comision_porcentaje'] = porcentaje
        df_temp.loc[mask_vendedor & (df_temp['subtotal'] <= 0), 'comision_porcentaje'] = 0

    # Porcentaje por defecto si el vendedor no está configurado
    df_temp['comision_porcentaje'] = df_temp['comision_porcentaje'].fillna(3)
    
    # Calcular monto de comisión (solo sobre subtotales positivos)
    # Las notas de crédito NO generan comisión (subtotal negativo)
    df_temp['monto_comision'] = df_temp.apply(
        lambda row: (row['subtotal'] * row['comision_porcentaje']) / 100 if row['subtotal'] > 0 else 0,
        axis=1
    )

    return df_temp


def calcular_comisiones_ventas(df):
    """
    Calcula comisiones por ventas con tasas personalizadas por vendedor
    
    Estructura esperada del DataFrame:
    - documento: tipo de documento (FEV, FEP=facturas; NCE, NCEL=notas crédito; RCE=recibos)
    - fecha: fecha de la factura
    - vendedor identidad: ID del vendedor
    - vendedor nombre: nombre del vendedor
    - beneficiario identidad: NIT o identificación del cliente
    - beneficiario nombre: nombre del cliente
    - nombre concepto: artículo (EXCLUIR "FLETE" - no suma para comisión)
    - cantidad: cantidad solicitada
    - Vr. bruto: valor del artículo
    - vr. descuento: descuento aplicado al producto
    
    REGLAS:
    - NCE y NCEL (notas crédito) RESTAN de las ventas
    - FEV, FEP (facturas) y RCE (recibos) SUMAN a las ventas
    - Productos con "FLETE" se EXCLUYEN del cálculo
    - Comisión = (Vr. bruto - vr. descuento) * porcentaje según vendedor
    """
    df_temp = _preparar_ventas(df)
    
    # === AGRUPAR POR VENDEDOR ===
    df_resumen = df_temp.groupby('vendedor').agg({
        'monto': 'sum',
        'descuento': 'sum',
        'subtotal': 'sum',
        'cantidad': 'sum',
        'monto_comision': 'sum'
    }).reset_index()
    
    df_resumen.columns = ['vendedor', 'total_bruto', 'total_descuentos',
                          'total_neto', 'total_cantidad', 'comision_total']

    # Porcentaje efectivo de comisión por vendedor
    df_resumen['comision_porcentaje'] = df_resumen.apply(
        lambda row: (row['comision_total'] / row['total_neto'] * 100) if row['total_neto'] > 0 else 0,
        axis=1
    )
    
    # Reordenar columnas
    df_resumen = df_resumen[['vendedor', 'total_bruto', 'total_descuentos',
                             'total_neto', 'total_cantidad', 'comision_total', 'comision_porcentaje']]
    
    df_resumen = df_resumen.round(2)
    
    return df_resumen


def calcular_resumen_clientes_ventas(df):
    """
    Resume ventas por vendedor y cliente con comisiones calculadas.
    """
    df_temp = _preparar_ventas(df)

    df_resumen = df_temp.groupby(['vendedor', 'cliente', 'cliente_id']).agg({
        'monto': 'sum',
        'descuento': 'sum',
        'subtotal': 'sum',
        'cantidad': 'sum',
        'monto_comision': 'sum'
    }).reset_index()

    df_resumen.columns = ['vendedor', 'cliente', 'cliente_id', 'total_bruto', 'total_descuentos',
                          'total_neto', 'total_cantidad', 'comision_total']

    df_resumen['comision_porcentaje'] = df_resumen.apply(
        lambda row: (row['comision_total'] / row['total_neto'] * 100) if row['total_neto'] > 0 else 0,
        axis=1
    )

    df_resumen = df_resumen[['vendedor', 'cliente', 'cliente_id', 'total_bruto', 'total_descuentos',
                             'total_neto', 'total_cantidad', 'comision_total', 'comision_porcentaje']]

    df_resumen = df_resumen.round(2)

    return df_resumen


def calcular_comisiones_recaudos(df):
    """
    Calcula comisiones por recaudos (cobros)
    Solo aplica comisión del 3% para cobros con mora >= 60 días (Jorge Pernia)
    
    Estructura esperada del DataFrame:
    - cobrador: nombre del cobrador
    - monto: monto recaudado
    - fecha: fecha del recaudo
    - dias_mora: días de mora (opcional, requerido para aplicar comisión)
    """
    df = df.copy()
    
    # Normalizar nombres de columnas
    df.columns = df.columns.str.lower().str.strip()
    
    # Verificar si existe columna dias_mora
    if 'dias_mora' not in df.columns:
        df['dias_mora'] = 0  # Por defecto 0 si no se especifica
    
    # Aplicar porcentaje de comisión según el cobrador y monto
    # Solo aplica comisión si dias_mora >= 60
    df['comision_porcentaje'] = df.apply(
        lambda row: obtener_porcentaje_comision(row['cobrador'], row['monto']) 
                    if row.get('dias_mora', 0) >= 60 else 0, 
        axis=1
    )
    
    # Si el cobrador no está en la configuración, usar 0
    df['comision_porcentaje'] = df['comision_porcentaje'].fillna(0)
    
    # Calcular monto de comisión
    df['monto_comision'] = (df['monto'] * df['comision_porcentaje']) / 100
    
    # Agrupar por cobrador
    df_resumen = df.groupby('cobrador').agg({
        'monto': 'sum',
        'monto_comision': 'sum',
        'comision_porcentaje': 'mean'
    }).reset_index()
    
    df_resumen.columns = ['cobrador', 'total_recaudado', 'comision_total', 'comision_promedio']
    df_resumen = df_resumen.round(2)
    
    return df_resumen

def verificar_consecutivos_facturas(df):
    """
    Verifica si hay saltos en los consecutivos de facturas.
    Retorna una lista de alertas si encuentra saltos menores a 50.
    
    Un salto se considera crítico si es menor a 50 (es decir, faltan menos de 50 facturas).
    Por ejemplo:
    - FEV00100 -> FEV00151: salto de 51, NO genera alerta
    - FEV00100 -> FEV00150: salto de 50, SÍ genera alerta
    """
    import re
    
    alertas = []
    
    # Buscar columna documento
    documento_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'documento' in col_lower and 'identidad' not in col_lower:
            documento_col = col
            break
    
    if documento_col is None:
        return alertas  # Si no hay columna documento, no hay alertas
    
    # Convertir a string y limpiar
    df_temp = df.copy()
    df_temp['numero_documento'] = df_temp[documento_col].astype(str).str.upper().str.strip()
    
    # Agrupar por prefijo (letras) para cada documento
    # Estructura esperada: FEV00100, NCE00050, etc.
    documentos_agrupados = {}
    
    for doc in df_temp['numero_documento'].unique():
        if pd.isna(doc) or doc == '':
            continue
        
        # Extraer prefijo (letras) y número
        match = re.match(r'^([A-Z]+)(\d+)$', str(doc).strip())
        if match:
            prefijo = match.group(1)
            numero = int(match.group(2))
            
            if prefijo not in documentos_agrupados:
                documentos_agrupados[prefijo] = []
            
            documentos_agrupados[prefijo].append(numero)
    
    # Verificar saltos para cada prefijo
    for prefijo, numeros in documentos_agrupados.items():
        # Ordenar números
        numeros_ordenados = sorted(set(numeros))  # Eliminar duplicados y ordenar
        
        if len(numeros_ordenados) < 2:
            continue  # No hay saltos si hay solo un número
        
        # Verificar saltos consecutivos
        for i in range(len(numeros_ordenados) - 1):
            numero_actual = numeros_ordenados[i]
            numero_siguiente = numeros_ordenados[i + 1]
            salto = numero_siguiente - numero_actual
            
            # Si el salto es menor o igual a 50, generar alerta
            # Salto de 51 = faltan 50 facturas (NO alerta)
            # Salto de 50 = faltan 49 facturas (SÍ alerta)
            if 1 < salto <= 50:
                numero_actual_formateado = f"{prefijo}{numero_actual:05d}"
                numero_siguiente_formateado = f"{prefijo}{numero_siguiente:05d}"
                alerta = {
                    'tipo': 'advertencia',
                    'mensaje': f'Salto detectado en consecutivos: {numero_actual_formateado} → {numero_siguiente_formateado} (faltan {salto - 1} facturas)',
                    'prefijo': prefijo,
                    'desde': numero_actual,
                    'hasta': numero_siguiente,
                    'salto': salto
                }
                alertas.append(alerta)
    
    return alertas