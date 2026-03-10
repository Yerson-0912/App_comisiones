<div align="center">

# 💰 Liquidación de Comisiones Mensuales

### Aplicación web para calcular y liquidar comisiones de vendedores de forma automática

![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Excel](https://img.shields.io/badge/Excel%2FCSV-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)

</div>

---

## 📋 ¿Qué hace esta aplicación?

Carga archivos de ventas en formato **Excel o CSV**, procesa la información automáticamente y genera reportes de comisiones por vendedor, con reglas de negocio personalizadas por cada asesor.

---

## ✨ Funcionalidades principales

| Funcionalidad | Descripción |
|---|---|
| 📂 **Carga de archivos** | Soporta `.xlsx`, `.xls` y `.csv` |
| 🏢 **Multi-empresa** | INVERSIONES RUEDA SAS / LAMAR OPTICAL SAS / ABELARDO |
| 🔄 **Normalización** | Estandariza encabezados con variaciones de nombre |
| 🚫 **Exclusión de flete** | Excluye automáticamente conceptos de flete |
| 🏷️ **Clasificación** | Clasifica clientes en FAMILIA / CONSIGNACION / NORMAL |
| 🔍 **Filtros** | Filtrado por Mes, Empresa y Vendedor |

### 📊 Vistas generadas

- 📈 **Resumen general**
- 👥 **Consolidado de vendedores**
- 🧾 **Liquidación por vendedor y mes**
- 📑 **Base organizada de facturas**

---

## 🧮 Fórmula de cálculo

```
Subtotal = Vr. Neto  -  Vr. Imp. IVA  -  Vr. Descuento
```

---

## 📐 Reglas de comisión

### 🌐 Regla general
Para vendedores sin regla especial, se aplica el porcentaje `% Comisión` ingresado en pantalla.

---

### 👩 Natalia Reyes

**Clientes NORMAL** — Escala por tramo mensual:

| Tramo de ventas | Comisión |
|---|:---:|
| $0 — $5.000.000 | 0% |
| $5.000.001 — $10.000.000 | 2% |
| $10.000.001 — $20.000.000 | 3% |
| $20.000.001 — $30.000.000 | 4% |
| $30.000.001 en adelante | 5% |

- 🏬 Cliente **IMEVI/IMVEI**: 2% sin tope
- 👨‍👩‍👧 Clientes **FAMILIA**: 2% fijo
- 💸 Retención: **4%** sobre comisión bruta

---

### 👩‍💼 Karen Torrado

**Escala por tramo mensual consolidado:**

| Tramo de ventas | Comisión |
|---|:---:|
| $0 — $199.999.999 | 1.5% |
| $200.000.000 — $249.999.999 | 2% |
| $250.000.000 en adelante | 2.5% |

- 💳 Descuento fijo mensual: **$950.000**
- 💸 Retención: **6%** (aplicada después del descuento fijo)
- 🏢 El cálculo se toma sobre el **consolidado de todas las empresas** cargadas

---

## 🗂️ Estructura de la Base de Facturas

| Campo en tabla | Origen del dato |
|---|---|
| `CONSEC` | Documento + " " + CONSECUTIVO |
| `EMPRESAREAL` | Nombre real de empresa cargada |
| `PREFIJO` | Documento |
| `NUMERO DOC.` | CONSECUTIVO |
| `FECHA` | Fecha |
| `ASESOR` | Vendedor Nombre |
| `NIT` | Beneficiario Identidad |
| `CLIENTE` | Beneficiario Nombre |
| `CARTERA` | CONSIGNACION / FAMILIA / NORMAL |
| `CIUDAD` | Ciudad Nombre |
| `VALOR` | Suma de subtotal por factura |
| `CANTIDAD` | Suma de cantidad por factura |

---

## 🚀 Cómo usar la aplicación

```
1️⃣  Abre la app en el navegador
2️⃣  Carga uno o más archivos por empresa
3️⃣  Ajusta el % Comisión si aplica (vendedores sin regla especial)
4️⃣  Haz clic en "Procesar liquidación"
5️⃣  Usa los filtros para explorar los resultados
```

---

## 💻 Ejecución recomendada

Para evitar bloqueos del navegador al abrir archivos locales, levanta un servidor HTTP:

```bash
cd /home/comisiones_app
python3 -m http.server 5000 --bind 0.0.0.0
```

Luego abre en el navegador:

```
http://<tu-ip-o-host>:5000/reporte_comsiones_lamar/index.html
```

---

## 📄 Columnas esperadas en el archivo Excel

<details>
<summary>🔽 Ver todas las columnas</summary>

| # | Columna |
|:---:|---|
| 1 | Documento |
| 2 | TIPO CON |
| 3 | CONSECUTIVO |
| 4 | Documento Origen |
| 5 | Fecha |
| 6 | Vendedor Identidad |
| 7 | Vendedor Nombre |
| 8 | Funcionario Relacionado |
| 9 | Beneficiario Identidad |
| 10 | Beneficiario Nombre |
| 11 | Ciudad Nombre |
| 12 | Nombre Concepto |
| 13 | Cantidad |
| 14 | Vr. Base |
| 15 | Vr. Bruto |
| 16 | Vr. Descuento |
| 17 | Vr. Neto |
| 18 | Vr. Imp. IVA |
| 19 | Vr. Imp. Bebidas |
| 20 | Tf. Imp. Comestibles |
| 21 | Vr. Imp. Comestibles |

</details>

---

## ⚠️ Columnas mínimas requeridas para liquidar

> Sin estas columnas el sistema **no puede procesar** el archivo correctamente.

- `Fecha`
- `Vendedor Identidad`
- `Vendedor Nombre`
- `Vr. Descuento`
- `Vr. Neto`
- `Vr. Imp. IVA`

---

---

<div align="center">

## 👨‍💻 Desarrollador

**Yerson Vargas Vargas**

🏢 Soporte TI — LAMAR OPTICAL SAS

[![GitHub](https://img.shields.io/badge/GitHub-Yerson--0912-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Yerson-0912)
[![Gmail](https://img.shields.io/badge/Gmail-yervargas6@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:yervargas6@gmail.com)

---

*Desarrollado para **LAMAR OPTICAL SAS** & **INVERSIONES RUEDA SAS** 🏢*

</div>
