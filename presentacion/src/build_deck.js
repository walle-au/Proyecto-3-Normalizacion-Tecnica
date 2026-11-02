// Genera presentacion/Presentacion_Oral_P3.pptx (16:9) con pptxgenjs.
// Uso: NODE_PATH=<carpeta con node_modules> node presentacion/src/build_deck.js
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const ROOT = path.resolve(__dirname, "..");
const IMG = (f) => path.join(ROOT, "img", f);
// Con NOTAS=1 y el archivo local guion.json, se genera una copia con el guion en las
// notas del orador (solo para uso local, ignorada por git). Sin eso, la presentación sale sin notas.
const fs = require("fs");
const GUION_PATH = path.join(__dirname, "guion.json");
const CON_NOTAS = process.env.NOTAS === "1" && fs.existsSync(GUION_PATH);
const OUT = path.join(ROOT, CON_NOTAS ? "Presentacion_Oral_P3_con_notas.pptx" : "Presentacion_Oral_P3.pptx");
const GUION = CON_NOTAS ? JSON.parse(fs.readFileSync(GUION_PATH, "utf-8")) : [];
const G = (n) => { const d = GUION.find((x) => x.n === n); return d ? `${d.expositor.toUpperCase()} (${d.tiempo})\n\n` + d.texto.join("\n\n") : null; };

const THEME = {
  name: "Carga VE CAA",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2328", lt1: "FFFFFF", dk2: "0E3442", lt2: "EDF3F4",
    accent1: "13A37F", accent2: "E8962E", accent3: "2F6FC4",
    accent4: "C0392B", accent5: "5B6B73", accent6: "8FD6C1",
    hlink: "2F6FC4", folHlink: "5B6B73",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.author = "Walter Alfaro Ulate, Sebastián Meneses Castillo, Thomas Reed Víquez";
pres.title = "Proyecto 3 – Estación de carga de vehículos eléctricos";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

// ---------- iconos ----------
async function icon(Comp, color, size = 256) {
  const svg = renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}
// icono dentro de un círculo de color (motivo de la presentación)
async function iconCircle(slide, Comp, x, y, d, fill, fg = "FFFFFF") {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: "icono-fondo" });
  const p = d * 0.24;
  slide.addImage({ data: await icon(Comp, fg), x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p, altText: "icono", objectName: "icono" });
}

// ---------- layouts ----------
const FOOT = "EL-4601 · Proyecto 3 · Estación de carga VE – UTN/CAA";
pres.defineSlideMaster({
  title: "PORTADA",
  background: { color: HEX.dk2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.35, w: 6.4, h: 1.5, fontFace: THEME.headFontFace, fontSize: 36, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 3.0, w: 6.4, h: 0.8, fontSize: 18, color: C.accent6, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: HEX.lt1 },
  margin: [0.5, 0.5, 0.55, 0.5],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 7.6, h: 0.75, fontFace: THEME.headFontFace, fontSize: 26, bold: true, color: C.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: 0.5, y: 5.22, w: 7, h: 0.28, fontSize: 10, color: C.accent5, margin: 0 } } },
  ],
  slideNumber: { x: 9.0, y: 5.22, w: 0.5, h: 0.28, fontSize: 10, color: HEX.accent5, align: "right" },
});

// etiqueta del expositor (arriba a la derecha)
function speaker(slide, name, dark = false) {
  slide.addText(name, {
    x: 8.2, y: 0.42, w: 1.3, h: 0.36, fontSize: 11, bold: true, align: "center", valign: "middle",
    color: dark ? C.text2 : C.background1, fill: { color: dark ? HEX.accent6 : HEX.dk2 }, isTextBox: true,
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.18, margin: 0, objectName: "expositor",
  });
}
function title(slide, t) { slide.addText(t, { placeholder: "title" }); }
// tarjeta con fondo tenue
function card(slide, x, y, w, h, fill = HEX.lt2) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: fill }, objectName: "tarjeta" });
}
const W = "Walter", S = "Sebastián", T = "Thomas";

async function build() {
  // ===== 1. Portada =====
  pres.addSection({ title: "Introducción" });
  let s = pres.addSlide({ masterName: "PORTADA", sectionTitle: "Introducción" });
  s.addText("Estación de carga para vehículos eléctricos", { placeholder: "title" });
  s.addText("Parqueo norte del campus UTN Villa Bonita (CAA-TEC): investigación normativa y diseño en Costa Rica", { placeholder: "body" });
  await iconCircle(s, fa.FaChargingStation, 7.45, 1.45, 1.9, HEX.accent1);
  s.addText([
    { text: "Walter Alfaro Ulate · Sebastián Meneses Castillo · Thomas Reed Víquez", options: { breakLine: true } },
    { text: "Prof. Luis Roberto Pereira Arroyo · EL-4601 Normalización Técnica para Electrónica · 6 de noviembre de 2026" },
  ], { x: 0.6, y: 4.35, w: 8.8, h: 0.7, fontSize: 12, color: C.background1, margin: 0, isTextBox: true, paraSpaceAfter: 4 });
  if (CON_NOTAS) s.addNotes(G(1));

  // ===== 2. Mensaje principal =====
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Introducción" });
  title(s, "Qué diseñamos y qué concluimos");
  speaker(s, W);
  const stats = [
    ["4 + 1", "puntos de carga: 4 en CA y 1 rápido en CC de 60 kW", HEX.accent1],
    ["60 kW", "demanda máxima con gestión de energía (94,5 kW sin ella)", HEX.accent3],
    ["USD 102 500", "presupuesto referencial (≈ ₡51,8 millones)", HEX.accent2],
  ];
  stats.forEach(([n, l, col], i) => {
    const y = 1.3 + i * 1.25;
    s.addText(n, { x: 0.5, y, w: 2.9, h: 0.6, fontFace: THEME.headFontFace, fontSize: 30, bold: true, color: col === HEX.accent1 ? C.accent1 : col === HEX.accent3 ? C.accent3 : C.accent2, margin: 0, isTextBox: true });
    s.addText(l, { x: 0.5, y: y + 0.58, w: 3.6, h: 0.5, fontSize: 13, color: C.accent5, margin: 0, isTextBox: true, valign: "top" });
  });
  card(s, 4.6, 1.3, 4.9, 2.35, HEX.dk2);
  s.addText([
    { text: "Conclusión", options: { bold: true, fontSize: 14, color: C.accent6, breakLine: true } },
    { text: "Técnicamente viable con la infraestructura del campus. No se paga como negocio, pero se justifica como servicio institucional con gestión de energía.", options: { fontSize: 17, color: C.background1 } },
  ], { x: 4.85, y: 1.45, w: 4.45, h: 2.1, valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 6 });
  const agenda = ["Tecnologías", "Normativa", "Equipos", "Diseño", "Análisis"];
  agenda.forEach((a, i) => {
    s.addText(a, { x: 4.6 + i * 0.975, y: 3.95, w: 0.9, h: 0.42, fontSize: 10, bold: true, align: "center", valign: "middle", color: C.text2, fill: { color: HEX.lt2 }, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.12, margin: 0, isTextBox: true, objectName: "agenda" });
  });
  if (CON_NOTAS) s.addNotes(G(2));

  // ===== 3. Sitio =====
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Introducción" });
  title(s, "El sitio: campus UTN Villa Bonita");
  speaker(s, W);
  s.addImage({ path: IMG("sitio.jpg"), x: 0.5, y: 1.15, w: 3.65, h: 3.91, altText: "Imagen satelital del campus con la estación, el alimentador y el transformador del ICE (lámina VE-00)" });
  const sitio = [
    [fa.FaBolt, "Datos eléctricos reales", "Transformador del ICE N.º 119688: 750 kVA, 480Y/277 V (as-built E01 del P2)."],
    [fa.FaPlug, "Servicio nuevo e independiente", "Medidor propio del ICE; no carga el tablero del CAA. Alimentador de ≈ 120 m."],
    [fa.FaMapMarkedAlt, "Sin planos descargables en CR", "Plano dibujado sobre imagen satelital Esri (0,29 m/píxel) + datos del P2."],
  ];
  for (let i = 0; i < sitio.length; i++) {
    const [ic, h, d] = sitio[i]; const y = 1.2 + i * 1.3;
    await iconCircle(s, ic, 4.5, y, 0.62, HEX.accent1);
    s.addText(h, { x: 5.3, y: y - 0.04, w: 4.2, h: 0.36, fontSize: 16, bold: true, color: C.text2, margin: 0, isTextBox: true });
    s.addText(d, { x: 5.3, y: y + 0.33, w: 4.2, h: 0.75, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  }
  if (CON_NOTAS) s.addNotes(G(3));

  // ===== 4. Tecnologías =====
  pres.addSection({ title: "Tecnologías" });
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Tecnologías" });
  title(s, "Niveles y modos de carga");
  speaker(s, W);
  const niveles = [
    [fa.FaPlug, "Nivel 1 · Modo 2", "120 V, 12–16 A", "1,4–1,9 kW", "Cable portátil; 19–38 h del 20 al 80 %", HEX.accent5],
    [fa.FaChargingStation, "Nivel 2 · Modo 3", "208/240 V, 16–80 A", "3,3–19,2 kW", "Wallbox. En la estación: 8,3 y 6,7 kW", HEX.accent1],
    [fa.FaBolt, "CC · Modo 4", "480 V trifásico", "25–400 kW", "Convertidor en la estación. Aquí: 60 kW", HEX.accent2],
  ];
  for (let i = 0; i < 3; i++) {
    const [ic, h, v, p, d, col] = niveles[i]; const x = 0.5 + i * 3.05;
    card(s, x, 1.25, 2.85, 2.65);
    await iconCircle(s, ic, x + 0.2, 1.4, 0.55, col);
    s.addText(h, { x: x + 0.9, y: 1.42, w: 1.85, h: 0.5, fontSize: 15, bold: true, color: C.text2, margin: 0, valign: "middle", isTextBox: true });
    s.addText(p, { x: x + 0.2, y: 2.1, w: 2.5, h: 0.55, fontFace: THEME.headFontFace, fontSize: 26, bold: true, color: C.text2, margin: 0, isTextBox: true });
    s.addText([{ text: v, options: { breakLine: true } }, { text: d }], { x: x + 0.2, y: 2.7, w: 2.5, h: 1.1, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 4 });
  }
  card(s, 0.5, 4.12, 9.0, 0.88, HEX.dk2);
  s.addText([
    { text: "Clave: ", options: { bold: true, color: C.accent6 } },
    { text: "en CA convierte el cargador a bordo (OBC); en CC, la estación. La potencia real es el mínimo entre vehículo, EVSE y suministro.", options: { color: C.background1 } },
  ], { x: 0.75, y: 4.17, w: 8.5, h: 0.78, fontSize: 15, valign: "middle", margin: 0, isTextBox: true });
  if (CON_NOTAS) s.addNotes(G(4));

  // ===== 5. Bidireccional =====
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Tecnologías" });
  title(s, "Carga bidireccional: qué existe hoy");
  speaker(s, W);
  const bidi = [
    ["V2L", "El vehículo alimenta cargas por sus tomacorrientes", "Disponible", HEX.accent1],
    ["V2V", "7–10 kW, solo con accesorios del fabricante. Verificado: F-150 Lightning → Nissan Leaf con el Mobile Power Cord de 30 A", "Limitado", HEX.accent2],
    ["V2H / V2B", "EVSE bidireccional y un medio de transferencia que aísle la casa de la red", "Limitado", HEX.accent2],
    ["V2G", "Inversor UL 1741 SB / IEEE 1547, ISO 15118-20 y contrato con la distribuidora", "No viable hoy en CR", HEX.accent4],
  ];
  bidi.forEach(([k, d, st, col], i) => {
    const y = 1.2 + i * 0.97;
    card(s, 0.5, y, 9.0, 0.82);
    s.addText(k, { x: 0.7, y, w: 1.4, h: 0.82, fontFace: THEME.headFontFace, fontSize: 20, bold: true, color: C.text2, valign: "middle", margin: 0, isTextBox: true });
    s.addText(d, { x: 2.15, y, w: 5.2, h: 0.82, fontSize: 14, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
    s.addText(st, { x: 7.5, y: y + 0.2, w: 1.85, h: 0.42, fontSize: 12, bold: true, align: "center", valign: "middle", color: C.background1, fill: { color: col }, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.12, margin: 0, isTextBox: true, objectName: "estado" });
  });
  if (CON_NOTAS) s.addNotes(G(5));

  // ===== 6. Marco legal =====
  pres.addSection({ title: "Normativa" });
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Normativa" });
  title(s, "Marco legal costarricense");
  speaker(s, S);
  const tl = [
    ["2011/2024", "RTCR 458", "Decreto 36979-MEIC: el NEC es obligatorio. Edición vigente: NEC 2020"],
    ["2018", "Ley 9518", "Incentivos al transporte eléctrico. Reglamento 41092 (reforma 41428): INTE/IEC 61851"],
    ["2019", "Decreto 41642", "Red de recarga de las distribuidoras. No aplica a una instalación privada"],
    ["2022", "Ley 10209", "Reforma incentivos fiscales; no cambia la infraestructura"],
    ["2026", "Ley 10937", "Cualquiera puede operar y vender carga. Tarifa ARESEP y canon 0,05 %"],
  ];
  s.addShape(pres.shapes.LINE, { x: 0.8, y: 2.05, w: 8.4, h: 0, line: { color: HEX.accent5, width: 2 }, objectName: "linea-tiempo" });
  tl.forEach(([yr, name, d], i) => {
    const x = 0.5 + i * 1.82; const hi = i === 4;
    s.addShape(pres.shapes.OVAL, { x: x + 0.66, y: 1.9, w: 0.3, h: 0.3, fill: { color: hi ? HEX.accent2 : HEX.accent1 }, line: { color: HEX.lt1, width: 2 }, objectName: "hito" });
    s.addText(yr, { x, y: 1.3, w: 1.62, h: 0.45, fontSize: 15, bold: true, align: "center", color: hi ? C.accent2 : C.accent1, margin: 0, isTextBox: true });
    card(s, x, 2.4, 1.62, 2.1, hi ? "FCEFDD" : HEX.lt2);
    s.addText([{ text: name, options: { bold: true, fontSize: 15, color: C.text2, breakLine: true } }, { text: d, options: { fontSize: 12, color: C.text1 } }],
      { x: x + 0.1, y: 2.5, w: 1.42, h: 1.95, valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 5 });
  });
  s.addText("Además: INTE N121 y N120 (voluntarias), Ley 7600 (5 % de espacios accesibles), CFIA, municipalidad y Bomberos.", { x: 0.5, y: 4.62, w: 9.0, h: 0.45, fontSize: 13, italic: true, color: C.accent5, margin: 0, isTextBox: true });
  if (CON_NOTAS) s.addNotes(G(6));

  // ===== 7. NEC 625 =====
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Normativa" });
  title(s, "NEC 2020, artículo 625: cómo se aplicó");
  speaker(s, S);
  const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: HEX.dk2 } } });
  const rows = [
    [hdr("Artículo"), hdr("Exige"), hdr("Decisión en el diseño")],
    ["625.40", "Un circuito individual por EVSE", "Un circuito por cargador (VE-02)"],
    ["625.41", "Protección ≥ 125 % (carga continua)", "50 A para 40 A · 40 A para 32 A · 125 A para 91 A"],
    ["625.42", "Un EMS puede fijar una carga menor", "EMS a 60 kW; alimentador sin descontarlo"],
    ["625.43", "Desconexión bloqueable (> 60 A o > 150 V)", "Interruptor de 125 A bloqueable para DC-1"],
    ["625.22", "Protección del personal", "CCID 20 mA, IMD en CC, RCD tipo B en GB/T"],
    ["625.17", "Cable ≤ 7,5 m", "7,5 m en CA y 4,6 m en CC, con gestor de cable"],
  ];
  s.addTable(rows, { x: 0.5, y: 1.2, w: 9.0, colW: [1.1, 3.5, 4.4], fontSize: 13, color: C.text1, border: { type: "solid", pt: 0.75, color: "C9D6DA" }, fill: { color: HEX.lt1 }, rowH: 0.48, valign: "middle", margin: [0.03, 0.08, 0.03, 0.08] });
  if (CON_NOTAS) s.addNotes(G(7));

  // ===== 8. Compatibilidad =====
  pres.addSection({ title: "Equipos" });
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Equipos" });
  title(s, "Compatibilidad: el hallazgo clave");
  speaker(s, S);
  const Y = (t) => ({ text: t, options: { bold: true, color: C.accent1, align: "center" } });
  const N = { text: "—", options: { color: C.accent5, align: "center" } };
  const mrows = [
    [hdr("Vehículo"), hdr("J1772 (CA)"), hdr("GB/T (CA)"), hdr("CCS1 (CC)"), hdr("CHAdeMO (CC)")],
    [{ text: "BYD Dolphin (CR)", options: { bold: true } }, N, Y("6,6 kW"), N, N],
    ["Nissan Leaf", Y("6,6 kW"), N, N, Y("≤ 46 kW")],
    ["Hyundai Ioniq 5", Y("8,3 kW"), N, Y("60 kW"), N],
    ["Tesla Model Y*", Y("8,3 kW"), N, Y("60 kW"), N],
    ["Ford F-150 Lightning", Y("8,3 kW"), N, Y("60 kW"), N],
  ];
  s.addTable(mrows, { x: 0.5, y: 1.2, w: 5.9, colW: [1.7, 1.05, 1.05, 1.05, 1.05], fontSize: 13, color: C.text1, border: { type: "solid", pt: 0.75, color: "C9D6DA" }, fill: { color: HEX.lt1 }, rowH: 0.5, valign: "middle", margin: [0.03, 0.06, 0.03, 0.06] });
  s.addText("* con el adaptador oficial de Tesla", { x: 0.5, y: 4.3, w: 5.9, h: 0.3, fontSize: 11, italic: true, color: C.accent5, margin: 0, isTextBox: true });
  card(s, 6.7, 1.2, 2.8, 3.75, HEX.dk2);
  await iconCircle(s, fa.FaSearch, 6.95, 1.4, 0.6, HEX.accent2);
  s.addText([
    { text: "El BYD Dolphin vendido en Costa Rica usa GB/T", options: { bold: true, fontSize: 15, color: C.background1, breakLine: true } },
    { text: "En Europa usa CCS2. Ningún cargador CC con listado UL a 480 V ofrece GB/T, así que los GB/T se atienden en CA.", options: { fontSize: 13, color: C.accent6 } },
  ], { x: 6.95, y: 2.15, w: 2.35, h: 2.7, valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 8 });
  if (CON_NOTAS) s.addNotes(G(8));

  // ===== 9. Equipos =====
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Equipos" });
  title(s, "Equipos seleccionados");
  speaker(s, S);
  const eq = [
    [fa.FaPlug, "AC-1 y AC-2", "Autel MaxiCharger AC Elite 50A", ["J1772, ajustado a 40 A", "8,3 kW a 208 V", "UL 2594 y UL 2231"], HEX.accent3],
    [fa.FaPlug, "AC-3 y AC-4", "MDAC 132EN K", ["GB/T, 32 A", "6,7 kW a 208 V", "Sin UL: RCD tipo B 30 mA"], HEX.accent1],
    [fa.FaBolt, "DC-1", "Autel MaxiCharger DC Fast 60 kW", ["CCS1 + CHAdeMO", "480 V, 91 A máx.", "UL 2202; reparte 30 + 30 kW"], HEX.accent2],
  ];
  for (let i = 0; i < 3; i++) {
    const [ic, id, model, pts, col] = eq[i]; const x = 0.5 + i * 3.05;
    card(s, x, 1.2, 2.85, 3.0);
    await iconCircle(s, ic, x + 0.2, 1.35, 0.6, col);
    s.addText(id, { x: x + 0.95, y: 1.35, w: 1.8, h: 0.6, fontFace: THEME.headFontFace, fontSize: 20, bold: true, color: C.text2, valign: "middle", margin: 0, isTextBox: true });
    s.addText(model, { x: x + 0.2, y: 2.05, w: 2.5, h: 0.6, fontSize: 14, bold: true, color: C.text1, margin: 0, valign: "top", isTextBox: true });
    s.addText(pts.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < pts.length - 1 } })), { x: x + 0.2, y: 2.7, w: 2.55, h: 1.4, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 4 });
  }
  s.addText("Comparamos 7 cargadores y 5 vehículos. La selección la definieron el listado y los conectores, no solo la potencia.", { x: 0.5, y: 4.4, w: 9.0, h: 0.6, fontSize: 15, italic: true, color: C.text2, margin: 0, valign: "middle", isTextBox: true });
  if (CON_NOTAS) s.addNotes(G(9));

  // ===== 10. Planta =====
  pres.addSection({ title: "Diseño" });
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Diseño" });
  title(s, "Planta de la estación (lámina VE-01)");
  speaker(s, T);
  s.addImage({ path: IMG("planta.jpg"), x: 0.5, y: 1.15, w: 6.75, h: 3.77, altText: "Planta de la estación de carga: seis espacios, pedestales, DC-1 y celda eléctrica (lámina VE-01)" });
  const pl = [
    ["6 espacios", "2,60 m en CA y 2,80 m en CC para abrir puertas con el cable"],
    ["1 accesible", "3,30 m con franja de 1,20 m (Ley 7600)"],
    ["Celda eléctrica", "TD-VE, transformador de 45 kVA y TD-AC, con 1,1 m de espacio de trabajo"],
    ["Seguridad", "2 paros de emergencia, bolardos, topes y alumbrado LED"],
  ];
  pl.forEach(([h, d], i) => {
    s.addText([{ text: h, options: { bold: true, color: C.text2, breakLine: true } }, { text: d, options: { color: C.text1 } }],
      { x: 7.45, y: 1.15 + i * 0.95, w: 2.05, h: 0.9, fontSize: 12, valign: "top", margin: 0, isTextBox: true });
  });
  if (CON_NOTAS) s.addNotes(G(10));

  // ===== 11. Unifilar =====
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Diseño" });
  title(s, "Unifilar y resultados eléctricos (VE-02)");
  speaker(s, T);
  s.addImage({ path: IMG("unifilar.jpg"), x: 0.5, y: 1.2, w: 6.3, h: 3.04, altText: "Diagrama unifilar desde el transformador del ICE hasta cada cargador (lámina VE-02)" });
  s.addText("Servicio 480Y/277 V → IP-VE 200 A → alimentador 3#3/0 Cu (≈ 120 m) → TD-VE → DC-1 y transformador de 45 kVA → TD-AC 208Y/120 V → AC-1 a AC-4", { x: 0.5, y: 4.35, w: 6.3, h: 0.7, fontSize: 12, color: C.accent5, margin: 0, valign: "top", isTextBox: true });
  const res = [["1,54 %", "caída de tensión en el alimentador (2,79 % en el peor ramal)"], ["15,7 kA", "corriente de falla en el transformador del ICE (5,8 kA en TD-VE)"], ["182,8 A", "125 % de la carga continua; el #3/0 da 200 A"]];
  res.forEach(([n, l], i) => {
    const y = 1.2 + i * 1.28;
    card(s, 7.05, y, 2.45, 1.12);
    s.addText(n, { x: 7.2, y: y + 0.06, w: 2.2, h: 0.45, fontFace: THEME.headFontFace, fontSize: 22, bold: true, color: C.accent1, margin: 0, isTextBox: true });
    s.addText(l, { x: 7.2, y: y + 0.5, w: 2.2, h: 0.58, fontSize: 11, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  });
  if (CON_NOTAS) s.addNotes(G(11));

  // ===== 12. Tiempos =====
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Diseño" });
  title(s, "Tiempo de carga del 20 al 80 %");
  speaker(s, T);
  s.addChart(pres.charts.BAR, [
    { name: "CA (mejor punto compatible)", labels: ["BYD Dolphin", "Nissan Leaf", "Tesla Model Y", "Hyundai Ioniq 5", "Ford F-150 Lightning"], values: [4.53, 3.93, 6.02, 6.2, 10.5] },
    { name: "DC-1, un vehículo (60 kW)", labels: ["BYD Dolphin", "Nissan Leaf", "Tesla Model Y", "Hyundai Ioniq 5", "Ford F-150 Lightning"], values: [0, 0.65, 0.77, 0.8, 1.35] },
  ], {
    x: 0.5, y: 1.15, w: 5.9, h: 3.9, barDir: "bar", barGrouping: "clustered", barGapWidthPct: 60,
    chartColors: [HEX.accent3, HEX.accent2], showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0\" h\";;", dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt", dataLabelColor: HEX.dk1,
    catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt", catAxisOrientation: "maxMin",
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showTitle: true, title: "Horas (curva de aceptación de cada vehículo)", titleFontSize: 12, titleFontFace: "+mn-lt", titleColor: HEX.accent5,
  });
  const tk = [
    [fa.FaTachometerAlt, "En CC la potencia cae con el SOC", "Del 20 al 100 % tarda más del doble que del 20 al 80 %."],
    [fa.FaBolt, "208 V no es 240 V", "Un EVSE de 40 A entrega 8,3 kW, no 9,6 kW."],
    [fa.FaCarSide, "El Dolphin no carga en DC-1", "Usa GB/T: CA en la estación o la red del ICE en CC."],
  ];
  for (let i = 0; i < tk.length; i++) {
    const [ic, h, d] = tk[i]; const y = 1.2 + i * 1.28;
    await iconCircle(s, ic, 6.65, y, 0.5, HEX.accent1);
    s.addText([{ text: h, options: { bold: true, color: C.text2, breakLine: true } }, { text: d, options: { color: C.text1 } }], { x: 7.3, y: y - 0.05, w: 2.2, h: 1.15, fontSize: 13, valign: "top", margin: 0, isTextBox: true });
  }
  if (CON_NOTAS) s.addNotes(G(12));

  // ===== 13. Economía =====
  pres.addSection({ title: "Análisis" });
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Análisis" });
  title(s, "Costo de operación anual");
  speaker(s, T);
  const cats = ["T-CO sin EMS", "T-CO con EMS", "T-CS sin EMS", "T-CS con EMS"];
  s.addChart(pres.charts.BAR, [
    { name: "Energía", labels: cats, values: [9.71, 9.71, 8.25, 8.25] },
    { name: "Demanda", labels: cats, values: [11.18, 7.10, 9.50, 6.04] },
    { name: "O&M", labels: cats, values: [1.67, 1.67, 1.67, 1.67] },
  ], {
    x: 0.5, y: 1.15, w: 5.9, h: 3.9, barDir: "col", barGrouping: "stacked", barGapWidthPct: 55,
    chartColors: [HEX.accent3, HEX.accent2, HEX.accent5], showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
    showValue: true, dataLabelPosition: "ctr", dataLabelFormatCode: "0.0", dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt", dataLabelColor: "FFFFFF",
    catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt",
    valAxisLabelColor: HEX.accent5, valAxisLabelFontSize: 10, valAxisLabelFontFace: "+mn-lt", valGridLine: { color: "DDE5E8", size: 0.5 }, catGridLine: { style: "none" },
    showTitle: true, title: "Millones de colones por año (162,8 MWh/año)", titleFontSize: 12, titleFontFace: "+mn-lt", titleColor: HEX.accent5,
  });
  const ec = [["₡98/kWh", "costo con T-CS y EMS (₡139 sin EMS en T-CO)", C.accent1], ["≈ 12 años", "retorno en el mejor caso, vendiendo a precios del ICE", C.accent2], ["₡145/kWh", "precio medio de equilibrio a 10 años (8 %)", C.accent3]];
  ec.forEach(([n, l, col], i) => {
    const y = 1.2 + i * 1.28;
    s.addText(n, { x: 6.7, y, w: 2.8, h: 0.5, fontFace: THEME.headFontFace, fontSize: 24, bold: true, color: col, margin: 0, isTextBox: true });
    s.addText(l, { x: 6.7, y: y + 0.5, w: 2.8, h: 0.6, fontSize: 12, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  });
  if (CON_NOTAS) s.addNotes(G(13));

  // ===== 14. Viabilidad =====
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Análisis" });
  title(s, "Viabilidad del proyecto");
  speaker(s, T);
  const via = [
    [fa.FaCheckCircle, "Técnica", "Viable", "Cabe en el transformador del campus, sujeto al estudio de capacidad del ICE.", HEX.accent1, C.accent1],
    [fa.FaTimesCircle, "Como negocio", "No se paga", "Retorno de 12 años en el mejor caso; con la mitad del uso no se recupera.", HEX.accent4, C.accent4],
    [fa.FaExclamationTriangle, "Regulatoria", "En transición", "La Ley 10937 permite vender carga; faltan el reglamento del MINAE y la tarifa de ARESEP.", HEX.accent2, C.accent2],
  ];
  for (let i = 0; i < 3; i++) {
    const [ic, h, v, d, hex, sc] = via[i]; const x = 0.5 + i * 3.05;
    card(s, x, 1.2, 2.85, 2.75);
    await iconCircle(s, ic, x + 0.2, 1.35, 0.6, hex);
    s.addText(h, { x: x + 0.95, y: 1.35, w: 1.8, h: 0.6, fontSize: 16, bold: true, color: C.text2, valign: "middle", margin: 0, isTextBox: true });
    s.addText(v, { x: x + 0.2, y: 2.1, w: 2.5, h: 0.5, fontFace: THEME.headFontFace, fontSize: 22, bold: true, color: sc, margin: 0, isTextBox: true });
    s.addText(d, { x: x + 0.2, y: 2.65, w: 2.5, h: 1.2, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  }
  card(s, 0.5, 4.15, 9.0, 0.85, HEX.dk2);
  s.addText([{ text: "Recomendación: ", options: { bold: true, color: C.accent6 } }, { text: "ejecutarla como servicio institucional de la UTN, con EMS, y considerar una fase 1 solo en CA (USD 71 700).", options: { color: C.background1 } }],
    { x: 0.75, y: 4.2, w: 8.5, h: 0.75, fontSize: 15, valign: "middle", margin: 0, isTextBox: true });
  if (CON_NOTAS) s.addNotes(G(14));

  // ===== 15. Supuestos e IA =====
  s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Análisis" });
  title(s, "Supuestos declarados y uso de IA");
  speaker(s, W);
  card(s, 0.5, 1.2, 4.35, 3.8);
  await iconCircle(s, fa.FaClipboardList, 0.7, 1.35, 0.55, HEX.accent2);
  s.addText("Supuestos (S) por confirmar", { x: 1.4, y: 1.35, w: 3.35, h: 0.55, fontSize: 16, bold: true, color: C.text2, valign: "middle", margin: 0, isTextBox: true });
  const sup = ["Capacidad remanente del transformador del ICE", "Posición del nicho y ruta de 120 m", "Precio de DC-1 (Autel no lo publica)", "Texto de INTE N121 y N120 (de pago)", "Dimensiones finales según Ley 7600"];
  s.addText(sup.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < sup.length - 1 } })), { x: 0.75, y: 2.05, w: 3.95, h: 2.8, fontSize: 14, color: C.text1, valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 6 });
  card(s, 5.15, 1.2, 4.35, 3.8);
  await iconCircle(s, fa.FaRobot, 5.35, 1.35, 0.55, HEX.accent3);
  s.addText("Inteligencia artificial", { x: 6.05, y: 1.35, w: 3.35, h: 0.55, fontSize: 16, bold: true, color: C.text2, valign: "middle", margin: 0, isTextBox: true });
  const ia = ["Claude (Anthropic) para buscar fuentes, programar los cálculos y redactar", "Todo se verificó contra fuentes primarias: La Gaceta, ICE, ARESEP, fichas y NEC", "Lo no verificable se marcó (S) o se eliminó", "Prompts íntegros en el anexo del informe"];
  s.addText(ia.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < ia.length - 1 } })), { x: 5.4, y: 2.05, w: 3.95, h: 2.8, fontSize: 14, color: C.text1, valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 6 });
  if (CON_NOTAS) s.addNotes(G(15));

  // ===== 16. Cierre =====
  s = pres.addSlide({ masterName: "PORTADA", sectionTitle: "Análisis" });
  s.addText("¿Preguntas?", { placeholder: "title" });
  s.addText("Informe, láminas, cálculos y datasheets: github.com/walle-au/Proyecto-3-Normalizacion-Tecnica", { placeholder: "body" });
  await iconCircle(s, fa.FaComments, 7.45, 1.45, 1.9, HEX.accent1);
  if (CON_NOTAS) s.addNotes(G(16));

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("OK", OUT);
}
build().catch((e) => { console.error(e); process.exit(1); });
