"""Energía, potencia efectiva y tiempo de carga por vehículo y por punto de carga.

Potencia efectiva = mínimo entre: límite del vehículo (cargador a bordo en CA o curva de
aceptación en CC según el SOC), límite del EVSE (corriente configurada o potencia
compartida) y límite del suministro (tensión real del circuito). Se integra el SOC paso a
paso, sin suponer potencia máxima constante.
Ejecutar:  python3 carga.py > carga_out.txt
"""

# ------------------------------------------------------------------ vehículos
# E_u: capacidad útil (kWh). Curva CC: lista (SOC, kW) interpolada linealmente (S, forma
# típica publicada; el máximo de cada curva es el dato del fabricante).
VEH = {
    'BYD Dolphin (CR, 2024)': dict(
        E_u=44.9, ac='GB/T', P_obc=6.6, I_obc=32, dc='GB/T', P_dc=60,
        curva=[(0, 60), (0.5, 60), (0.8, 40), (0.9, 20), (1.0, 7)]),
    'Nissan Leaf 40 kWh (EE. UU., 2023)': dict(
        E_u=39.0, ac='J1772', P_obc=6.6, I_obc=32, dc='CHAdeMO', P_dc=46,
        curva=[(0, 46), (0.5, 44), (0.8, 22), (0.9, 12), (1.0, 4)]),
    'Hyundai Ioniq 5 LR (EE. UU., 2024)': dict(
        E_u=77.4, ac='J1772', P_obc=10.9, I_obc=48, dc='CCS1', P_dc=230,
        curva=[(0, 230), (0.5, 220), (0.8, 150), (0.9, 70), (1.0, 20)]),
    'Tesla Model Y LR (EE. UU., 2024)': dict(
        E_u=75.0, ac='NACS (adaptador J1772 incluido)', P_obc=11.5, I_obc=48, dc='NACS (adaptador CCS1 Tesla)',
        P_dc=250, curva=[(0, 250), (0.3, 200), (0.5, 120), (0.8, 60), (0.9, 35), (1.0, 10)]),
    'Ford F-150 Lightning ER (EE. UU., 2024)': dict(
        E_u=131.0, ac='J1772', P_obc=19.2, I_obc=80, dc='CCS1', P_dc=155,
        curva=[(0, 155), (0.5, 120), (0.8, 70), (0.9, 35), (1.0, 10)]),
}

ETA_AC = 0.90      # red -> batería en CA (cargador a bordo + cable) (S)
ETA_DC_VEH = 0.97  # salida del cargador CC -> batería (S)
ETA_DC_EVSE = 0.95 # entrada CA -> salida CC del cargador (hoja técnica: pico >= 96 %) (S)

# ------------------------------------------------------------------ puntos de carga
V_AC = 208.0
EVSE = {
    'AC-1/AC-2 (J1772, 40 A)': dict(tipo='AC', con='J1772', I=40),
    'AC-3/AC-4 (GB/T, 32 A)': dict(tipo='AC', con='GB/T', I=32),
    'DC-1 un vehículo (60 kW)': dict(tipo='DC', con=('CCS1', 'CHAdeMO', 'NACS (adaptador CCS1 Tesla)'), P=60),
    'DC-1 dos vehículos (30 kW c/u)': dict(tipo='DC', con=('CCS1', 'CHAdeMO', 'NACS (adaptador CCS1 Tesla)'), P=30),
}
CHADEMO_MAX = 125 * 0.4   # kW: 125 A x ~400 V (cable CHAdeMO del cargador) (S)


def interp(c, s):
    for (s0, p0), (s1, p1) in zip(c, c[1:]):
        if s0 <= s <= s1:
            return p0 + (p1 - p0) * (s - s0) / (s1 - s0)
    return c[-1][1]


def compatible(v, e):
    if e['tipo'] == 'AC':
        return v['ac'].startswith(e['con']) or (e['con'] == 'J1772' and 'J1772' in v['ac'])
    return v['dc'] in e['con']


def p_batt(v, e, soc):
    """Potencia en la batería (kW) y potencia tomada de la red (kW)."""
    if e['tipo'] == 'AC':
        p_evse = V_AC * e['I'] / 1000                       # límite del EVSE a 208 V
        p_obc = V_AC * min(v['I_obc'], e['I']) / 1000       # el OBC limita por corriente
        p_in = min(p_evse, p_obc, v['P_obc'])
        # reducción por balanceo de celdas por encima de 95 % (S)
        if soc > 0.95:
            p_in *= max(0.25, 1 - (soc - 0.95) / 0.05 * 0.75)
        return p_in * ETA_AC, p_in
    p_out = min(e['P'], interp(v['curva'], soc), v['P_dc'])
    if v['dc'] == 'CHAdeMO':
        p_out = min(p_out, CHADEMO_MAX)
    pb = p_out * ETA_DC_VEH
    return pb, p_out / ETA_DC_EVSE


def sesion(v, e, s0, s1, dt=1 / 600):
    """Integra de s0 a s1. Devuelve horas, kWh en batería, kWh de la red y kW medios."""
    soc, t, eb, eg = s0, 0.0, 0.0, 0.0
    pmax = 0.0
    while soc < s1 - 1e-9:
        pb, pg = p_batt(v, e, soc)
        pmax = max(pmax, pg)
        d = min(pb * dt, (s1 - soc) * v['E_u'])
        h = d / pb
        soc += d / v['E_u']
        t += h
        eb += d
        eg += pg * h
    return t, eb, eg, eb / t if t else 0, pmax


def hm(h):
    return f'{int(h)} h {round((h - int(h)) * 60):02d} min'


# sesiones por día lectivo (S): (punto, vehículo, SOC inicial, SOC final, sesiones)
USO = [
    ('AC-1/AC-2 (J1772, 40 A)', 'Hyundai Ioniq 5 LR (EE. UU., 2024)', 0.40, 0.90, 2),
    ('AC-1/AC-2 (J1772, 40 A)', 'Nissan Leaf 40 kWh (EE. UU., 2023)', 0.30, 1.00, 2),
    ('AC-3/AC-4 (GB/T, 32 A)', 'BYD Dolphin (CR, 2024)', 0.30, 1.00, 4),
    ('DC-1 un vehículo (60 kW)', 'Hyundai Ioniq 5 LR (EE. UU., 2024)', 0.20, 0.80, 2),
    ('DC-1 un vehículo (60 kW)', 'Ford F-150 Lightning ER (EE. UU., 2024)', 0.20, 0.80, 1),
    ('DC-1 un vehículo (60 kW)', 'Nissan Leaf 40 kWh (EE. UU., 2023)', 0.20, 0.80, 2),
    ('DC-1 un vehículo (60 kW)', 'Tesla Model Y LR (EE. UU., 2024)', 0.20, 0.80, 1),
]
DIAS_L, DIAS_NL, F_NL = 250, 115, 0.30


def main():
  out = []
  P = out.append
  P('=' * 100)
  P('ENERGÍA, POTENCIA EFECTIVA Y TIEMPO DE CARGA (CA a 208 V; CC con curva de aceptación)')
  P('=' * 100)
  P(f'Supuestos: eta CA red->batería = {ETA_AC}; eta CC cargador = {ETA_DC_EVSE}; eta CC vehículo = {ETA_DC_VEH}')

  for (s0, s1) in [(0.20, 0.80), (0.10, 0.80), (0.20, 1.00)]:
      P(f'\n--- Sesión de {s0 * 100:.0f} % a {s1 * 100:.0f} % de SOC ---')
      P(f'{"Vehículo":40s}{"Punto":32s}{"E bat":>8s}{"E red":>8s}{"P media":>9s}{"P máx red":>10s}{"Tiempo":>14s}')
      for vn, v in VEH.items():
          for en, e in EVSE.items():
              if not compatible(v, e):
                  continue
              t, eb, eg, pm, pmax = sesion(v, e, s0, s1)
              P(f'{vn:40s}{en:32s}{eb:8.1f}{eg:8.1f}{pm:9.1f}{pmax:10.1f}{hm(t):>14s}')

  P('\nIncompatibilidades sin adaptador aprobado por el fabricante:')
  for vn, v in VEH.items():
      nok = [en for en, e in EVSE.items() if not compatible(v, e)]
      P(f'  {vn}: {", ".join(nok)}')

  # ------------------------------------------------------------------ escenario de uso diario
  P('\n' + '=' * 100)
  P('ESCENARIO DE USO (S) Y ENERGÍA DE LA ESTACIÓN')
  P('=' * 100)
  # sesiones por día lectivo: (punto, vehículo, SOC inicial, SOC final, sesiones)
  E_dia, E_bat_dia, h_dc = 0.0, 0.0, 0.0
  for en, vn, s0, s1, n in USO:
      t, eb, eg, pm, pmax = sesion(VEH[vn], EVSE[en], s0, s1)
      E_dia += n * eg
      E_bat_dia += n * eb
      if en.startswith('DC'):
          h_dc += n * t
      P(f'  {n} x {vn:38s} en {en:28s} {s0 * 100:.0f}->{s1 * 100:.0f} %: {n * eg:6.1f} kWh red, {hm(n * t)}')
  E_anual = E_dia * (DIAS_L + DIAS_NL * F_NL)
  P(f'  Energía por día lectivo: {E_dia:.0f} kWh de la red ({E_bat_dia:.0f} kWh entregados a baterías)')
  P(f'  Ocupación de DC-1: {h_dc:.1f} h por día lectivo')
  P(f'  Energía anual: {E_dia:.0f} x ({DIAS_L} + {DIAS_NL} x {F_NL}) = {E_anual / 1000:.1f} MWh/año '
    f'(promedio {E_anual / 12:.0f} kWh/mes)')
  print('\n'.join(out))


if __name__ == '__main__':
    main()
