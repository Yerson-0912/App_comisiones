# Guía para Subir a GitHub

## Paso 1: Crear un nuevo repositorio en GitHub

1. Ve a https://github.com/new
2. Llena los detalles:
   - **Repository name:** `comisiones_app` (o tu nombre preferido)
   - **Description:** Sistema de Gestión de Comisiones de Ventas y Recaudos
   - **Private/Public:** Elige Private para mantenerlo privado
3. NO inicialices con README.md (ya existe)
4. Haz clic en "Create repository"

## Paso 2: Conectar el repositorio local con GitHub

Después de crear el repositorio en GitHub, verás instrucciones. Ejecuta esto en terminal:

```bash
cd /home/comisiones_app
git remote add origin https://github.com/TU_USUARIO/comisiones_app.git
git branch -M main
git push -u origin main
```

**Reemplaza:**
- `TU_USUARIO` con tu nombre de usuario de GitHub

## Paso 3: Verificar en GitHub

1. Actualiza la página de tu repositorio en GitHub
2. Deberías ver todos los archivos subidos
3. En la sección "Releases" podrás ver v1.0.0 si creas un tag

## Crear Tags para versiones (Opcional)

Para crear un tag para la versión actual:

```bash
cd /home/comisiones_app
git tag -a v1.0.0 -m "Versión 1.0.0 - Sistema completo"
git push origin v1.0.0
```

Luego en GitHub puedes crear una Release desde la pestaña "Releases".

## Autenticación en GitHub (Si lo necesitas)

Si GitHub te pide autenticación por terminal:

### Con Token Personal (Recomendado)
1. Ve a GitHub Settings → Developer settings → Personal access tokens
2. Crea un nuevo token con permisos `repo`
3. Copia el token
4. Cuando Git pida contraseña, usa el token como contraseña

### Con SSH (Alternativa)
```bash
ssh-keygen -t ed25519 -C "tu_email@example.com"
# Sigue las instrucciones
cat ~/.ssh/id_ed25519.pub  # Copia el contenido
# Ve a GitHub Settings → SSH and GPG keys
# Añade la nueva clave SSH
```

## Próximos cambios

Para futuros cambios y versiones:

```bash
# Hacer cambios en archivos...

# Agregar cambios
git add .

# Hacer commit
git commit -m "Descripción del cambio"

# Subir a GitHub
git push origin main
```

## Documentación de cambios

Cuando hagas cambios importantes:

1. Actualiza `CHANGELOG.md` con los nuevos cambios
2. Actualiza `VERSION` con el nuevo número de versión
3. Haz commit y push
4. (Opcional) Crea un tag con `git tag v1.x.x`

---

## Información del Repositorio Actual

- **Rama principal:** main
- **Versión actual:** 1.0.0
- **Commit inicial:** Sistema completo con todas las características
- **Archivos:** 30 archivos incluyendo código, templates y configuración
