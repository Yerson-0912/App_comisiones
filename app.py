from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
import pandas as pd
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from comisiones import calcular_comisiones_ventas, calcular_comisiones_recaudos, calcular_resumen_clientes_ventas, verificar_consecutivos_facturas
from contador import obtener_consecutivo_formateado
from historial import agregar_reporte, obtener_reportes
from usuarios import autenticar_usuario, obtener_usuario_por_username, obtener_todos_usuarios, crear_usuario, cambiar_contraseña, generar_token_recuperacion, resetear_contraseña_con_token, obtener_usuario_por_email
from emails import enviar_email_recuperacion
from comentarios import agregar_comentario_consecutivo
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Credenciales de acceso (cámbialas antes de entregar)
app.config['APP_USERNAME'] = 'admin'
app.config['APP_PASSWORD'] = 'admin123'

# Crear carpetas si no existen
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'ventas'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'recaudos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'reportes'), exist_ok=True)
os.makedirs('EXCEL__/COMISIONES', exist_ok=True)


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.path))
        return view_func(*args, **kwargs)
    return wrapper


@app.context_processor
def inject_auth_state():
    return {
        'logged_in': session.get('logged_in', False),
        'username_actual': session.get('username', ''),
        'es_admin': session.get('es_admin', False)
    }

def generar_excel_ventas(df_comisiones, consecutivo):
    """Genera un archivo Excel formateado para ventas"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja de resumen
        df_comisiones.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Aplicar formato
        worksheet = writer.sheets['Resumen']
        worksheet.column_dimensions['A'].width = 20
        worksheet.column_dimensions['B'].width = 15
        worksheet.column_dimensions['C'].width = 15
        worksheet.column_dimensions['D'].width = 15
        worksheet.column_dimensions['E'].width = 15
    
    output.seek(0)
    return output


def generar_excel_ventas_clientes(df_clientes, consecutivo):
    """Genera un archivo Excel formateado para ventas por cliente"""
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_clientes.to_excel(writer, sheet_name='Resumen', index=False)

        worksheet = writer.sheets['Resumen']
        worksheet.column_dimensions['A'].width = 20
        worksheet.column_dimensions['B'].width = 30
        worksheet.column_dimensions['C'].width = 18
        worksheet.column_dimensions['D'].width = 15
        worksheet.column_dimensions['E'].width = 15
        worksheet.column_dimensions['F'].width = 15
        worksheet.column_dimensions['G'].width = 15
        worksheet.column_dimensions['H'].width = 15
        worksheet.column_dimensions['I'].width = 15

    output.seek(0)
    return output

def generar_excel_recaudos(df_comisiones, consecutivo):
    """Genera un archivo Excel formateado para recaudos"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja de resumen
        df_comisiones.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Aplicar formato
        worksheet = writer.sheets['Resumen']
        worksheet.column_dimensions['A'].width = 20
        worksheet.column_dimensions['B'].width = 15
        worksheet.column_dimensions['C'].width = 15
        worksheet.column_dimensions['D'].width = 15
    
    output.seek(0)
    return output

@app.route('/')
@login_required
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        usuario = autenticar_usuario(username, password)
        if usuario:
            session['logged_in'] = True
            session['username'] = usuario['username']
            session['es_admin'] = usuario['es_admin']
            next_url = request.args.get('next') or url_for('index')
            return redirect(next_url)

        flash('Usuario o contraseña incorrectos', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get('es_admin', False):
            flash('Solo administradores pueden acceder', 'error')
            return redirect(url_for('index'))
        return view_func(*args, **kwargs)
    return wrapper


@app.route('/configuracion')
@admin_required
def configuracion():
    """Panel de configuración y administración de usuarios"""
    usuarios = obtener_todos_usuarios()
    return render_template('configuracion.html', usuarios=usuarios)


@app.route('/crear-usuario', methods=['GET', 'POST'])
@admin_required
def crear_nuevo_usuario():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        es_admin = request.form.get('es_admin') == 'on'

        if not username or not email or not password:
            flash('Todos los campos son requeridos', 'error')
            return redirect(url_for('configuracion'))

        exito, mensaje = crear_usuario(username, email, password, es_admin)
        if exito:
            flash(f'Usuario "{username}" creado exitosamente', 'success')
        else:
            flash(mensaje, 'error')

        return redirect(url_for('configuracion'))

    return render_template('crear_usuario.html')


@app.route('/cambiar-contraseña', methods=['GET', 'POST'])
@login_required
def cambiar_mi_contraseña():
    """Cambiar contraseña del usuario actual"""
    if request.method == 'POST':
        contraseña_actual = request.form.get('contraseña_actual', '')
        contraseña_nueva = request.form.get('contraseña_nueva', '')
        confirmar_contraseña = request.form.get('confirmar_contraseña', '')

        if not contraseña_actual or not contraseña_nueva or not confirmar_contraseña:
            flash('Todos los campos son requeridos', 'error')
            return render_template('cambiar_contraseña.html')

        if contraseña_nueva != confirmar_contraseña:
            flash('Las contraseñas nuevas no coinciden', 'error')
            return render_template('cambiar_contraseña.html')

        exito, mensaje = cambiar_contraseña(session.get('username'), contraseña_actual, contraseña_nueva)
        if exito:
            flash('Contraseña cambiada exitosamente', 'success')
            return redirect(url_for('index'))
        else:
            flash(mensaje, 'error')

    return render_template('cambiar_contraseña.html')


@app.route('/olvide-contraseña', methods=['GET', 'POST'])
def olvide_contraseña():
    """Solicitar recuperación de contraseña"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            flash('Por favor ingresa tu email', 'error')
            return render_template('olvide_contraseña.html')

        usuario = obtener_usuario_por_email(email)
        if usuario:
            exito, token = generar_token_recuperacion(email)
            if exito:
                # Enviar email
                enviar_email_recuperacion(email, usuario['username'], token)
                flash('Se envió un correo de recuperación a tu email. Por favor revisa tu bandeja de entrada.', 'success')
                return redirect(url_for('login'))

        # No revelar si el email existe o no por seguridad
        flash('Si el email existe en nuestro sistema, recibirás un correo de recuperación.', 'info')
        return redirect(url_for('login'))

    return render_template('olvide_contraseña.html')


@app.route('/recuperar-contraseña', methods=['GET', 'POST'])
def recuperar_contraseña():
    """Restablecer contraseña con token"""
    email = request.args.get('email', '').strip()
    token = request.args.get('token', '').strip()

    if not email or not token:
        flash('Enlace de recuperación inválido o expirado', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        contraseña_nueva = request.form.get('contraseña_nueva', '')
        confirmar_contraseña = request.form.get('confirmar_contraseña', '')

        if not contraseña_nueva or not confirmar_contraseña:
            flash('Ambos campos de contraseña son requeridos', 'error')
            return render_template('recuperar_contraseña.html', email=email, token=token)

        if contraseña_nueva != confirmar_contraseña:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('recuperar_contraseña.html', email=email, token=token)

        exito, mensaje = resetear_contraseña_con_token(email, token, contraseña_nueva)
        if exito:
            flash('Contraseña restablecida exitosamente. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash(mensaje, 'error')

    return render_template('recuperar_contraseña.html', email=email, token=token)


@app.route('/cargar-ventas', methods=['GET', 'POST'])
@login_required
def cargar_ventas():
    """Cargar y procesar archivo de ventas"""
    if request.method == 'POST':
        if 'archivo' not in request.files:
            flash('No se seleccionó archivo', 'error')
            return redirect(request.url)
        
        file = request.files['archivo']
        if file.filename == '':
            flash('No se seleccionó archivo', 'error')
            return redirect(request.url)
        
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in {'csv', 'xlsx', 'xls'}:
            flash('Solo se permiten archivos CSV y XLSX', 'error')
            return redirect(request.url)
        
        try:
            # Obtener consecutivo
            consecutivo = obtener_consecutivo_formateado('ventas')
            
            # Guardar archivo original
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'ventas', 
                                   f"{consecutivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
            file.save(filepath)
            
            # Procesar archivo
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
            
            # Validar columnas requeridas para ventas
            columnas_lower = [c.lower() for c in df.columns]
            
            # Columnas críticas: vendedor nombre/vendedor, vr. bruto
            tiene_vendedor = any('vendedor' in c for c in columnas_lower)
            tiene_bruto = any('bruto' in c for c in columnas_lower)
            
            if not tiene_vendedor:
                flash('Falta columna "vendedor" o "vendedor nombre"', 'error')
                return redirect(request.url)
            
            if not tiene_bruto:
                flash('Falta columna "Vr. bruto"', 'error')
                return redirect(request.url)
            
            # Calcular comisiones
            df_comisiones = calcular_comisiones_ventas(df)
            df_clientes = calcular_resumen_clientes_ventas(df)
            
            # Verificar consecutivos
            alertas_consecutivos = verificar_consecutivos_facturas(df)
            
            # Si hay alertas, guardar datos en sesión y mostrar modal
            if alertas_consecutivos:
                # Guardar datos en sesión para continuar después
                session['datos_ventas_pendientes'] = {
                    'df_comisiones_json': df_comisiones.to_json(),
                    'df_clientes_json': df_clientes.to_json(),
                    'consecutivo': consecutivo
                }
                session.modified = True
                
                return render_template('cargar_ventas.html', 
                                     alertas_consecutivos=alertas_consecutivos,
                                     mostrar_modal=True)
            
            # Si no hay alertas, proceder normalmente
            
            # Generar Excel
            excel_output = generar_excel_ventas(df_comisiones, consecutivo)
            reporte_filename = f"{consecutivo}_Reporte_Ventas.xlsx"
            reporte_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reportes', reporte_filename)
            reporte_path_excel = os.path.join('EXCEL__', 'COMISIONES', reporte_filename)

            # Reporte por cliente
            excel_clientes_output = generar_excel_ventas_clientes(df_clientes, consecutivo)
            reporte_clientes_filename = f"{consecutivo}_Reporte_Ventas_Por_Cliente.xlsx"
            reporte_clientes_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reportes', reporte_clientes_filename)
            reporte_clientes_path_excel = os.path.join('EXCEL__', 'COMISIONES', reporte_clientes_filename)
            
            with open(reporte_path, 'wb') as f:
                f.write(excel_output.getvalue())
            
            # Guardar también en EXCEL__/COMISIONES
            with open(reporte_path_excel, 'wb') as f:
                excel_output.seek(0)
                f.write(excel_output.getvalue())

            with open(reporte_clientes_path, 'wb') as f:
                f.write(excel_clientes_output.getvalue())

            with open(reporte_clientes_path_excel, 'wb') as f:
                excel_clientes_output.seek(0)
                f.write(excel_clientes_output.getvalue())
            
            # Agregar al historial
            agregar_reporte('ventas', consecutivo, reporte_filename)
            
            flash(f'Ventas procesadas correctamente. Reporte: {consecutivo}', 'success')
            return redirect(url_for('ver_reportes_ventas', reporte=reporte_filename, reporte_clientes=reporte_clientes_filename))
        
        except Exception as e:
            flash(f'Error al procesar archivo: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('cargar_ventas.html')


@app.route('/cargar-recaudos', methods=['GET', 'POST'])
@login_required
def cargar_recaudos():
    """Cargar y procesar archivo de recaudos"""
    if request.method == 'POST':
        if 'archivo' not in request.files:
            flash('No se seleccionó archivo', 'error')
            return redirect(request.url)
        
        file = request.files['archivo']
        if file.filename == '':
            flash('No se seleccionó archivo', 'error')
            return redirect(request.url)
        
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in {'csv', 'xlsx', 'xls'}:
            flash('Solo se permiten archivos CSV y XLSX', 'error')
            return redirect(request.url)
        
        try:
            # Obtener consecutivo
            consecutivo = obtener_consecutivo_formateado('recaudos')
            
            # Guardar archivo original
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'recaudos',
                                   f"{consecutivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
            file.save(filepath)
            
            # Procesar archivo
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
            
            # Validar columnas requeridas
            columnas_requeridas = ['cobrador', 'monto', 'fecha']
            columnas_faltantes = [col for col in columnas_requeridas if col.lower() not in [c.lower() for c in df.columns]]
            
            if columnas_faltantes:
                flash(f'Faltan columnas: {", ".join(columnas_faltantes)}', 'error')
                return redirect(request.url)
            
            # Calcular comisiones
            df_comisiones = calcular_comisiones_recaudos(df)
            
            # Generar Excel
            excel_output = generar_excel_recaudos(df_comisiones, consecutivo)
            reporte_filename = f"{consecutivo}_Reporte_Recaudos.xlsx"
            reporte_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reportes', reporte_filename)
            reporte_path_excel = os.path.join('EXCEL__', 'COMISIONES', reporte_filename)
            
            with open(reporte_path, 'wb') as f:
                f.write(excel_output.getvalue())
            
            # Guardar también en EXCEL__/COMISIONES
            with open(reporte_path_excel, 'wb') as f:
                excel_output.seek(0)
                f.write(excel_output.getvalue())
            
            # Agregar al historial
            agregar_reporte('recaudos', consecutivo, reporte_filename)
            
            flash(f'Recaudos procesados correctamente. Reporte: {consecutivo}', 'success')
            return redirect(url_for('ver_reportes_recaudos', reporte=reporte_filename))
        
        except Exception as e:
            flash(f'Error al procesar archivo: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('cargar_recaudos.html')


@app.route('/reportes/ventas')
@login_required
def ver_reportes_ventas():
    """Ver reportes de ventas"""
    reporte = request.args.get('reporte')
    reporte_clientes = request.args.get('reporte_clientes')
    datos = None
    datos_clientes = None
    
    if reporte:
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'reportes', reporte)
            df = pd.read_excel(filepath, sheet_name='Resumen')
            # Convertir a lista de diccionarios
            if len(df) > 0:
                datos = df.to_dict('records')
            else:
                datos = []
        except Exception as e:
            print(f'Error al leer reporte: {str(e)}')
            flash(f'No se encontró el reporte: {str(e)}', 'error')
            datos = None

    if not reporte_clientes and reporte and reporte.endswith('_Reporte_Ventas.xlsx'):
        reporte_clientes = reporte.replace('_Reporte_Ventas.xlsx', '_Reporte_Ventas_Por_Cliente.xlsx')

    if reporte_clientes:
        try:
            clientes_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reportes', reporte_clientes)
            df_clientes = pd.read_excel(clientes_path, sheet_name='Resumen')
            if len(df_clientes) > 0:
                datos_clientes = df_clientes.to_dict('records')
            else:
                datos_clientes = []
        except Exception as e:
            print(f'Error al leer reporte por cliente: {str(e)}')
            datos_clientes = []
    
    return render_template('reportes_ventas.html', datos=datos if datos else [], datos_clientes=datos_clientes if datos_clientes else [], reporte_clientes=reporte_clientes)


@app.route('/reportes/recaudos')
@login_required
def ver_reportes_recaudos():
    """Ver reportes de recaudos"""
    reporte = request.args.get('reporte')
    datos = None
    
    if reporte:
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'reportes', reporte)
            df = pd.read_excel(filepath, sheet_name='Resumen')
            # Convertir a lista de diccionarios
            if len(df) > 0:
                datos = df.to_dict('records')
            else:
                datos = []
        except Exception as e:
            print(f'Error al leer reporte: {str(e)}')
            flash(f'No se encontró el reporte: {str(e)}', 'error')
            datos = None
    
    return render_template('reportes_recaudos.html', datos=datos if datos else [])


@app.route('/historial')
@login_required
def historial():
    """Ver historial de todos los reportes"""
    tipo = request.args.get('tipo')  # 'ventas', 'recaudos' o None para todos
    reportes = obtener_reportes(tipo)
    return render_template('historial.html', reportes=reportes, tipo_filtro=tipo)


@app.route('/descargar/<filename>')
@login_required
def descargar(filename):
    """Descargar un reporte en Excel"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'reportes', filename)
        
        if not os.path.exists(filepath):
            flash('Archivo no encontrado', 'error')
            return redirect(url_for('historial'))
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f'Error al descargar: {str(e)}', 'error')
        return redirect(url_for('historial'))


@app.route('/api/resumen')
@login_required
def api_resumen():
    """API para obtener resumen general"""
    reportes = obtener_reportes()
    
    total_reportes = len(reportes)
    reportes_ventas = len([r for r in reportes if r['tipo'] == 'ventas'])
    reportes_recaudos = len([r for r in reportes if r['tipo'] == 'recaudos'])
    
    return jsonify({
        'total_reportes': total_reportes,
        'reportes_ventas': reportes_ventas,
        'reportes_recaudos': reportes_recaudos
    })


@app.route('/guardar-comentario-consecutivo', methods=['POST'])
@login_required
def guardar_comentario_consecutivo():
    """Guarda un comentario sobre un salto de consecutivo"""
    try:
        datos = request.get_json()
        
        usuario = session.get('username', 'Usuario desconocido')
        prefijo = datos.get('prefijo', '')
        desde = int(datos.get('desde', 0))
        hasta = int(datos.get('hasta', 0))
        salto = int(datos.get('salto', 0))
        comentario = datos.get('comentario', '').strip()
        
        if not comentario:
            return jsonify({'success': False, 'message': 'El comentario no puede estar vacío'}), 400
        
        # Guardar el comentario
        comentario_guardado = agregar_comentario_consecutivo(
            usuario=usuario,
            prefijo=prefijo,
            desde=desde,
            hasta=hasta,
            salto=salto,
            comentario=comentario
        )
        
        return jsonify({
            'success': True,
            'message': 'Comentario guardado correctamente',
            'comentario_id': comentario_guardado['id']
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al guardar comentario: {str(e)}'}), 500


@app.route('/comentarios-consecutivos', methods=['GET'])
@login_required
def ver_comentarios_consecutivos():
    """Muestra todos los comentarios de consecutivos registrados"""
    from comentarios import obtener_todos_comentarios
    
    comentarios = obtener_todos_comentarios()
    
    # Agrupar comentarios por prefijo y salto
    comentarios_agrupados = {}
    for com in comentarios:
        key = f"{com['prefijo']}{com['desde']:05d}→{com['prefijo']}{com['hasta']:05d}"
        if key not in comentarios_agrupados:
            comentarios_agrupados[key] = {
                'prefijo': com['prefijo'],
                'desde': com['desde'],
                'hasta': com['hasta'],
                'salto': com['salto'],
                'comentarios': []
            }
        comentarios_agrupados[key]['comentarios'].append(com)
    
    return render_template('comentarios_consecutivos.html', 
                         comentarios_agrupados=comentarios_agrupados,
                         comentarios=comentarios,
                         total_comentarios=len(comentarios))


@app.route('/procesar-reporte-ventas', methods=['POST'])
@login_required
def procesar_reporte_ventas():
    """Procesa el reporte de ventas después de guardar los comentarios"""
    try:
        datos_pendientes = session.get('datos_ventas_pendientes')
        
        if not datos_pendientes:
            return jsonify({'success': False, 'message': 'Datos de sesión no encontrados'}), 400
        
        # Recuperar datos de la sesión
        df_comisiones = pd.read_json(datos_pendientes['df_comisiones_json'])
        df_clientes = pd.read_json(datos_pendientes['df_clientes_json'])
        consecutivo = datos_pendientes['consecutivo']
        
        # Generar Excel
        excel_output = generar_excel_ventas(df_comisiones, consecutivo)
        reporte_filename = f"{consecutivo}_Reporte_Ventas.xlsx"
        reporte_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reportes', reporte_filename)
        reporte_path_excel = os.path.join('EXCEL__', 'COMISIONES', reporte_filename)

        # Reporte por cliente
        excel_clientes_output = generar_excel_ventas_clientes(df_clientes, consecutivo)
        reporte_clientes_filename = f"{consecutivo}_Reporte_Ventas_Por_Cliente.xlsx"
        reporte_clientes_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reportes', reporte_clientes_filename)
        reporte_clientes_path_excel = os.path.join('EXCEL__', 'COMISIONES', reporte_clientes_filename)
        
        with open(reporte_path, 'wb') as f:
            f.write(excel_output.getvalue())
        
        # Guardar también en EXCEL__/COMISIONES
        with open(reporte_path_excel, 'wb') as f:
            excel_output.seek(0)
            f.write(excel_output.getvalue())

        with open(reporte_clientes_path, 'wb') as f:
            f.write(excel_clientes_output.getvalue())

        with open(reporte_clientes_path_excel, 'wb') as f:
            excel_clientes_output.seek(0)
            f.write(excel_clientes_output.getvalue())
        
        # Agregar al historial
        agregar_reporte('ventas', consecutivo, reporte_filename)
        
        # Limpiar sesión
        if 'datos_ventas_pendientes' in session:
            del session['datos_ventas_pendientes']
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Reporte procesado correctamente',
            'redirect': url_for('ver_reportes_ventas', reporte=reporte_filename, reporte_clientes=reporte_clientes_filename)
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al procesar reporte: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
