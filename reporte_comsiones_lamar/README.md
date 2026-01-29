# Liquidacion de comisiones mensuales

Aplicacion web para cargar archivos Excel de ventas y liquidar comisiones por vendedor.

## Que hace

- Carga archivos `.xlsx`, `.xls` o `.csv`.
- Permite cargar archivo por empresa:
  - INVERSIONES RUEDA SAS
  - LAMAR OPTICAL SAS
  - ABELARDO (opcional)
- Estandariza encabezados aunque vengan con variaciones de nombre.
- Excluye conceptos de flete del calculo.
- Calcula subtotal por fila:

`Subtotal = Vr. Neto - Vr. Imp. IVA - Vr. Descuento`

- Clasifica cliente en cartera:
  - FAMILIA
  - CONSIGNACION
  - NORMAL
- Genera vistas:
  - Resumen general
  - Consolidado de vendedores
  - Liquidacion por vendedor y mes
  - Base organizada de facturas

## Reglas de comision implementadas

### Regla general

- Para vendedores sin regla especial, usa el porcentaje `% Comision` ingresado en pantalla.

### Natalia Reyes

- Clientes NORMAL por tramo mensual:
  - 0 a 5.000.000: 0%
  - 5.000.001 a 10.000.000: 2%
  - 10.000.001 a 20.000.000: 3%
  - 20.000.001 a 30.000.000: 4%
  - 30.000.001 en adelante: 5%
- Cliente IMEVI/IMVEI: 2% sin tope.
- Clientes FAMILIA: 2%.
- Retencion: 4% sobre comision bruta.

### Karen Torrado

- Comision por tramo mensual:
  - 0 a 199.999.999: 1.5%
  - 200.000.000 a 249.999.999: 2%
  - 250.000.000 en adelante: 2.5%
- Descuento fijo mensual: 950.000.
- Retencion: 6% despues del descuento fijo.
- El calculo mensual se toma sobre el consolidado de empresas cargadas.

## Base organizada de facturas

La tabla `Base organizada de facturas` se muestra con este formato:

- CONSEC = Documento + " " + CONSECUTIVO
- EMPRESAREAL = nombre real de empresa cargada
- EMPRESA = igual a EMPRESAREAL
- PREFIJO = Documento
- NUMERO DOC. = CONSECUTIVO
- FECHA = Fecha
- ASESOR = Vendedor Nombre
- NIT = Beneficiario Identidad
- CLIENTE = Beneficiario Nombre
- CARTERA = tipo cliente (CONSIGNACION, FAMILIA, NORMAL)
- CIUDAD = Ciudad Nombre
- VALOR = suma de subtotal por factura
- CANTIDAD = suma de cantidad por factura

## Filtros

La interfaz permite filtrar por:

- Mes
- Empresa
- Vendedor

## Como usar

1. Abre la app en navegador.
2. Carga uno o mas archivos de empresa.
3. Ajusta `% Comision` si aplica para vendedores sin regla especial.
4. Haz clic en `Procesar liquidacion`.
5. Usa filtros para revisar resultados.

## Recomendacion de ejecucion

Para evitar problemas del navegador al abrir archivos locales, usa servidor HTTP:

```bash
cd /home/comisiones_app
python3 -m http.server 5000 --bind 0.0.0.0
```

Luego abre:

`http://<tu-ip-o-host>:5000/reporte_comsiones_lamar/index.html`

## Columnas esperadas en el archivo

- Documento
- TIPO CON
- CONSECUTIVO
- Documento Origen
- Fecha
- Vendedor Identidad
- Vendedor Nombre
- Funcionario Relacionado
- Beneficiario Identidad
- Beneficiario Nombre
- Ciudad Nombre
- Nombre Concepto
- Cantidad
- Vr. Base
- Vr. Bruto
- Vr. Descuento
- Vr. Neto
- Vr. Imp. IVA
- Vr. Imp. Bebidas
- Tf. Imp. Comestibles
- Vr. Imp. Comestibles

## Columnas minimas para liquidar

- Fecha
- Vendedor Identidad
- Vendedor Nombre
- Vr. Descuento
- Vr. Neto
- Vr. Imp. IVA
