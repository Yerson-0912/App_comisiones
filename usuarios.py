"""
Gestión de usuarios y autenticación
"""
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

USUARIOS_FILE = 'usuarios.json'

def _crear_archivo_usuarios_si_no_existe():
    """Crea archivo de usuarios con usuario admin por defecto"""
    if not os.path.exists(USUARIOS_FILE):
        usuarios = {
            'usuarios': [
                {
                    'id': 1,
                    'username': 'admin',
                    'email': 'admin@example.com',
                    'password_hash': generate_password_hash('admin123'),
                    'es_admin': True,
                    'fecha_creacion': datetime.now().isoformat(),
                    'activo': True
                }
            ],
            'fecha_creacion': datetime.now().isoformat()
        }
        with open(USUARIOS_FILE, 'w') as f:
            json.dump(usuarios, f, indent=2)

def _leer_usuarios():
    """Lee el archivo de usuarios"""
    _crear_archivo_usuarios_si_no_existe()
    with open(USUARIOS_FILE, 'r') as f:
        return json.load(f)

def _guardar_usuarios(datos):
    """Guarda el archivo de usuarios"""
    with open(USUARIOS_FILE, 'w') as f:
        json.dump(datos, f, indent=2)

def autenticar_usuario(username, password):
    """Autentica un usuario"""
    datos = _leer_usuarios()
    for usuario in datos['usuarios']:
        if usuario['username'] == username and usuario['activo']:
            if check_password_hash(usuario['password_hash'], password):
                return usuario
    return None

def obtener_usuario_por_username(username):
    """Obtiene un usuario por su nombre"""
    datos = _leer_usuarios()
    for usuario in datos['usuarios']:
        if usuario['username'] == username:
            return usuario
    return None

def obtener_usuario_por_email(email):
    """Obtiene un usuario por su email"""
    datos = _leer_usuarios()
    for usuario in datos['usuarios']:
        if usuario['email'] == email:
            return usuario
    return None

def crear_usuario(username, email, password, es_admin=False):
    """Crea un nuevo usuario"""
    datos = _leer_usuarios()
    
    # Validar que no exista
    if obtener_usuario_por_username(username):
        return False, 'El usuario ya existe'
    
    if obtener_usuario_por_email(email):
        return False, 'El email ya está registrado'
    
    nuevo_id = max([u['id'] for u in datos['usuarios']], default=0) + 1
    
    nuevo_usuario = {
        'id': nuevo_id,
        'username': username,
        'email': email,
        'password_hash': generate_password_hash(password),
        'es_admin': es_admin,
        'fecha_creacion': datetime.now().isoformat(),
        'activo': True,
        'token_recuperacion': None,
        'token_expira': None
    }
    
    datos['usuarios'].append(nuevo_usuario)
    _guardar_usuarios(datos)
    return True, 'Usuario creado exitosamente'

def cambiar_contraseña(username, contraseña_actual, contraseña_nueva):
    """Cambia la contraseña de un usuario"""
    usuario = obtener_usuario_por_username(username)
    
    if not usuario:
        return False, 'Usuario no encontrado'
    
    if not check_password_hash(usuario['password_hash'], contraseña_actual):
        return False, 'Contraseña actual incorrecta'
    
    datos = _leer_usuarios()
    for u in datos['usuarios']:
        if u['username'] == username:
            u['password_hash'] = generate_password_hash(contraseña_nueva)
            break
    
    _guardar_usuarios(datos)
    return True, 'Contraseña cambiada exitosamente'

def generar_token_recuperacion(email):
    """Genera un token de recuperación de contraseña"""
    usuario = obtener_usuario_por_email(email)
    
    if not usuario:
        return False, 'Email no encontrado'
    
    # Generar token seguro
    token = secrets.token_urlsafe(32)
    
    datos = _leer_usuarios()
    for u in datos['usuarios']:
        if u['email'] == email:
            u['token_recuperacion'] = token
            u['token_expira'] = (datetime.now().timestamp() + 3600)  # 1 hora
            break
    
    _guardar_usuarios(datos)
    return True, token

def validar_token_recuperacion(email, token):
    """Valida un token de recuperación"""
    usuario = obtener_usuario_por_email(email)
    
    if not usuario:
        return False, 'Usuario no encontrado'
    
    if not usuario.get('token_recuperacion'):
        return False, 'No hay token de recuperación activo'
    
    if usuario['token_recuperacion'] != token:
        return False, 'Token inválido'
    
    if datetime.now().timestamp() > usuario.get('token_expira', 0):
        return False, 'Token expirado'
    
    return True, 'Token válido'

def resetear_contraseña_con_token(email, token, contraseña_nueva):
    """Resetea la contraseña usando un token válido"""
    valido, mensaje = validar_token_recuperacion(email, token)
    
    if not valido:
        return False, mensaje
    
    datos = _leer_usuarios()
    for u in datos['usuarios']:
        if u['email'] == email:
            u['password_hash'] = generate_password_hash(contraseña_nueva)
            u['token_recuperacion'] = None
            u['token_expira'] = None
            break
    
    _guardar_usuarios(datos)
    return True, 'Contraseña restablecida exitosamente'

def obtener_todos_usuarios():
    """Obtiene todos los usuarios (para panel admin)"""
    datos = _leer_usuarios()
    # No devolver contraseñas
    usuarios = []
    for u in datos['usuarios']:
        usuario_seguro = {
            'id': u['id'],
            'username': u['username'],
            'email': u['email'],
            'es_admin': u['es_admin'],
            'fecha_creacion': u['fecha_creacion'],
            'activo': u['activo']
        }
        usuarios.append(usuario_seguro)
    return usuarios

def desactivar_usuario(username):
    """Desactiva un usuario"""
    datos = _leer_usuarios()
    for u in datos['usuarios']:
        if u['username'] == username:
            u['activo'] = False
            break
    _guardar_usuarios(datos)
    return True

def activar_usuario(username):
    """Activa un usuario"""
    datos = _leer_usuarios()
    for u in datos['usuarios']:
        if u['username'] == username:
            u['activo'] = True
            break
    _guardar_usuarios(datos)
    return True
