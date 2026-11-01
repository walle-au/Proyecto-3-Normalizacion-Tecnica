"""Memoria de cálculo eléctrico - Estación de carga VE, parqueo norte campus UTN (CAA-TEC).

NEC 2020 (NFPA 70), oficializado en Costa Rica por el RTCR 458:2011 (Decreto 36979-MEIC).
Todas las longitudes y datos marcados (S) son supuestos de diseño declarados en el informe.
Ejecutar:  python3 electrico.py > electrico_out.txt
"""
import math

SQ3 = math.sqrt(3)

# ------------------------------------------------------------------ datos
V_LL = 480.0                 # V, secundario del transformador ICE N.o 119688 (480Y/277 V)
V_LN = 277.0
V2_LL = 208.0                # V, secundario del transformador seco T-VE (208Y/120 V)
V2_LN = 120.0

# Hojas técnicas (corriente de entrada máxima, que exige NEC 625.41/625.42)
DC1 = dict(nombre='Autel MaxiCharger DC Fast 60 kW (UF060A3001)', P_out=60.0,
           I_in_max=91.0, I_in_nom=83.0, fp=0.98, eta=0.96)                 # 480 V 3F, 3P+PE
AC_J = dict(nombre='Autel MaxiCharger AC Elite 50A (MC50AHS), ajustado a 40 A', I=40.0)
AC_G = dict(nombre='MDAC 132EN K, conector GB/T, 32 A', I=32.0)
ILUM_W = 2 * 150.0           # W, dos postes LED (S)
AUX_VA = 1000.0              # VA, tomacorriente de mantenimiento, control y comunicaciones (S)
T_VE_KVA = 45.0              # kVA, transformador seco 480D-208Y/120 V
Z_TVE = 0.045                # p.u., impedancia típica de transformador seco de 45 kVA (S)
T_ICE_KVA = 750.0            # kVA, transformador ICE N.o 119688 (lámina E01)
Z_TICE = 0.0575              # p.u. (S): valor típico de transformadores de pedestal de 750 kVA
XR_TICE = 5.0                # relación X/R (S)

# Longitudes (S): medidas sobre la imagen satelital y la lámina E01, con 10 % de holgura
L_ALIM = 120.0               # m, nicho del transformador ICE -> TD-VE (≈100 m sobre la imagen + 20 %)
L_DC1 = 8.0                  # m, TD-VE -> DC-1
L_TVE = 3.0                  # m, TD-VE -> T-VE (primario) y T-VE -> TD-AC (secundario <= 3 m)
L_AC = {'AC-1': 18.0, 'AC-2': 18.0, 'AC-3': 13.0, 'AC-4': 13.0}   # m, TD-AC -> pedestal (VE-01)
L_ILUM = 40.0                # m, recorrido del circuito de alumbrado

# NEC 2020 Tabla 310.16, Cu THWN-2 (A) en columnas de 75 °C y 90 °C
AMP75 = {'14': 20, '12': 25, '10': 35, '8': 50, '6': 65, '4': 85, '3': 100, '2': 115, '1': 130,
         '1/0': 150, '2/0': 175, '3/0': 200, '4/0': 230, '250': 255}
AMP90 = {'14': 25, '12': 30, '10': 40, '8': 55, '6': 75, '4': 95, '3': 115, '2': 130, '1': 145,
         '1/0': 170, '2/0': 195, '3/0': 225, '4/0': 260, '250': 290}
# NEC 2020 Cap. 9 Tabla 9: R y XL de Cu en tubería de PVC, ohm/km
R_CU = {'14': 10.2, '12': 6.6, '10': 3.9, '8': 2.56, '6': 1.61, '4': 1.02, '3': 0.82, '2': 0.62,
        '1': 0.49, '1/0': 0.39, '2/0': 0.33, '3/0': 0.253, '4/0': 0.203, '250': 0.171}
XL_PVC = {'14': 0.190, '12': 0.177, '10': 0.164, '8': 0.171, '6': 0.167, '4': 0.157, '3': 0.154,
          '2': 0.148, '1': 0.151, '1/0': 0.144, '2/0': 0.141, '3/0': 0.138, '4/0': 0.135, '250': 0.135}
# NEC 2020 Cap. 9 Tabla 5: área de THHN/THWN-2 (mm2)
AREA = {'14': 6.258, '12': 8.581, '10': 13.61, '8': 23.61, '6': 32.71, '4': 53.16, '3': 62.77,
        '2': 73.16, '1': 100.8, '1/0': 119.7, '2/0': 143.4, '3/0': 172.8, '4/0': 208.8, '250': 256.1}
# NEC 2020 Cap. 9 Tabla 4, PVC cédula 40: área interna total (mm2)
PVC40 = {'1/2"': 184, '3/4"': 327, '1"': 537, '1-1/4"': 937, '1-1/2"': 1281, '2"': 2123,
         '2-1/2"': 3029, '3"': 4689, '4"': 8091}
STD = [15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 125, 150, 175, 200, 225, 250,
       300, 350, 400]        # NEC 240.6(A)
EGC = [(15, '14'), (20, '12'), (60, '10'), (100, '8'), (200, '6'), (300, '4'), (400, '3')]  # 250.122

F_T90 = 0.96                 # Tabla 310.15(B)(1): 90 °C, ambiente 31-35 °C (S, criterio de P2)
F_AG = {3: 1.00, 4: 0.80, 5: 0.80, 6: 0.80}   # Tabla 310.15(C)(1)


def std_up(i):
    return next(s for s in STD if s >= i - 1e-9)


def egc(ocpd):
    return next(c for lim, c in EGC if ocpd <= lim)


def ampac(cal, n_ccc):
    """Ampacidad corregida (columna 90 °C) y límite de terminales a 75 °C (110.14(C))."""
    return min(AMP90[cal] * F_T90 * F_AG[max(3, n_ccc)], AMP75[cal])


def vd(I, L, cal, fp=0.98, trif=True, V=V_LL):
    """Caída de tensión con impedancia eficaz (Cap. 9 Tabla 9, nota 2)."""
    s = math.sqrt(1 - fp ** 2)
    Zef = R_CU[cal] * fp + XL_PVC[cal] * s
    dv = (SQ3 if trif else 2.0) * I * (L / 1000) * Zef
    return dv, dv / V * 100


def fill(conds, tubo):
    a = sum(AREA[c] for c in conds)
    return a, a / PVC40[tubo] * 100


out = []
P = out.append

P('=' * 78)
P('MEMORIA DE CÁLCULO ELÉCTRICO - ESTACIÓN DE CARGA VE (NEC 2020, Art. 625, 215, 240, 250, 310, 450)')
P('=' * 78)

# ------------------------------------------------------------------ 1. Cargas
P('\n1. CUADRO DE CARGAS (corriente máxima de entrada de cada EVSE, NEC 625.42)')
I_dc = DC1['I_in_max']
kva_dc = SQ3 * V_LL * I_dc / 1000
P(f'  DC-1  {DC1["nombre"]}: I = {I_dc:.1f} A a 480 V 3F -> {kva_dc:.1f} kVA')
cargas_208 = [('AC-1', AC_J['I'], 'A-B'), ('AC-2', AC_J['I'], 'B-C'),
              ('AC-3', AC_G['I'], 'C-A'), ('AC-4', AC_G['I'], 'A-B')]
kva_ac = 0.0
for n, i, f in cargas_208:
    s = V2_LL * i / 1000
    kva_ac += s
    P(f'  {n}  monofásico 208 V entre fases {f}: I = {i:.0f} A -> {s:.2f} kVA')
kva_aux = AUX_VA / 1000
P(f'  Auxiliares 120 V (tomacorriente, control, comunicaciones) (S): {kva_aux:.2f} kVA')
kva_208 = kva_ac + kva_aux
P(f'  Total lado 208 V: {kva_208:.2f} kVA  (T-VE de {T_VE_KVA:.0f} kVA -> utilización {kva_208 / T_VE_KVA * 100:.0f} %)')
P(f'  Alumbrado 277 V: {ILUM_W:.0f} W')

# corrientes de línea en 208 V (fasores)
a = complex(math.cos(-2 * math.pi / 3), math.sin(-2 * math.pi / 3))
Va, Vb, Vc = V2_LN, V2_LN * a, V2_LN * a * a
Vf = {'A': Va, 'B': Vb, 'C': Vc}
Il = {'A': 0j, 'B': 0j, 'C': 0j}
for n, i, f in cargas_208:
    p, q = f.split('-')
    V = Vf[p] - Vf[q]
    I = i * V / abs(V)          # fp unitario
    Il[p] += I
    Il[q] -= I
I_aux = AUX_VA / V2_LN
Il['C'] += I_aux * Vc / abs(Vc)   # auxiliares en la fase menos cargada
P('  Corrientes de línea en 208 V (suma fasorial, fp = 1):')
for k in 'ABC':
    P(f'    Fase {k}: {abs(Il[k]):.1f} A')
I208_max = max(abs(v) for v in Il.values())
P(f'  Fase más cargada: {I208_max:.1f} A; 125 % = {1.25 * I208_max:.1f} A <= principal de TD-AC (125 A)')
I_TVE_sec = T_VE_KVA * 1000 / (SQ3 * V2_LL)
I_TVE_pri = T_VE_KVA * 1000 / (SQ3 * V_LL)
P(f'  Corriente nominal de T-VE: primario {I_TVE_pri:.1f} A, secundario {I_TVE_sec:.1f} A')

# ------------------------------------------------------------------ 2. Circuitos derivados 208 V
P('\n2. CIRCUITOS DERIVADOS DE LOS CARGADORES DE CA (NEC 625.40, 625.41, 210.19, 240.4)')
P('   Dos circuitos por tubería (4 conductores portadores de corriente -> factor 0,80).')
ramales = {}
for n, i, f in cargas_208:
    ic = 1.25 * i                              # 625.41: 125 % de la corriente máxima
    ocpd = std_up(ic)
    # menor calibre cuya ampacidad corregida cubre el 125 % y queda protegido por el OCPD (240.4(B))
    cal = next(c for c in ['10', '8', '6', '4'] if ampac(c, 4) >= ic and std_up(ampac(c, 4)) >= ocpd)
    dv, dvp = vd(i, L_AC[n], cal, fp=0.99, trif=False, V=V2_LL)
    ramales[n] = dict(i=i, ic=ic, ocpd=ocpd, cal=cal, egc=egc(ocpd), dvp=dvp)
    P(f'  {n}: I = {i:.0f} A; 125 % = {ic:.0f} A -> interruptor 2P {ocpd} A; '
      f'#{cal} Cu THWN-2 (ampacidad corregida {ampac(cal, 4):.1f} A >= {ic:.0f} A); '
      f'EGC #{egc(ocpd)}; L = {L_AC[n]:.0f} m; caída {dv:.2f} V ({dvp:.2f} %)')

# ------------------------------------------------------------------ 3. Transformador T-VE (450.3(B))
P('\n3. TRANSFORMADOR SECO T-VE 45 kVA 480D-208Y/120 V (NEC 450.3(B), 240.21(C), 250.30)')
ocpd_pri = std_up(1.25 * I_TVE_pri)   # protección solo en el primario <= 125 % (nota 1: siguiente normalizado)
P(f'  Primario: 125 % x {I_TVE_pri:.1f} A = {1.25 * I_TVE_pri:.1f} A -> interruptor 3P {ocpd_pri} A (Tabla 450.3(B), nota 1)')
cal_pri = '4'
P(f'  Conductores primarios #{cal_pri} Cu ({ampac(cal_pri, 3):.0f} A >= {ocpd_pri} A); EGC #{egc(ocpd_pri)}')
ocpd_sec = std_up(I_TVE_sec)
cal_sec = '1'
P(f'  Secundario: I = {I_TVE_sec:.1f} A -> interruptor principal de TD-AC {ocpd_sec} A a <= 3 m (240.21(C)(2))')
P(f'  Conductores secundarios #{cal_sec} Cu ({ampac(cal_sec, 3):.0f} A >= {ocpd_sec} A), neutro #{cal_sec}')
P('  Sistema derivado separadamente: puente de unión en T-VE y GEC #6 Cu al electrodo de la estación (250.30(A), 250.66)')

# ------------------------------------------------------------------ 4. Circuito DC-1
P('\n4. CIRCUITO DEL CARGADOR RÁPIDO DC-1 (480 V, 3P + PE)')
ic_dc = 1.25 * I_dc
ocpd_dc = std_up(ic_dc)
cal_dc = '1'
dv_dc, dvp_dc = vd(I_dc, L_DC1, cal_dc, fp=DC1['fp'])
P(f'  125 % x {I_dc:.0f} A = {ic_dc:.2f} A -> interruptor 3P {ocpd_dc} A, bloqueable (625.43)')
P(f'  #{cal_dc} Cu THWN-2: {ampac(cal_dc, 3):.0f} A >= {ic_dc:.1f} A; EGC #{egc(ocpd_dc)}; L = {L_DC1:.0f} m; '
  f'caída {dv_dc:.2f} V ({dvp_dc:.2f} %)')

# ------------------------------------------------------------------ 5. Alimentador AL-VE 480 V
P('\n5. ALIMENTADOR AL-VE: NICHO DEL TRANSFORMADOR ICE -> TD-VE (NEC 215.2(A)(1), 215.3)')
I_ilum = ILUM_W / V_LN
# Cargas continuas al 125 %. Se usa la capacidad completa de T-VE para dejar previsto el crecimiento.
I_cont = I_dc + I_TVE_pri + I_ilum
I_dis = 1.25 * I_cont
ocpd_al = std_up(I_dis)
cal_al = '3/0'
I_real = I_dc + kva_208 * 1000 / (SQ3 * V_LL) + I_ilum
dv_al, dvp_al = vd(I_real, L_ALIM, cal_al, fp=0.98)
P(f'  Carga continua: DC-1 {I_dc:.1f} A + T-VE {I_TVE_pri:.1f} A (capacidad nominal) + alumbrado {I_ilum:.1f} A = {I_cont:.1f} A')
P(f'  125 % = {I_dis:.1f} A -> interruptor IP-VE 3P {ocpd_al} A')
P(f'  Conductor #{cal_al} Cu THWN-2: {ampac(cal_al, 3):.0f} A >= {ocpd_al} A; neutro #4 (solo carga 277 V); EGC #{egc(ocpd_al)}')
P(f'  Corriente real con la carga instalada: {I_real:.1f} A; L = {L_ALIM:.0f} m; caída {dv_al:.2f} V ({dvp_al:.2f} %)')
for alt in ['2/0', '4/0']:
    d, dp = vd(I_real, L_ALIM, alt)
    P(f'    alternativa #{alt}: ampacidad {ampac(alt, 3):.0f} A, caída {dp:.2f} %')

P('\n   Caída de tensión total (alimentador + ramal), criterio de diseño <= 5 % total y <= 3 % por tramo')
P(f'    DC-1: {dvp_al:.2f} + {dvp_dc:.2f} = {dvp_al + dvp_dc:.2f} %')
for n in ramales:
    dsec = vd(I208_max, L_TVE, cal_sec, trif=True, V=V2_LL)[1]
    tot = dvp_al + dsec + ramales[n]['dvp']
    P(f'    {n}: {dvp_al:.2f} + {dsec:.2f} (secundario T-VE) + {ramales[n]["dvp"]:.2f} = {tot:.2f} % '
      f'(sin la regulación interna de T-VE, que se compensa con su derivación de +2,5 %)')

# ------------------------------------------------------------------ 6. Canalizaciones (Cap. 9 Tabla 1: 40 %)
P('\n6. CANALIZACIONES PVC CÉDULA 40 SUBTERRÁNEAS (Cap. 9 Tablas 1, 4 y 5; 300.5; 352)')
canal = [
    ('AL-VE (alimentador)', ['3/0'] * 3 + ['4', '6'], '3"'),
    ('DC-1', ['1'] * 3 + ['6'], '1-1/2"'),
    ('AC-1 + AC-2', ['6'] * 4 + ['10'], '1"'),
    ('AC-3 + AC-4', ['8'] * 4 + ['10'], '1"'),
    ('Alumbrado', ['12'] * 2 + ['12'], '3/4"'),
]
for n, c, t in canal:
    a_, f_ = fill(c, t)
    # tubo mínimo
    tmin = next(k for k in PVC40 if sum(AREA[x] for x in c) <= 0.40 * PVC40[k])
    P(f'  {n}: {len(c)} conductores, {a_:.0f} mm2; mínimo {tmin}; adoptado {t} -> ocupación {f_:.1f} % (<= 40 %)')
P('  Profundidad: 600 mm bajo zona de rodamiento del parqueo (Tabla 300.5, columna 3, fila de calles y parqueos)')
P('  Se deja un ducto de 3" de reserva paralelo al alimentador para ampliación.')

# ------------------------------------------------------------------ 7. Cortocircuito
P('\n7. CORRIENTE DE CORTOCIRCUITO DISPONIBLE (NEC 110.9, 110.10, 110.24)')
Zb = V_LL ** 2 / (T_ICE_KVA * 1000)
Zt = Zb * Z_TICE
Rt = Zt / math.sqrt(1 + XR_TICE ** 2)
Xt = Rt * XR_TICE
Isc_t = V_LN / Zt / 1000
Rc = R_CU[cal_al] * L_ALIM / 1000
Xc = XL_PVC[cal_al] * L_ALIM / 1000
Isc_td = V_LN / abs(complex(Rt + Rc, Xt + Xc)) / 1000
P(f'  Bornes del transformador ICE (barra infinita, Z = {Z_TICE * 100:.2f} % (S)): {Isc_t:.1f} kA')
P(f'  En TD-VE (después de {L_ALIM:.0f} m de #{cal_al}): {Isc_td:.1f} kA')
Zt2 = V2_LL ** 2 / (T_VE_KVA * 1000) * Z_TVE
Isc_tac = V2_LN / Zt2 / 1000
P(f'  En TD-AC (secundario de T-VE, Z = {Z_TVE * 100:.1f} % (S), barra infinita): {Isc_tac:.1f} kA')
P('  Capacidades: IP-VE >= 35 kA a 480 V; TD-VE >= 14 kA; TD-AC >= 10 kA; DC-1 SCCR >= 65 kA (hoja técnica)')

# ------------------------------------------------------------------ 8. Puesta a tierra
P('\n8. PUESTA A TIERRA Y EQUIPOTENCIALIZACIÓN (NEC 250.32, 250.30, 250.52, 250.53, 250.66, 250.122)')
P('  Electrodo de la estación: 2 varillas Cu 16 mm x 2,4 m separadas >= 1,8 m (250.53(A)(2) y (A)(3)), unidas con #4 desnudo')
P('  GEC desde TD-VE y desde T-VE: #6 Cu, suficiente porque termina solo en varillas (250.66(A))')
P('  EGC continuo en cada circuito (250.122); pedestales, bolardos metálicos y luminarias unidos al EGC')
P('  Neutro y tierra separados en TD-VE (equipo de alimentador, 250.32(B)(1)); unión N-T solo en el servicio y en T-VE')

# ------------------------------------------------------------------ 9. Resumen
P('\n9. RESUMEN DE PROTECCIONES')
P(f'  IP-VE  3P {ocpd_al} A, 480 V, >= 35 kA, con disparo en derivación (paro de emergencia)')
P(f'  DC-1   3P {ocpd_dc} A, 480 V (bloqueable)')
P(f'  T-VE   3P {ocpd_pri} A, 480 V (primario)   |  TD-AC principal 3P {ocpd_sec} A, 208 V')
for n, r in ramales.items():
    P(f'  {n}   2P {r["ocpd"]} A, 208 V, #{r["cal"]} Cu, EGC #{r["egc"]}')
P('  AC-3/AC-4 (equipo IEC sin listado UL): interruptor diferencial tipo B 30 mA aguas arriba (IEC 60364-7-722)')
P('  SPD tipo 1 en TD-VE (UL 1449) y tipo 2 en TD-AC')

print('\n'.join(out))
