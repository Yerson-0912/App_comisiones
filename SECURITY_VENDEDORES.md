# 🔐 RECOMENDACIONES SOBRE VENDEDORES.PY

## ⚠️ INFORMACIÓN SENSIBLE

El archivo `vendedores.py` contiene:
- Porcentajes de comisión por vendedor
- Tramos de comisión
- Clientes especiales y sus condiciones
- Lógica de negocio privada

## 📝 OPCIONES PARA GIT

### **Opción 1: Repositorio PRIVADO (Recomendado para equipos pequeños)**
✅ **PUEDES subir vendedores.py** si:
- El repositorio de GitHub es **Private**
- Solo personas autorizadas tienen acceso
- Es más fácil mantener el código sincronizado

**Ventajas:**
- ✅ Código completo en un solo lugar
- ✅ Fácil de clonar y usar
- ✅ Control de versiones de las reglas de negocio

**Desventajas:**
- ⚠️ Si alguien obtiene acceso al repo, ve las comisiones
- ⚠️ Historial de Git guarda todas las versiones

### **Opción 2: NO subir vendedores.py (Máxima seguridad)**
🔒 **NO subas vendedores.py** si:
- El repositorio es público
- Quieres máxima seguridad
- Trabajas con desarrolladores externos

**Cómo hacerlo:**
1. Descomentar en `.gitignore`:
   ```
   vendedores.py
   ```

2. Crear `vendedores.py.example` con estructura pero sin datos reales:
   ```python
   VENDEDORES_CONFIG = {
       "Vendedor 1": {
           "tramos": [[0, 999999, 1.5]],
       },
       # Agregar más vendedores aquí
   }
   ```

3. Documentar en README cómo crear el archivo real

**Ventajas:**
- ✅ Información de negocio nunca en Git
- ✅ Máxima seguridad
- ✅ Puedes compartir el código sin exponer datos

**Desventajas:**
- ⚠️ Cada desarrollador debe crear su propio vendedores.py
- ⚠️ No hay control de versiones de las reglas de negocio

### **Opción 3: Variables de entorno (Producción)**
🚀 Para producción profesional:
- Guardar configuraciones en variables de entorno
- Usar servicios como AWS Secrets Manager
- Cargar desde base de datos encriptada

## 💡 MI RECOMENDACIÓN

**Para tu caso:**
1. **Si el repo es PRIVADO**: Sube vendedores.py (ya está configurado así)
2. **Si el repo será PÚBLICO algún día**: NO lo subas, descomentar en .gitignore
3. **Para producción futura**: Migrar a base de datos o variables de entorno

## 🔧 Estado Actual

Actualmente `vendedores.py` **SE SUBIRÁ** a Git porque:
- No está en .gitignore
- Esto es correcto si tu repositorio es **privado**

Si quieres cambiar esto:
```bash
# Para NO subir vendedores.py:
echo "vendedores.py" >> .gitignore
git rm --cached vendedores.py
git commit -m "Remover vendedores.py del repositorio"
```

## 📋 Resumen

| Escenario | Acción | Archivo |
|-----------|--------|---------|
| Repo privado, equipo de confianza | ✅ Subir vendedores.py | Tal como está |
| Repo público o desarrolladores externos | ❌ NO subir, usar .example | Descomentar en .gitignore |
| Producción profesional | 🔐 Variables de entorno | Migrar a config externa |

---

**Conclusión:** Actualmente configurado para **repositorio privado**. Si cambias a público, descomentar la línea en `.gitignore`.
