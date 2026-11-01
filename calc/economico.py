"""Presupuesto referencial (BOM valorado), costo de operación y análisis económico simple.

Tarifas: pliego del ICE 2026 (precios sin impuestos). Precios de equipos: fuente y fecha en
el informe; los marcados (S) son estimaciones de mercado declaradas como supuestos.
Ejecutar:  python3 economico.py > economico_out.txt
"""
from carga import VEH, EVSE, USO, sesion, DIAS_L, DIAS_NL, F_NL

TC = 505.0                  # CRC/USD (S), mismo criterio que el Proyecto 2

# ------------------------------------------------------------------ presupuesto (USD)
# (código, descripción, cantidad, unidad, precio unitario USD, fuente)
BOM = [
    ('DC-1', 'Autel MaxiCharger DC Fast 60 kW UL, CCS1 + CHAdeMO (UF060A3001)', 1, 'u', 28000, 'S'),
    ('AC-1/2', 'Autel MaxiCharger AC Elite 50 A cableado, J1772 7,5 m (MC50AHS)', 2, 'u', 639, 'Autel'),
    ('AC-3/4', 'Cargador CA GB/T 7 kW 32 A, IP54, OCPP 1.6 (MDAC 132EN K)', 2, 'u', 650, 'S'),
    ('PED', 'Pedestal metálico doble para cargadores de CA, con soporte de cable', 2, 'u', 450, 'S'),
    ('RCD-B', 'Interruptor diferencial tipo B 2P 40 A 30 mA (para AC-3/AC-4)', 2, 'u', 280, 'S'),
    ('T-VE', 'Transformador seco 45 kVA 480D-208Y/120 V, NEMA 3R (Square D EE45T3H)', 1, 'u', 5200, 'S'),
    ('IP-VE', 'Interruptor 3P 200 A 480 V >= 35 kA (PowerPact JGL36200) en gabinete NEMA 3R', 1, 'u', 2600, 'S'),
    ('TD-VE', 'Tablero 480Y/277 V 225 A, principal 200 A con disparo en derivación, NEMA 3R', 1, 'u', 4800, 'S'),
    ('INT-480', 'Interruptores en TD-VE: 3P 125 A, 3P 70 A, 1P 20 A 277 V', 1, 'lote', 1620, 'S'),
    ('TD-AC', 'Tablero QO 208Y/120 V 125 A, 24 espacios, NEMA 3R, con interruptores', 1, 'u', 1000, 'S'),
    ('SPD', 'Supresores tipo 1 (480Y/277 V) y tipo 2 (208Y/120 V), UL 1449', 1, 'lote', 1300, 'S'),
    ('EPO', 'Botón de paro de emergencia tipo hongo con rótulo, cableado al disparo de TD-VE', 2, 'u', 250, 'S'),
    ('C-3/0', 'Conductor Cu THWN-2 3/0 AWG (3 fases x 126 m)', 378, 'm', 14.0, 'S'),
    ('C-4/6', 'Conductor Cu THWN-2 #4 (neutro) y #6 verde (EGC), 126 m c/u', 252, 'm', 3.8, 'S'),
    ('C-RAM', 'Conductores de circuitos derivados (#1, #4, #6, #8, #10, #12)', 1, 'lote', 950, 'S'),
    ('PVC-3', 'Tubería PVC cédula 40 de 3" (alimentador + reserva), 2 x 126 m', 252, 'm', 6.5, 'S'),
    ('PVC-R', 'Tubería PVC cédula 40 de 3/4" a 1-1/2" y accesorios', 1, 'lote', 650, 'S'),
    ('ZANJA', 'Zanja 0,6 m: corte y reposición de asfalto, excavación, relleno, cinta de aviso', 125, 'm', 45, 'S'),
    ('REG', 'Registros eléctricos de concreto 60 x 60 cm con tapa de tránsito', 5, 'u', 350, 'S'),
    ('BASES', 'Bases de concreto (DC-1, celda eléctrica, pedestales) y anclajes', 1, 'lote', 2500, 'S'),
    ('BOL', 'Bolardos de acero Ø 150 mm rellenos de concreto, h = 1,0 m', 10, 'u', 180, 'S'),
    ('TOPE', 'Topes de rueda de concreto', 6, 'u', 60, 'S'),
    ('LUM', 'Poste de 6 m con luminaria LED de 150 W, 277 V', 2, 'u', 1400, 'S'),
    ('PAT', 'Puesta a tierra: 2 varillas Cu 16 mm x 2,4 m, #4 desnudo, soldadura exotérmica', 1, 'lote', 600, 'S'),
    ('SEÑAL', 'Demarcación, rótulos INTE N120, señal vertical, Ley 7600 y rótulos NEC', 1, 'lote', 1200, 'S'),
    ('MED', 'Medición indirecta del ICE (TC + medidor) y aporte por conexión', 1, 'lote', 2500, 'S'),
    ('MO', 'Mano de obra de instalación eléctrica y obra civil menor', 1, 'lote', 9000, 'S'),
    ('PEM', 'Puesta en marcha, configuración OCPP, módem 4G y capacitación', 1, 'lote', 1500, 'S'),
    ('ING', 'Diseño, planos, visado CFIA, dirección técnica y permisos', 1, 'lote', 5000, 'S'),
]
IMPREVISTOS = 0.10

# ------------------------------------------------------------------ tarifas ICE 2026 (sin IVA)
TAR = {
    'T-CO (comercios y servicios)': dict(e=59.67, d=9861.68),
    'T-CS (preferencial, educación pública)': dict(e=50.72, d=8382.41),
}
P_AC_ICE = 99.70     # CRC/kWh, tarifa pública de carga semirrápida del ICE (junio 2026), sin IVA
P_DC_MIN = 141.0     # CRC/min, carga rápida L3 de la red nacional (ARESEP 2023), sin IVA

# ------------------------------------------------------------------ O&M (USD/año, S)
OM = [('Contrato de mantenimiento preventivo DC-1', 1500), ('Mantenimiento de cargadores CA y obra', 400),
      ('Plataforma de gestión OCPP (6 puertos)', 360), ('Conectividad 4G', 240),
      ('Póliza de responsabilidad civil (Ley 10937, art. 31)', 800)]

out = []
P = out.append
P('=' * 90)
P('PRESUPUESTO REFERENCIAL (USD, sin IVA)')
P('=' * 90)
tot = 0.0
equipos = 0.0
for cod, d, q, u, pu, f in BOM:
    st = q * pu
    tot += st
    if cod in ('DC-1', 'AC-1/2', 'AC-3/4', 'PED', 'T-VE', 'IP-VE', 'TD-VE', 'TD-AC'):
        equipos += st
    P(f'{cod:8s}{d[:70]:72s}{q:6g} {u:4s}{pu:10,.0f}{st:11,.0f}  {f}')
imp = IMPREVISTOS * tot
capex = tot + imp
P(f'{"":8s}{"Subtotal":72s}{"":21s}{tot:11,.0f}')
P(f'{"":8s}{"Imprevistos 10 %":72s}{"":21s}{imp:11,.0f}')
P(f'{"":8s}{"TOTAL":72s}{"":21s}{capex:11,.0f}  (= {capex * TC / 1e6:.1f} millones de colones)')
P(f'  Equipos principales: {equipos:,.0f} USD ({equipos / capex * 100:.0f} % del total)')

# ------------------------------------------------------------------ energía y demanda
E_dia = 0.0
min_dc = 0.0
e_ac, e_dc = 0.0, 0.0
for en, vn, s0, s1, n in USO:
    t, eb, eg, pm, pmax = sesion(VEH[vn], EVSE[en], s0, s1)
    E_dia += n * eg
    if en.startswith('DC'):
        min_dc += n * t * 60
        e_dc += n * eg
    else:
        e_ac += n * eg
fd = DIAS_L + DIAS_NL * F_NL
E_an = E_dia * fd
P_SIN_EMS = 63.2 + 2 * 8.32 + 2 * 6.66 + 1.0 + 0.3        # kW: suma de máximos (carga.py y electrico.py)
P_CON_EMS = 60.0                                        # kW: límite del sistema de gestión (NEC 625.42)
om = sum(v for _, v in OM)

P('\n' + '=' * 90)
P('COSTO DE OPERACIÓN ANUAL (escenario de uso de carga.py)')
P('=' * 90)
P(f'  Energía anual: {E_an / 1000:.1f} MWh (CA {e_ac * fd / 1000:.1f}, CC {e_dc * fd / 1000:.1f}); '
  f'minutos de CC por año: {min_dc * fd:,.0f}')
P(f'  Demanda máxima mensual sin gestión: {P_SIN_EMS:.1f} kW; con gestión de carga: {P_CON_EMS:.0f} kW')
P(f'  O&M: {om:,.0f} USD/año = {om * TC / 1e6:.2f} M CRC/año')
res = {}
for tn, t in TAR.items():
    for ems, pd in [('sin EMS', P_SIN_EMS), ('con EMS 60 kW', P_CON_EMS)]:
        c_e = E_an * t['e']
        c_d = 12 * pd * t['d']
        c_tot = c_e + c_d + om * TC
        res[(tn, ems)] = c_tot
        P(f'  {tn:40s} {ems:14s}: energía {c_e / 1e6:6.2f} M + demanda {c_d / 1e6:6.2f} M + O&M '
          f'{om * TC / 1e6:4.2f} M = {c_tot / 1e6:6.2f} M CRC/año -> {c_tot / E_an:6.1f} CRC/kWh '
          f'(demanda = {c_d / (c_e + c_d) * 100:.0f} % de la factura)')

P('\n' + '=' * 90)
P('INGRESOS DE REFERENCIA Y RETORNO SIMPLE (si se vende el servicio, Ley 10937)')
P('=' * 90)
ing = e_ac * fd * P_AC_ICE + min_dc * fd * P_DC_MIN
P(f'  Ingreso con precios de referencia del ICE (CA {P_AC_ICE} CRC/kWh; CC {P_DC_MIN} CRC/min): '
  f'{ing / 1e6:.2f} M CRC/año')
for k, c in res.items():
    flujo = ing - c
    pb = capex * TC / flujo if flujo > 0 else float('inf')
    P(f'  {k[0]:40s} {k[1]:14s}: flujo neto {flujo / 1e6:6.2f} M CRC/año -> retorno simple '
      f'{pb:5.1f} años')
# precio de equilibrio a 10 años, 8 %
r, n = 0.08, 10
crf = r * (1 + r) ** n / ((1 + r) ** n - 1)
for k, c in res.items():
    p_eq = (capex * TC * crf + c) / E_an
    P(f'  Precio medio de equilibrio (10 años, 8 %), {k[0][:5]} {k[1]:14s}: {p_eq:6.1f} CRC/kWh')

P('\n  Sensibilidad: uso al 50 % del escenario (la demanda máxima no cambia)')
for k, c in res.items():
    t = TAR[k[0]]
    pd = P_SIN_EMS if k[1] == 'sin EMS' else P_CON_EMS
    c50 = 0.5 * E_an * t['e'] + 12 * pd * t['d'] + om * TC
    f50 = 0.5 * ing - c50
    pb = capex * TC / f50 if f50 > 0 else float('inf')
    P(f'  {k[0][:5]} {k[1]:14s}: costo {c50 / (0.5 * E_an):6.1f} CRC/kWh; flujo {f50 / 1e6:6.2f} M CRC/año; '
      f'retorno {pb:5.1f} años')
print('\n'.join(out))

# ------------------------------------------------------------------ fase 1: solo carga en CA
out2 = []
Q = out2.append
Q('\n' + '=' * 90)
Q('ESCENARIO POR FASES: FASE 1 SOLO CA (infraestructura completa, sin DC-1)')
Q('=' * 90)
capex_ac = capex - 1.10 * 28000            # se difiere DC-1 (con su parte de imprevistos)
e_ac_an = e_ac * fd
p_ac = 2 * 8.32 + 2 * 6.66 + 1.0 + 0.3
ing_ac = e_ac_an * P_AC_ICE
for tn, t in TAR.items():
    c = e_ac_an * t['e'] + 12 * p_ac * t['d'] + (om - 1500 + 0) * TC
    f = ing_ac - c
    pb = capex_ac * TC / f if f > 0 else float('inf')
    Q(f'  {tn:40s}: CAPEX {capex_ac:,.0f} USD; energía {e_ac_an / 1000:.1f} MWh; demanda {p_ac:.1f} kW; '
      f'costo {c / e_ac_an:6.1f} CRC/kWh; flujo {f / 1e6:5.2f} M CRC/año; retorno {pb:5.1f} años')
print('\n'.join(out2))
