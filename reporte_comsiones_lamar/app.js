const EXPECTED_COLUMNS = [
  "Documento",
  "TIPO CON",
  "CONSECUTIVO",
  "Documento Origen",
  "Fecha",
  "Vendedor Identidad",
  "Vendedor Nombre",
  "Funcionario Relacionado",
  "Beneficiario Identidad",
  "Beneficiario Nombre",
  "Ciudad Nombre",
  "Nombre Concepto",
  "Cantidad",
  "Vr. Base",
  "Vr. Bruto",
  "Vr. Descuento",
  "Vr. Neto",
  "Vr. Imp. IVA",
  "Vr. Imp. Bebidas",
  "Tf. Imp. Comestibles",
  "Vr. Imp. Comestibles",
];

const REQUIRED_FOR_CALC = [
  "Fecha",
  "Vendedor Identidad",
  "Vendedor Nombre",
  "Vr. Descuento",
  "Vr. Neto",
  "Vr. Imp. IVA",
];

const HEADER_ALIASES = {
  Documento: ["documento", "tipo documento"],
  "TIPO CON": ["tipo con", "tipocon", "tipo concepto"],
  CONSECUTIVO: ["consecutivo", "nro consecutivo", "numero consecutivo"],
  "Documento Origen": ["documento origen", "doc origen"],
  Fecha: ["fecha", "fecha documento", "fecha factura"],
  "Vendedor Identidad": [
    "vendedor identidad",
    "identidad vendedor",
    "vendedor identificacion",
    "identificacion vendedor",
    "cedula vendedor",
    "id vendedor",
  ],
  "Vendedor Nombre": [
    "vendedor nombre",
    "nombre vendedor",
    "vendedor",
    "asesor",
    "asesor nombre",
  ],
  "Funcionario Relacionado": ["funcionario relacionado", "funcionario"],
  "Beneficiario Identidad": [
    "beneficiario identidad",
    "identidad beneficiario",
    "beneficiario identificacion",
    "id beneficiario",
  ],
  "Beneficiario Nombre": ["beneficiario nombre", "nombre beneficiario"],
  "Ciudad Nombre": ["ciudad nombre", "nombre ciudad", "ciudad"],
  "Nombre Concepto": ["nombre concepto", "concepto", "descripcion concepto"],
  Cantidad: ["cantidad", "cant"],
  "Vr. Base": ["vr base", "valor base", "v base"],
  "Vr. Bruto": ["vr bruto", "valor bruto", "v bruto"],
  "Vr. Descuento": ["vr descuento", "valor descuento", "descuento"],
  "Vr. Neto": ["vr neto", "valor neto", "neto"],
  "Vr. Imp. IVA": ["vr imp iva", "valor imp iva", "iva", "impuesto iva"],
  "Vr. Imp. Bebidas": [
    "vr imp bebidas",
    "valor imp bebidas",
    "impuesto bebidas",
  ],
  "Tf. Imp. Comestibles": [
    "tf imp comestibles",
    "tarifa imp comestibles",
    "tasa imp comestibles",
  ],
  "Vr. Imp. Comestibles": [
    "vr imp comestibles",
    "valor imp comestibles",
    "impuesto comestibles",
  ],
};

const COLUMN_ALIAS_SETS = new Map(
  EXPECTED_COLUMNS.map((column) => {
    const aliases = HEADER_ALIASES[column] ?? [];
    const normalizedAliases = [column, ...aliases].map((item) => normalizeHeader(item));
    return [column, new Set(normalizedAliases)];
  })
);

const state = {
  rawRowsByCompany: {
    "INVERSIONES RUEDA SAS": [],
    "LAMAR OPTICAL SAS": [],
    ABELARDO: [],
  },
  fileNamesByCompany: {
    "INVERSIONES RUEDA SAS": "",
    "LAMAR OPTICAL SAS": "",
    ABELARDO: "",
  },
  processedRows: [],
  groupedRows: [],
  organizedRows: [],
};

const fileRuedaInput = document.getElementById("fileRueda");
const fileLamarInput = document.getElementById("fileLamar");
const fileAbelardoInput = document.getElementById("fileAbelardo");
const commissionRateInput = document.getElementById("commissionRate");
const monthFilter = document.getElementById("monthFilter");
const companyFilter = document.getElementById("companyFilter");
const sellerFilter = document.getElementById("sellerFilter");
const customerFilter = document.getElementById("customerFilter");
const processBtn = document.getElementById("processBtn");
const message = document.getElementById("message");

const conditionsSection = document.getElementById("conditionsSection");
const conditionsBody = document.getElementById("conditionsBody");

const summary = document.getElementById("summary");
const sellerSection = document.getElementById("sellerSection");
const resultsSection = document.getElementById("resultsSection");
const detailSection = document.getElementById("detailSection");

const kpiInvoices = document.getElementById("kpiInvoices");
const kpiSubtotal = document.getElementById("kpiSubtotal");
const kpiCommission = document.getElementById("kpiCommission");
const kpiRetention = document.getElementById("kpiRetention");
const kpiNetCommission = document.getElementById("kpiNetCommission");

const COMPANY_RUEDA = "INVERSIONES RUEDA SAS";
const COMPANY_LAMAR = "LAMAR OPTICAL SAS";
const COMPANY_ABELARDO = "ABELARDO";
const SELLER_NATALIA_REYES = normalizeHeader("NATALIA REYES");
const SELLER_KAREN_TORRADO = normalizeHeader("KAREN TORRADO");
const SELLER_JOSE_ALFREDO = normalizeHeader("JOSE ALFREDO");
const NATALIA_RETENTION_RATE = 4;
const KAREN_MONTHLY_DISCOUNT = 950000;
const KAREN_RETENTION_RATE = 6;
const PRIVATE_CONDITIONS_SHORTCUT_KEY = "q";

const SELLER_CONDITIONS = [
  {
    key: "natalia",
    seller: "Natalia Reyes",
    rules: [
      "Cliente IMEVI: comision fija del 2%.",
      "Clientes tipo FAMILIA: comision fija del 2%.",
      "Clientes tipo NORMAL: escala mensual sobre subtotal (0% <= 5M, 2% <= 10M, 3% <= 20M, 4% <= 30M, 5% > 30M).",
      `Retencion del ${NATALIA_RETENTION_RATE}% sobre la comision calculada.`,
      "Clientes en CONSIGNACION (distintos de IMEVI): actualmente 0%.",
    ],
  },
  {
    key: "karen",
    seller: "Karen Torrado",
    rules: [
      "Comision segun total mensual: 1.5% hasta 199.999.999; 2% hasta 249.999.999; 2.5% desde 250.000.000.",
      `Descuento fijo mensual de ${formatMoney(KAREN_MONTHLY_DISCOUNT)} sobre la comision mensual.`,
      `Retencion del ${KAREN_RETENTION_RATE}% sobre la base despues del descuento fijo.`,
      "El descuento y la retencion mensual se distribuyen proporcionalmente por factura.",
    ],
  },
  {
    key: "jose",
    seller: "Jose Alfredo",
    rules: [
      "Cliente Optica Colsanitas: si el total mensual de Colsanitas >= 45.000.000, aplica 2%.",
      "Clientes de CONSIGNACION (excepto regla Colsanitas): 0%.",
      "Ventas en Bogota (no consignacion): escala mensual 0% (<60M), 1% (>=60M), 1.5% (>=80M).",
      "Fuera de Bogota y sin regla especial: 0%.",
    ],
  },
  {
    key: "jhonatan",
    seller: "Jhonatan",
    rules: [
      "Actualmente no tiene reglas especiales configuradas.",
      "Usa el porcentaje general digitado en el campo % Comision.",
      "No tiene descuento fijo mensual configurado.",
      "No tiene retencion especial configurada; por defecto aplica 0%.",
    ],
  },
];

const commandState = {
  conditionsOpen: false,
};

const FAMILY_CUSTOMERS = [
  "GRUPO OPTICO DEL CARIBE RUEDA S.A.S",
  "GRUPO OPTICO S.A.S",
  "GRUPO OPTICO S.A.S (NUEVA OPTICA UNIVISION JR)",
  "GRUPO OPTICO S.A.S (OPTICA SELECTA CABECERA)",
  "GRUPO OPTICO S.A.S (OPTICA SELECTA CACIQUE)",
  "GRUPO OPTICO S.A.S (OPTICA SELECTA CAÑAVERAL)",
  "GRUPO OPTICO S.A.S (OPTICA SELECTA CENTRO)",
  "GRUPO OPTICO S.A.S (OPTICA SELECTA LEBRIJA)",
  "GRUPO OPTICO S.A.S (OPTICA SELECTA MEGA MALL)",
  "GRUPO OPTICO S.A.S (OPTICA SELECTA PIEDECUESTA)",
  "GRUPO OPTICO S.A.S (OPTICA SELECTA SAN GIL)",
  "LABORATORIO UNILENTES S.A.S",
  "MEGA OPTICAS SOL Y GAFAS S.A.S",
  "OPTICA SOL Y GAFAS DR COL S.A.S",
  "OPTICAS SOL Y GAFAS S.A.S",
  "OPTICAS SOL Y GAFAS S.A.S ",
  "OPTICAS SOL Y GAFAS S.A.S ( SEDE PEREIRA )",
  "OPTICAS SOL Y GAFAS S.A.S (SEDE BUCARAMANGA)",
  "RUEDA FLOREZ ISABELLA",
  "RUEDA MAYORGA GLADYS",
  "RUEDA MAYORGA JORGE ( AGUACHICA) ",
  "RUEDA MAYORGA JORGE ( OCAÑA) ",
  "RUEDA MAYORGA JORGE (MEGA OPTICA SELECTA)",
  "RUEDA MAYORGA JORGE (OPTICA SELECTA CABECERA)",
  "RUEDA MAYORGA JORGE (OPTICA SELECTA LA ISLA)",
  "UMI SALUD VISUAL S.A.S",
  "UMI SALUD VISUAL S.A.S (SEDE BUCARAMANGA)",
  "UMI SALUD VISUAL S.A.S (SEDE PEREIRA)",
  "VISUALDENT SALUD S.A.S",
];

const CONSIGNMENT_CUSTOMERS = [
  "OPTICA COLSANITAS S.A.S",
  "OPTICA COLSANITAS S.A.S ",
  "SERVICIOS DE SALUD IPS SURAMERICANA S.A.S",
  "SERVICIOS MEDICOS Y OFTALMOLOGICOS S.A.S",
  "SERVIOPTICA S.A.S",
  "VISUAL POINT S.A.S",
  "IMEVI S.A.S",
];










const CUSTOMER_CLASSIFICATION = new Map([
  ...FAMILY_CUSTOMERS.map((name) => [normalizeHeader(name), "FAMILIA"]),
  ...CONSIGNMENT_CUSTOMERS.map((name) => [normalizeHeader(name), "CONSIGNACION"]),
]);

const resultsBody = document.querySelector("#resultsTable tbody");
const sellerBody = document.querySelector("#sellerTable tbody");
const detailBody = document.querySelector("#detailTable tbody");

fileRuedaInput?.addEventListener("change", () => handleCompanyFileChange(COMPANY_RUEDA, fileRuedaInput));
fileLamarInput?.addEventListener("change", () => handleCompanyFileChange(COMPANY_LAMAR, fileLamarInput));
fileAbelardoInput?.addEventListener("change", () => handleCompanyFileChange(COMPANY_ABELARDO, fileAbelardoInput));
processBtn?.addEventListener("click", processLiquidation);
monthFilter?.addEventListener("change", renderAll);
companyFilter?.addEventListener("change", renderAll);
sellerFilter?.addEventListener("change", renderAll);
customerFilter?.addEventListener("change", renderAll);
commissionRateInput?.addEventListener("input", () => {
  if (state.processedRows.length) {
    processLiquidation();
  }
});

document.addEventListener("keydown", handleGlobalShortcut);

if (typeof XLSX === "undefined") {
  notify(
    "No se pudo cargar la libreria de Excel (XLSX). Verifica internet o guarda la libreria localmente para usar la pagina sin conexion.",
    true
  );
}

function notify(text, isError = false) {
  if (!message) {
    console[isError ? "error" : "log"](text);
    return;
  }

  message.textContent = text;
  message.style.color = isError ? "#b91c1c" : "#0f172a";
}

function normalizeHeader(value) {
  return String(value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9]+/g, " ")
    .trim()
    .replace(/\s+/g, " ")
    .toLowerCase();
}

function resolveCanonicalColumn(headerText) {
  const normalized = normalizeHeader(headerText);
  if (!normalized) return null;

  for (const [column, aliases] of COLUMN_ALIAS_SETS.entries()) {
    if (aliases.has(normalized)) return column;
  }

  for (const [column, aliases] of COLUMN_ALIAS_SETS.entries()) {
    for (const alias of aliases) {
      if (!alias) continue;

      const aliasWords = alias.split(" ").filter(Boolean);
      if (
        aliasWords.length >= 2 &&
        aliasWords.every((word) => normalized.includes(word))
      ) {
        return column;
      }

      if (alias.length >= 7 && (normalized.includes(alias) || alias.includes(normalized))) {
        return column;
      }
    }
  }

  return null;
}

function firstNonEmptyRowIndex(rowsAsMatrix) {
  for (let i = 0; i < rowsAsMatrix.length; i += 1) {
    const row = rowsAsMatrix[i] ?? [];
    const hasAnyValue = row.some((cell) => {
      if (cell == null) return false;
      if (typeof cell === "string") return Boolean(cell.trim());
      return true;
    });
    if (hasAnyValue) return i;
  }
  return -1;
}

function findHeaderRowIndex(rowsAsMatrix) {
  const searchLimit = Math.min(rowsAsMatrix.length, 60);
  let best = {
    rowIndex: -1,
    requiredMatches: 0,
    expectedMatches: 0,
    filledRequiredColumns: 0,
  };

  for (let rowIndex = 0; rowIndex < searchLimit; rowIndex += 1) {
    const headerRow = rowsAsMatrix[rowIndex] ?? [];
    if (isCompletelyEmptyRow(headerRow)) continue;

    const headerIndexMap = buildHeaderIndexMap(headerRow);
    const expectedMatches = headerIndexMap.size;
    const requiredMatches = REQUIRED_FOR_CALC.filter((col) => headerIndexMap.has(col)).length;

    if (!expectedMatches) continue;

    const canonicalRows = buildCanonicalRowsFromMatrix(rowsAsMatrix, rowIndex, headerIndexMap);
    const filledRequiredColumns = REQUIRED_FOR_CALC.filter((column) => {
      return canonicalRows.some((row) => row[column] != null && String(row[column]).trim() !== "");
    }).length;

    const isBetter =
      filledRequiredColumns > best.filledRequiredColumns ||
      (filledRequiredColumns === best.filledRequiredColumns && requiredMatches > best.requiredMatches) ||
      (filledRequiredColumns === best.filledRequiredColumns &&
        requiredMatches === best.requiredMatches &&
        expectedMatches > best.expectedMatches);

    if (isBetter) {
      best = { rowIndex, requiredMatches, expectedMatches, filledRequiredColumns };
    }
  }

  return best.filledRequiredColumns >= 3 || best.requiredMatches >= 4 ? best.rowIndex : -1;
}

function buildHeaderIndexMap(headerRow) {
  const indexMap = new Map();

  headerRow.forEach((cell, idx) => {
    const canonical = resolveCanonicalColumn(cell);
    if (canonical && !indexMap.has(canonical)) {
      indexMap.set(canonical, idx);
    }
  });

  return indexMap;
}

function isCompletelyEmptyRow(row) {
  return row.every((cell) => {
    if (cell == null) return true;
    if (typeof cell === "string") return !cell.trim();
    return false;
  });
}

function buildCanonicalRowsFromMatrix(rowsAsMatrix, headerRowIndex, headerIndexMap) {
  const dataRows = [];

  for (let i = headerRowIndex + 1; i < rowsAsMatrix.length; i += 1) {
    const rawRow = rowsAsMatrix[i] ?? [];
    if (isCompletelyEmptyRow(rawRow)) continue;

    const canonical = {};
    EXPECTED_COLUMNS.forEach((column) => {
      const columnIndex = headerIndexMap.get(column);
      canonical[column] = typeof columnIndex === "number" ? rawRow[columnIndex] ?? null : null;
    });

    dataRows.push(canonical);
  }

  return dataRows;
}

function parseNumber(value) {
  if (typeof value === "number") return Number.isFinite(value) ? value : 0;
  if (value == null) return 0;

  let txt = String(value).trim();
  if (!txt) return 0;

  txt = txt.replace(/\s/g, "");
  const hasComma = txt.includes(",");
  const hasDot = txt.includes(".");

  if (hasComma && hasDot) {
    const lastComma = txt.lastIndexOf(",");
    const lastDot = txt.lastIndexOf(".");
    if (lastComma > lastDot) {
      txt = txt.replace(/\./g, "").replace(/,/g, ".");
    } else {
      txt = txt.replace(/,/g, "");
    }
  } else if (hasComma && !hasDot) {
    txt = txt.replace(/,/g, ".");
  }

  txt = txt.replace(/[^0-9.-]/g, "");
  const parsed = Number(txt);
  return Number.isFinite(parsed) ? parsed : 0;
}

function parseDate(value) {
  if (value instanceof Date && !Number.isNaN(value.getTime())) return value;

  if (typeof value === "number") {
    const dateCode = XLSX.SSF.parse_date_code(value);
    if (dateCode) {
      return new Date(dateCode.y, dateCode.m - 1, dateCode.d);
    }
  }

  if (typeof value === "string") {
    const clean = value.trim();
    if (!clean) return null;

    const direct = new Date(clean);
    if (!Number.isNaN(direct.getTime())) return direct;

    const dmY = clean.match(/^(\d{1,2})[\/-](\d{1,2})[\/-](\d{2,4})$/);
    if (dmY) {
      const d = Number(dmY[1]);
      const m = Number(dmY[2]) - 1;
      let y = Number(dmY[3]);
      if (y < 100) y += 2000;
      const dt = new Date(y, m, d);
      if (!Number.isNaN(dt.getTime())) return dt;
    }
  }

  return null;
}

function monthKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function monthLabel(key) {
  const [year, month] = key.split("-");
  return `${month}/${year}`;
}

function isFreightConcept(conceptName) {
  const normalized = normalizeHeader(conceptName);
  if (!normalized) return false;
  return normalized.includes("flete") || normalized.includes("fletes") || normalized.includes("felte");
}

function classifyCustomer(customerName) {
  const normalized = normalizeHeader(customerName);
  if (!normalized) return "NORMAL";
  return CUSTOMER_CLASSIFICATION.get(normalized) ?? "NORMAL";
}

function isImeviCustomer(customerName) {
  const normalized = normalizeHeader(customerName);
  return normalized.includes("imevi") || normalized.includes("imvei");
}

function isBogotaCity(cityName) {
  const normalized = normalizeHeader(cityName);
  return normalized.includes("bogota");
}

function isColsanitasCustomer(customerName) {
  const normalized = normalizeHeader(customerName);
  return normalized.includes("optica colsanitas");
}

function isJoseAlfredoSeller(sellerName) {
  const normalized = normalizeHeader(sellerName);
  if (!normalized) return false;
  if (normalized === SELLER_JOSE_ALFREDO) return true;
  return normalized.includes("jose alfredo");
}

function renderSellerConditions(filterKey = "all") {
  if (!conditionsBody || !conditionsSection) return;

  const keyNormalized = normalizeHeader(filterKey);
  const rowsToRender =
    !keyNormalized || keyNormalized === "all" || keyNormalized === "todos"
      ? SELLER_CONDITIONS
      : SELLER_CONDITIONS.filter((item) => item.key === keyNormalized);

  conditionsBody.innerHTML = "";

  if (!rowsToRender.length) {
    conditionsBody.innerHTML = "<p>No hay condiciones para el vendedor solicitado.</p>";
    conditionsSection.classList.remove("hidden");
    return;
  }

  rowsToRender.forEach((item) => {
    const card = document.createElement("article");
    card.className = "condition-card";

    const title = document.createElement("h3");
    title.textContent = item.seller;
    card.appendChild(title);

    const list = document.createElement("ul");
    item.rules.forEach((ruleText) => {
      const li = document.createElement("li");
      li.textContent = ruleText;
      list.appendChild(li);
    });

    card.appendChild(list);
    conditionsBody.appendChild(card);
  });

  conditionsSection.classList.remove("hidden");
}

function handleGlobalShortcut(event) {
  const target = event.target;
  const isTypingTarget =
    target instanceof HTMLInputElement ||
    target instanceof HTMLTextAreaElement ||
    target instanceof HTMLSelectElement ||
    target?.isContentEditable;

  if (
    event.altKey &&
    !event.ctrlKey &&
    !event.metaKey &&
    normalizeHeader(event.key) === PRIVATE_CONDITIONS_SHORTCUT_KEY
  ) {
    if (isTypingTarget) return;

    event.preventDefault();
    commandState.conditionsOpen = !commandState.conditionsOpen;

    if (commandState.conditionsOpen) {
      renderSellerConditions("all");
      notify("Panel privado abierto.");
    } else {
      conditionsSection?.classList.add("hidden");
      notify("Panel privado cerrado.");
    }

    return;
  }

  if (event.key === "Escape" && commandState.conditionsOpen) {
    commandState.conditionsOpen = false;
    conditionsSection?.classList.add("hidden");
    notify("Panel privado cerrado.");
  }
}

function getNataliaNormalRate(totalSales) {
  if (totalSales <= 5000000) return 0;
  if (totalSales <= 10000000) return 2;
  if (totalSales <= 20000000) return 3;
  if (totalSales <= 30000000) return 4;
  return 5;
}

function getKarenRate(totalSales) {
  if (totalSales <= 199999999) return 1.5;
  if (totalSales <= 249999999) return 2;
  return 2.5;
}

function getJoseBogotaRate(totalSales) {
  if (totalSales >= 80000000) return 1.5;
  if (totalSales >= 60000000) return 1;
  return 0;
}

function getRetentionRateForRow(row) {
  const sellerNormalized = normalizeHeader(row["Vendedor Nombre"]);
  return sellerNormalized === SELLER_NATALIA_REYES ? NATALIA_RETENTION_RATE : 0;
}

function getSellerMonthKey(row) {
  const sellerName = String(row["Vendedor Nombre"] ?? "SIN_NOMBRE").trim() || "SIN_NOMBRE";
  return `${normalizeHeader(sellerName)}::${row.__monthKey}`;
}

function getInvoiceAggregationKey(row) {
  const sellerName = String(row["Vendedor Nombre"] ?? "").trim();
  const customerId = String(row["Beneficiario Identidad"] ?? "").trim();
  const customerName = String(row["Beneficiario Nombre"] ?? "").trim();
  const prefixValue = String(row["Documento"] ?? "").trim();
  const consecutiveValue = String(row["CONSECUTIVO"] ?? "").trim();

  return [
    row.__company ?? "",
    row.__monthKey ?? "",
    prefixValue,
    consecutiveValue,
    sellerName,
    customerId,
    customerName,
  ].join("::");
}

function resolveRowCommissionRate(
  row,
  defaultRate,
  nataliaNormalTotalsByMonth,
  karenTotalsByMonth,
  joseBogotaTotalsByMonth,
  joseColsanitasTotalsByMonth
) {
  const sellerNormalized = normalizeHeader(row["Vendedor Nombre"]);
  if (sellerNormalized === SELLER_KAREN_TORRADO) {
    const monthlyTotal = karenTotalsByMonth.get(row.__monthKey) ?? 0;
    return getKarenRate(monthlyTotal);
  }

  if (isJoseAlfredoSeller(row["Vendedor Nombre"])) {
    if (isColsanitasCustomer(row["Beneficiario Nombre"])) {
      const monthlyColsanitasTotal = joseColsanitasTotalsByMonth.get(row.__monthKey) ?? 0;
      if (monthlyColsanitasTotal >= 45000000) return 2;
    }

    if (row.__customerType === "CONSIGNACION") {
      return 0;
    }

    if (isBogotaCity(row["Ciudad Nombre"])) {
      const monthlyBogotaTotal = joseBogotaTotalsByMonth.get(row.__monthKey) ?? 0;
      return getJoseBogotaRate(monthlyBogotaTotal);
    }

    return 0;
  }

  if (sellerNormalized !== SELLER_NATALIA_REYES) return defaultRate;

  if (isImeviCustomer(row["Beneficiario Nombre"])) return 2;
  if (row.__customerType === "FAMILIA") return 2;

  if (row.__customerType === "NORMAL") {
    const monthlyTotal = nataliaNormalTotalsByMonth.get(row.__monthKey) ?? 0;
    return getNataliaNormalRate(monthlyTotal);
  }

  // Por ahora, para consignacion diferente de IMEVI no hay regla definida.
  return 0;
}

function formatMoney(value) {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 2,
  }).format(value || 0);
}

function getCanonicalRow(rawRow) {
  const normalizedMap = new Map();
  Object.keys(rawRow).forEach((key) => {
    normalizedMap.set(normalizeHeader(key), rawRow[key]);
  });

  const canonical = {};
  EXPECTED_COLUMNS.forEach((column) => {
    canonical[column] = normalizedMap.get(normalizeHeader(column)) ?? null;
  });

  return canonical;
}

async function parseExcelFile(file) {
  if (!file) return;

  if (typeof XLSX === "undefined") {
    throw new Error("La libreria XLSX no esta disponible. Revisa la conexion a internet.");
  }

  const arrayBuffer = await file.arrayBuffer();
  const workbook = XLSX.read(arrayBuffer, { type: "array" });
  const firstSheetName = workbook.SheetNames[0];
  const worksheet = workbook.Sheets[firstSheetName];

  const rowsAsMatrix = XLSX.utils.sheet_to_json(worksheet, {
    header: 1,
    defval: null,
    raw: true,
    blankrows: false,
  });

  if (!rowsAsMatrix.length) {
    throw new Error("El archivo no contiene filas con datos.");
  }

  let headerRowIndex = findHeaderRowIndex(rowsAsMatrix);
  if (headerRowIndex < 0) {
    headerRowIndex = firstNonEmptyRowIndex(rowsAsMatrix);
  }

  if (headerRowIndex < 0) {
    throw new Error("No se pudo encontrar una fila de encabezados en el archivo.");
  }

  const headerIndexMap = buildHeaderIndexMap(rowsAsMatrix[headerRowIndex] ?? []);
  const canonicalRows = buildCanonicalRowsFromMatrix(rowsAsMatrix, headerRowIndex, headerIndexMap);

  if (!canonicalRows.length) {
    throw new Error("Se encontró encabezado, pero no hay filas de facturas debajo.");
  }

  const missing = REQUIRED_FOR_CALC.filter((column) => {
    return canonicalRows.every((row) => {
      const value = row[column];
      return value == null || String(value).trim() === "";
    });
  });

  if (missing.length) {
    throw new Error(`Faltan columnas obligatorias para liquidar: ${missing.join(", ")}`);
  }

  return canonicalRows;
}

function updateProcessAvailability() {
  const hasAnyFile = Object.values(state.rawRowsByCompany).some((rows) => rows.length > 0);
  if (processBtn) {
    processBtn.disabled = !hasAnyFile;
  }
}

async function handleCompanyFileChange(companyName, inputElement) {
  const file = inputElement.files?.[0];
  if (!file) return;

  resetOutputs();
  state.rawRowsByCompany[companyName] = [];
  state.fileNamesByCompany[companyName] = "";
  updateProcessAvailability();
  notify(`Leyendo archivo de ${companyName}...`);

  try {
    const canonicalRows = await parseExcelFile(file);
    state.rawRowsByCompany[companyName] = canonicalRows;
    state.fileNamesByCompany[companyName] = file.name;
    updateProcessAvailability();

    const companyStatus = [COMPANY_RUEDA, COMPANY_LAMAR, COMPANY_ABELARDO]
      .map((company) => `${state.rawRowsByCompany[company].length ? "✅" : "⏳"} ${company}`)
      .join(" | ");

    notify(
      `Archivo cargado para ${companyName}: ${file.name}. Filas detectadas: ${canonicalRows.length}. Estado: ${companyStatus}`
    );
  } catch (error) {
    state.rawRowsByCompany[companyName] = [];
    state.fileNamesByCompany[companyName] = "";
    updateProcessAvailability();
    notify(`No se pudo cargar ${companyName}: ${error.message}`, true);
  }
}

function processLiquidation() {
  const allRows = [
    ...state.rawRowsByCompany[COMPANY_RUEDA].map((row) => ({ ...row, __company: COMPANY_RUEDA })),
    ...state.rawRowsByCompany[COMPANY_LAMAR].map((row) => ({ ...row, __company: COMPANY_LAMAR })),
    ...state.rawRowsByCompany[COMPANY_ABELARDO].map((row) => ({ ...row, __company: COMPANY_ABELARDO })),
  ];

  if (!allRows.length) {
    notify("Debes cargar al menos un archivo para procesar la información.", true);
    return;
  }

  const commissionRate = parseNumber(commissionRateInput.value);
  if (commissionRate < 0) {
    notify("El porcentaje de comisión no puede ser negativo.", true);
    return;
  }

  const preparedRows = allRows
    .map((row) => {
      if (isFreightConcept(row["Nombre Concepto"])) {
        return null;
      }

      const date = parseDate(row["Fecha"]);
      if (!date) return null;

      const vrNeto = parseNumber(row["Vr. Neto"]);
      const vrIva = parseNumber(row["Vr. Imp. IVA"]);
      const vrDescuento = parseNumber(row["Vr. Descuento"]);
      const subtotal = vrNeto - vrIva - vrDescuento;
      const customerType = classifyCustomer(row["Beneficiario Nombre"]);

      return {
        ...row,
        __monthKey: monthKey(date),
        __date: date,
        __vrNeto: vrNeto,
        __vrIva: vrIva,
        __vrDescuento: vrDescuento,
        __customerType: customerType,
        __subtotal: subtotal,
      };
    })
    .filter(Boolean);

  const nataliaNormalTotalsByMonth = new Map();
  const karenTotalsByMonth = new Map();
  const joseBogotaTotalsByMonth = new Map();
  const joseColsanitasTotalsByMonth = new Map();
  preparedRows.forEach((row) => {
    const sellerNormalized = normalizeHeader(row["Vendedor Nombre"]);

    if (sellerNormalized === SELLER_KAREN_TORRADO) {
      const currentKaren = karenTotalsByMonth.get(row.__monthKey) ?? 0;
      karenTotalsByMonth.set(row.__monthKey, currentKaren + row.__subtotal);
    }

    if (isJoseAlfredoSeller(row["Vendedor Nombre"])) {
      if (isBogotaCity(row["Ciudad Nombre"]) && row.__customerType !== "CONSIGNACION") {
        const currentJoseBogota = joseBogotaTotalsByMonth.get(row.__monthKey) ?? 0;
        joseBogotaTotalsByMonth.set(row.__monthKey, currentJoseBogota + row.__subtotal);
      }

      if (isColsanitasCustomer(row["Beneficiario Nombre"])) {
        const currentJoseColsanitas = joseColsanitasTotalsByMonth.get(row.__monthKey) ?? 0;
        joseColsanitasTotalsByMonth.set(row.__monthKey, currentJoseColsanitas + row.__subtotal);
      }
    }

    if (sellerNormalized !== SELLER_NATALIA_REYES) return;
    if (row.__customerType !== "NORMAL") return;

    const current = nataliaNormalTotalsByMonth.get(row.__monthKey) ?? 0;
    nataliaNormalTotalsByMonth.set(row.__monthKey, current + row.__subtotal);
  });

  const processedRows = preparedRows.map((row) => {
    const rowCommissionRate = resolveRowCommissionRate(
      row,
      commissionRate,
      nataliaNormalTotalsByMonth,
      karenTotalsByMonth,
      joseBogotaTotalsByMonth,
      joseColsanitasTotalsByMonth
    );
    const commissionValue = (row.__subtotal * rowCommissionRate) / 100;
    const retentionRate = getRetentionRateForRow(row);
    const retentionValue = (commissionValue * retentionRate) / 100;
    return {
      ...row,
      __commissionRate: rowCommissionRate,
      __commissionValue: commissionValue,
      __monthlyDiscountValue: 0,
      __retentionRate: retentionRate,
      __retentionValue: retentionValue,
      __netCommissionValue: commissionValue - retentionValue,
    };
  });

  const karenMonthlyBuckets = new Map();
  processedRows.forEach((row) => {
    const sellerNormalized = normalizeHeader(row["Vendedor Nombre"]);
    if (sellerNormalized !== SELLER_KAREN_TORRADO) return;

    const key = getSellerMonthKey(row);
    if (!karenMonthlyBuckets.has(key)) {
      karenMonthlyBuckets.set(key, {
        commissionValue: 0,
      });
    }

    const bucket = karenMonthlyBuckets.get(key);
    bucket.commissionValue += row.__commissionValue;
  });

  processedRows.forEach((row) => {
    const sellerNormalized = normalizeHeader(row["Vendedor Nombre"]);
    if (sellerNormalized !== SELLER_KAREN_TORRADO) return;

    const key = getSellerMonthKey(row);
    const bucket = karenMonthlyBuckets.get(key);
    const monthlyCommission = bucket?.commissionValue ?? 0;
    const commissionShare = monthlyCommission > 0 ? row.__commissionValue / monthlyCommission : 0;
    const monthlyDiscountApplied = Math.min(KAREN_MONTHLY_DISCOUNT, monthlyCommission);
    const commissionAfterDiscount = Math.max(monthlyCommission - monthlyDiscountApplied, 0);
    const monthlyRetentionValue = (commissionAfterDiscount * KAREN_RETENTION_RATE) / 100;

    row.__monthlyDiscountValue = monthlyDiscountApplied * commissionShare;
    row.__retentionRate = KAREN_RETENTION_RATE;
    row.__retentionValue = monthlyRetentionValue * commissionShare;
    row.__netCommissionValue = row.__commissionValue - row.__monthlyDiscountValue - row.__retentionValue;
  });

  state.processedRows = processedRows;
  state.groupedRows = groupBySellerAndMonth(processedRows);
  state.organizedRows = buildOrganizedRows(processedRows);

  populateFilters();
  renderAll();

  notify(
    `Proceso generado. Filas válidas: ${processedRows.length}. Registros agrupados: ${state.groupedRows.length}. Facturas organizadas: ${state.organizedRows.length}.`
  );
}

function buildOrganizedRows(rows) {
  const groupedMap = new Map();

  rows.forEach((row) => {
    const sellerName = String(row["Vendedor Nombre"] ?? "").trim();
    const customerId = String(row["Beneficiario Identidad"] ?? "").trim();
    const customerName = String(row["Beneficiario Nombre"] ?? "").trim();
    const prefixValue = String(row["Documento"] ?? "").trim();
    const consecutiveValue = String(row["CONSECUTIVO"] ?? "").trim();
    const consecValue = `${prefixValue}${prefixValue && consecutiveValue ? " " : ""}${consecutiveValue}`;
    const cityValue = String(row["Ciudad Nombre"] ?? "").trim();
    const key = getInvoiceAggregationKey(row);

    if (!groupedMap.has(key)) {
      groupedMap.set(key, {
        consec: consecValue,
        empresaReal: row.__company ?? "",
        empresa: row.__company ?? "",
        prefijo: prefixValue,
        numeroDoc: consecutiveValue,
        fecha: row.__date,
        asesor: sellerName,
        nit: customerId,
        cliente: customerName,
        cartera: row.__customerType ?? "NORMAL",
        ciudad: cityValue,
        valor: 0,
        cantidad: 0,
      });
    }

    const bucket = groupedMap.get(key);
    bucket.valor += row.__subtotal;
    bucket.cantidad += parseNumber(row["Cantidad"]);
  });

  return [...groupedMap.values()].sort((a, b) => {
    if (a.empresaReal !== b.empresaReal) return a.empresaReal.localeCompare(b.empresaReal);
    if (a.fecha && b.fecha) return a.fecha - b.fecha;
    return a.cliente.localeCompare(b.cliente);
  });
}

function groupBySellerAndMonth(rows) {
  const groupedMap = new Map();

  rows.forEach((row) => {
    const sellerId = String(row["Vendedor Identidad"] ?? "SIN_ID").trim() || "SIN_ID";
    const sellerName = String(row["Vendedor Nombre"] ?? "SIN_NOMBRE").trim() || "SIN_NOMBRE";
    const company = row.__company ?? "SIN_EMPRESA";
    const key = `${company}::${row.__monthKey}::${sellerId}`;

    if (!groupedMap.has(key)) {
      groupedMap.set(key, {
        company,
        monthKey: row.__monthKey,
        sellerId,
        sellerName,
        invoiceKeys: new Set(),
        subtotal: 0,
        commissionRates: new Set(),
        commissionValue: 0,
        retentionValue: 0,
        netCommissionValue: 0,
      });
    }

    const bucket = groupedMap.get(key);
    bucket.invoiceKeys.add(getInvoiceAggregationKey(row));
    bucket.subtotal += row.__subtotal;
    bucket.commissionRates.add(row.__commissionRate);
    bucket.commissionValue += row.__commissionValue;
    bucket.retentionValue += row.__retentionValue;
    bucket.netCommissionValue += row.__netCommissionValue;
  });

  return [...groupedMap.values()]
    .map((bucket) => {
      const rates = [...bucket.commissionRates].sort((a, b) => a - b);
      const commissionRateLabel =
        rates.length === 1 ? `${rates[0].toFixed(2)}%` : `Variable (${rates.map((r) => `${r.toFixed(2)}%`).join(", ")})`;

      return {
        ...bucket,
        invoices: bucket.invoiceKeys.size,
        commissionRateLabel,
      };
    })
    .sort((a, b) => {
    if (a.company !== b.company) return a.company.localeCompare(b.company);
    if (a.monthKey !== b.monthKey) return a.monthKey.localeCompare(b.monthKey);
    return a.sellerName.localeCompare(b.sellerName);
  });
}

function populateFilters() {
  const monthKeys = [...new Set(state.processedRows.map((row) => row.__monthKey))].sort();
  monthFilter.innerHTML = `<option value="ALL">Todos</option>`;

  monthKeys.forEach((mk) => {
    const opt = document.createElement("option");
    opt.value = mk;
    opt.textContent = monthLabel(mk);
    monthFilter.appendChild(opt);
  });

  monthFilter.disabled = monthKeys.length === 0;

  const companies = [...new Set(state.processedRows.map((row) => row.__company))].sort();
  companyFilter.innerHTML = `<option value="ALL">Todas</option>`;
  companies.forEach((company) => {
    const opt = document.createElement("option");
    opt.value = company;
    opt.textContent = company;
    companyFilter.appendChild(opt);
  });
  companyFilter.disabled = companies.length === 0;

  const sellers = [...new Set(state.processedRows.map((row) => String(row["Vendedor Nombre"] ?? "").trim()).filter(Boolean))].sort(
    (a, b) => a.localeCompare(b)
  );
  sellerFilter.innerHTML = `<option value="ALL">Todos</option>`;
  sellers.forEach((seller) => {
    const opt = document.createElement("option");
    opt.value = seller;
    opt.textContent = seller;
    sellerFilter.appendChild(opt);
  });
  sellerFilter.disabled = sellers.length === 0;

  const customers = [
    ...new Set(state.processedRows.map((row) => String(row["Beneficiario Nombre"] ?? "").trim()).filter(Boolean)),
  ].sort((a, b) => a.localeCompare(b));
  customerFilter.innerHTML = `<option value="ALL">Todos</option>`;
  customers.forEach((customer) => {
    const opt = document.createElement("option");
    opt.value = customer;
    opt.textContent = customer;
    customerFilter.appendChild(opt);
  });
  customerFilter.disabled = customers.length === 0;
}

function renderAll() {
  const selectedMonth = monthFilter.value || "ALL";
  const selectedCompany = companyFilter.value || "ALL";
  const selectedSeller = sellerFilter.value || "ALL";
  const selectedCustomer = customerFilter.value || "ALL";

  const filteredOrganizedRows = state.organizedRows.filter((row) => {
    const organizedMonthKey = row.fecha ? monthKey(row.fecha) : "";
    if (selectedMonth !== "ALL" && organizedMonthKey !== selectedMonth) return false;
    if (selectedCompany !== "ALL" && row.empresaReal !== selectedCompany) return false;
    if (selectedSeller !== "ALL" && row.asesor !== selectedSeller) return false;
    if (selectedCustomer !== "ALL" && row.cliente !== selectedCustomer) return false;
    return true;
  });

  const rowsForSellerConsolidated = state.processedRows.filter((row) => {
    if (selectedMonth !== "ALL" && row.__monthKey !== selectedMonth) return false;
    if (selectedSeller !== "ALL" && String(row["Vendedor Nombre"] ?? "").trim() !== selectedSeller) return false;
    if (selectedCustomer !== "ALL" && String(row["Beneficiario Nombre"] ?? "").trim() !== selectedCustomer) return false;
    return true;
  });

  const detailRows = state.processedRows.filter((row) => {
    if (selectedMonth !== "ALL" && row.__monthKey !== selectedMonth) return false;
    if (selectedCompany !== "ALL" && row.__company !== selectedCompany) return false;
    if (selectedSeller !== "ALL" && String(row["Vendedor Nombre"] ?? "").trim() !== selectedSeller) return false;
    if (selectedCustomer !== "ALL" && String(row["Beneficiario Nombre"] ?? "").trim() !== selectedCustomer) return false;
    return true;
  });

  const grouped = groupBySellerAndMonth(detailRows);

  renderSummary(detailRows, filteredOrganizedRows);
  renderSellerTable(rowsForSellerConsolidated);
  renderGroupedTable(grouped);
  renderDetailTable(filteredOrganizedRows);
}

function renderSummary(rows, organizedRows) {
  const subtotal = rows.reduce((acc, row) => acc + row.__subtotal, 0);
  const commission = rows.reduce((acc, row) => acc + row.__commissionValue, 0);
  const retention = rows.reduce((acc, row) => acc + row.__retentionValue, 0);
  const netCommission = rows.reduce((acc, row) => acc + row.__netCommissionValue, 0);

  kpiInvoices.textContent = String(organizedRows.length);
  kpiSubtotal.textContent = formatMoney(subtotal);
  kpiCommission.textContent = formatMoney(commission);
  kpiRetention.textContent = formatMoney(retention);
  kpiNetCommission.textContent = formatMoney(netCommission);

  summary.classList.remove("hidden");
}

function renderSellerTable(rows) {
  sellerBody.innerHTML = "";

  const groupedBySeller = new Map();
  rows.forEach((row) => {
    const sellerId = String(row["Vendedor Identidad"] ?? "SIN_ID").trim() || "SIN_ID";
    const sellerName = String(row["Vendedor Nombre"] ?? "SIN_NOMBRE").trim() || "SIN_NOMBRE";
    const sellerKey = normalizeHeader(sellerName) || "sin_nombre";

    if (!groupedBySeller.has(sellerKey)) {
      groupedBySeller.set(sellerKey, {
        sellerIds: new Set(),
        sellerName,
        companies: new Set(),
        invoiceKeys: new Set(),
        subtotal: 0,
        commissionValue: 0,
        monthlyDiscountValue: 0,
        retentionValue: 0,
        netCommissionValue: 0,
      });
    }

    const bucket = groupedBySeller.get(sellerKey);
    bucket.sellerIds.add(sellerId);
    bucket.companies.add(row.__company ?? "SIN_EMPRESA");
    bucket.invoiceKeys.add(getInvoiceAggregationKey(row));
    bucket.subtotal += row.__subtotal;
    bucket.commissionValue += row.__commissionValue;
    bucket.monthlyDiscountValue += row.__monthlyDiscountValue;
    bucket.retentionValue += row.__retentionValue;
    bucket.netCommissionValue += row.__netCommissionValue;
  });

  [...groupedBySeller.values()]
    .sort((a, b) => a.sellerName.localeCompare(b.sellerName))
    .forEach((row) => {
      const baseAfterDiscount = row.commissionValue - row.monthlyDiscountValue;
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${[...row.sellerIds].sort().join(" / ")}</td>
        <td>${row.sellerName}</td>
        <td>${[...row.companies].sort().join(" + ")}</td>
        <td>${row.invoiceKeys.size}</td>
        <td>${formatMoney(row.subtotal)}</td>
        <td>${formatMoney(row.commissionValue)}</td>
        <td>${formatMoney(row.monthlyDiscountValue)}</td>
        <td>${formatMoney(baseAfterDiscount)}</td>
        <td>${formatMoney(row.retentionValue)}</td>
        <td>${formatMoney(row.netCommissionValue)}</td>
      `;
      sellerBody.appendChild(tr);
    });

  sellerSection.classList.remove("hidden");
}

function renderGroupedTable(groupedRows) {
  resultsBody.innerHTML = "";

  groupedRows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.company}</td>
      <td>${monthLabel(row.monthKey)}</td>
      <td>${row.sellerName}</td>
      <td>${row.invoices}</td>
      <td>${formatMoney(row.subtotal)}</td>
      <td>${row.commissionRateLabel}</td>
      <td>${formatMoney(row.commissionValue)}</td>
      <td>${formatMoney(row.retentionValue)}</td>
      <td>${formatMoney(row.netCommissionValue)}</td>
    `;
    resultsBody.appendChild(tr);
  });

  resultsSection.classList.remove("hidden");
}

function renderDetailTable(organizedRows) {
  detailBody.innerHTML = "";

  organizedRows
    .slice()
    .sort((a, b) => (a.fecha && b.fecha ? a.fecha - b.fecha : 0))
    .forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.consec}</td>
        <td>${row.empresaReal}</td>
        <td>${row.empresa}</td>
        <td>${row.prefijo}</td>
        <td>${row.numeroDoc}</td>
        <td>${row.fecha ? row.fecha.toLocaleDateString("es-CO") : ""}</td>
        <td>${row.asesor}</td>
        <td>${row.nit}</td>
        <td>${row.cliente}</td>
        <td>${row.cartera}</td>
        <td>${row.ciudad}</td>
        <td>${formatMoney(row.valor)}</td>
        <td>${row.cantidad}</td>
      `;
      detailBody.appendChild(tr);
    });

  detailSection.classList.remove("hidden");
}

function resetOutputs() {
  state.processedRows = [];
  state.groupedRows = [];
  state.organizedRows = [];
  monthFilter.disabled = true;
  monthFilter.innerHTML = `<option value="ALL">Todos</option>`;
  companyFilter.disabled = true;
  companyFilter.innerHTML = `<option value="ALL">Todas</option>`;
  sellerFilter.disabled = true;
  sellerFilter.innerHTML = `<option value="ALL">Todos</option>`;
  customerFilter.disabled = true;
  customerFilter.innerHTML = `<option value="ALL">Todos</option>`;

  summary.classList.add("hidden");
  sellerSection.classList.add("hidden");
  resultsSection.classList.add("hidden");
  detailSection.classList.add("hidden");

  sellerBody.innerHTML = "";
  resultsBody.innerHTML = "";
  detailBody.innerHTML = "";
}
