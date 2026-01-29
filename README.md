# Sistema de Gestión de Comisiones

Panel web profesional para calcular comisiones de ventas y recaudos. Sistema independiente con autenticación segura, verificación automática de consecutivos y auditoría completa.

**Versión:** v1.0.0 | [Ver historial de versiones](CHANGELOG.md)

## Características Principales

### 🔐 Autenticación y Seguridad
- Sistema de login seguro con sesiones
- Gestión de usuarios con roles (admin/regular)
- Panel de administración
- Recuperación de contraseña por email

### 📊 Cálculo de Comisiones Automático
- Cálculo inteligente para ventas (múltiples tramos)
- Cálculo para recaudos (3% con condición de plazo)
- Soporte para clientes especiales
- Validación de datos automática

### 📈 Reportes y Análisis
- Reportes detallados por vendedor/cobrador
- Análisis por cliente con Excel descargable
- Visualización con tablas expandibles
- Historial completo de reportes
- Resumenes comparativos

### 🚨 Verificación de Anomalías
- Detección automática de saltos en consecutivos
- Alertas inteligentes (gap < 50 facturas)
- Sistema de comentarios para justificar
- Auditoría completa con timestamps

### 🎨 Interfaz Moderna
- Diseño corporativo y responsivo
- Validación de formularios
- Mensajes de feedback claros
- Soporte para dispositivos móviles

---

## Instalación Rápida

### Requisitos
- Python 3.10+
- pip (gestor de paquetes)

### Pasos

1. **Clonar o descargar el proyecto**
```bash
git clone https://github.com/tu_usuario/comisiones_app.git
cd comisiones_app
```

2. **Crear entorno virtual**
```bash
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
# O instalar manualmente:
# pip install flask pandas openpyxl werkzeug
```

4. **Ejecutar la aplicación**
```bash
python3 app.py
```

5. **Acceder a la aplicación**
- **URL:** http://localhost:5000
- **Usuario:** admin
- **Contraseña:** admin123

---

## Uso

### Primer Acceso
1. Ingresa con usuario: `admin` / contraseña: `admin123`
2. Ve a **Configuración** para crear nuevos usuarios
3. Asigna roles (admin o regular)

### Cargar Datos de Ventas
1. Selecciona **Cargar Ventas**
2. Sube archivo CSV o Excel
3. El sistema verifica consecutivos automáticamente
4. Si hay saltos, comenta sobre ellos
5. Genera el reporte automáticamente

**Columnas requeridas:**
- `vendedor` - Nombre del vendedor
- `cliente` - Nombre del cliente
- `factura` - Número de factura (FEV000000)
- `monto` - Monto de la venta
- `descuentos` - Descuentos aplicados
- `cantidad` - Cantidad de unidades

### Cargar Datos de Recaudos
1. Selecciona **Cargar Recaudos**
2. Sube archivo con datos de recaudos
3. Genera reporte automáticamente

### Generar Reportes
1. Ve a **Reportes**
2. Selecciona **Ventas** o **Recaudos**
3. Visualiza datos en tablas expandibles
4. Descarga reportes por cliente en Excel

### Ver Historial de Comentarios
1. Ve a **Comentarios** (en el menú principal)
2. Visualiza todos los comentarios registrados
3. Filtra por salto de consecutivo si lo deseas

---

## Configuración de Comisiones

### Vendedores
Las comisiones se calculan por tramos según el monto de venta:

| Vendedor | Tramo 1 | Tramo 2 | Tramo 3 |
|----------|---------|---------|---------|
| Karen Torrado | 1.5% | 2.0% | 2.5% |
| Natalia Reyes | 0-5% * | - | - |
| Jose A. Fajardo | 1% | - | 2% |
| Jhonatan Vasquez | 1% | - | 2% |

*Clientes especiales tienen comisión variable

### Cobradores
| Cobrador | Comisión | Condición |
|----------|----------|-----------|
| Jorge Pernia | 3% | Solo recaudos con 60+ días de mora |

---

## Estructura de Archivos

```
comisiones_app/
├── app.py                      # Aplicación principal Flask
├── comisiones.py               # Lógica de cálculo de comisiones
├── comentarios.py              # Sistema de comentarios
├── contador.py                 # Gestor de consecutivos
├── historial.py                # Historial de reportes
├── vendedores.py               # Configuración de vendedores
├── usuarios.py                 # Autenticación de usuarios
├── emails.py                   # Notificaciones por email
├── static/                     # CSS, JavaScript, imágenes
├── templates/                  # Plantillas HTML
│   ├── base.html              # Plantilla base
│   ├── login.html             # Página de login
│   ├── index.html             # Panel principal
│   ├── cargar_ventas.html     # Cargar ventas
│   ├── cargar_recaudos.html   # Cargar recaudos
│   ├── reportes_ventas.html   # Reporte de ventas
│   ├── reportes_recaudos.html # Reporte de recaudos
│   ├── comentarios_consecutivos.html # Historial de comentarios
│   └── configuracion.html     # Panel de administración
├── uploads/                    # Archivos subidos
├── EXCEL__/                    # Reportes generados
├── contador.json               # Persistencia de consecutivos
├── usuarios.json               # Base de datos de usuarios
├── comentarios_consecutivos.json # Comentarios registrados
├── historial_reportes.json     # Historial de reportes
├── CHANGELOG.md                # Historial de versiones
├── VERSION                     # Versión actual
└── README.md                   # Este archivo
```

---

## Tecnología

- **Backend:** Python 3.10 + Flask 2.x
- **Frontend:** HTML5 + CSS3 + JavaScript vanilla
- **Data Processing:** Pandas, OpenPyXL
- **Seguridad:** Werkzeug password hashing
- **Persistencia:** JSON (sin SQL)
- **Control de versiones:** Git

---

## Troubleshooting

### Puerto 5000 en uso
```bash
# Encontrar proceso en puerto 5000
lsof -i :5000
# Matar proceso
kill -9 <PID>
# O cambiar puerto en app.py: app.run(port=5001)
```

### Errores de importación
```bash
# Reinstalar dependencias
pip install --upgrade flask pandas openpyxl werkzeug
```

### Problemas con archivos cargados
- Verifica que el archivo CSV/Excel tenga las columnas correctas
- Usa codificación UTF-8
- No incluyas filas vacías

---

## Contribuir

Para reportar bugs o sugerir mejoras:
1. Abre un issue en GitHub
2. Describe el problema detalladamente
3. Incluye pasos para reproducirlo

---

## Licencia

Proyecto privado. Todos los derechos reservados.

---

## Soporte

Para preguntas o soporte técnico, contacta al equipo de desarrollo.

**Última actualización:** Enero 2026

## 📁 Estructura del Proyecto

```
comisiones_app/
├── app.py                 # Aplicación principal Flask
├── comisiones.py          # Lógica de cálculo de comisiones
├── templates/
│   ├── base.html          # Template base
│   ├── index.html         # Página de inicio
│   ├── cargar_ventas.html # Formulario de ventas
│   ├── cargar_recaudos.html # Formulario de recaudos
│   ├── reportes_ventas.html # Reporte de ventas
│   └── reportes_recaudos.html # Reporte de recaudos
├── static/                # Archivos estáticos (CSS, JS)
└── uploads/               # Directorio de archivos subidos
```

## ⚙️ Personalización

### Cambiar porcentajes de comisión

Edita el archivo `comisiones.py`:

**Para ventas:**
```python
def calcular_comisiones_ventas(df):
    # Línea 22-24: Ajusta los porcentajes
    df.loc[df['producto'].str.lower().str.contains('premium', na=False), 'comision_porcentaje'] = 8  # Cambiar a tu valor
```

**Para recaudos:**
```python
def calcular_comisiones_recaudos(df):
    # Línea 57: Ajusta el porcentaje
    df['comision_porcentaje'] = 2  # Cambiar a tu valor
```

### Agregar nuevas categorías de productos

Dentro de `calcular_comisiones_ventas()`, agrega líneas como:
```python
df.loc[df['producto'].str.lower().str.contains('tu_producto', na=False), 'comision_porcentaje'] = 10
```

## 📊 Formato de Archivos

### Ventas (CSV/XLSX)
```
vendedor,monto,cantidad,producto
Juan López,5000,10,Premium
María García,3000,5,Estándar
Carlos Rodríguez,2000,20,Básico
```

### Recaudos (CSV/XLSX)
```
cobrador,monto,fecha
Pedro Martínez,2500,2025-01-27
Ana López,3500,2025-01-27
Carlos González,5000,2025-01-27
```

## 🔒 Seguridad

- Los archivos se guardan con timestamp automático
- Límite de tamaño: 50MB por archivo
- Solo se aceptan formatos CSV y XLSX
- Validación de columnas requeridas

## 🌐 Acceso Remoto

Para acceder desde otro equipo en la red:

1. Obtén tu IP del servidor: `ip addr show`
2. Accede desde otro navegador: `http://[tu_ip]:5000`

**Nota:** Este es un servidor de desarrollo. Para producción, usa Gunicorn o similar:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📝 Notas

- Los datos se guardan en archivos JSON dentro de `uploads/`
- Puedes descargar y guardar los reportes manualmente
- Para agregar funcionalidad de BD persistente, consulta la sección de extensiones

## 🐛 Troubleshooting

**Error: "module not found"**
```bash
python3 -m pip install flask pandas openpyxl
```

**Puerto 5000 en uso:**
```bash
# En app.py, cambiar: app.run(..., port=5001)
```

**Permisos de escritura en uploads:**
```bash
chmod 755 /home/comisiones_app/uploads
```

## 📧 Soporte

Este sistema es independiente de Odoo y no requiere configuración de Odoo.
Perfecto para gestión simplificada de comisiones.

---

**Desarrollado por:** Yerson Vargas  
**Última actualización:** Enero 2026  
**Versión:** 1.0
