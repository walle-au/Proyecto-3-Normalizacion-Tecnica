"""Genera VE-00.tex: plano general de ubicación sobre imagen satelital (Esri World Imagery, z19).

Recorte: píxeles (960, 700)-(1520, 1300) del mosaico z19 centrado en 10,0063 N; 84,2166 O.
Resolución del mosaico: 0,294 m/px (latitud 10 grados).
"""
MPP = 0.2940                     # m por píxel
W_PX, H_PX = 560, 600
X0, Y0 = 15.0, 283.0             # esquina superior izquierda de la imagen en la lámina (mm)
WMM = 200.0
K = WMM / W_PX                   # mm por píxel


def S(px, py):
    return (X0 + px * K, Y0 - py * K)


o = []
A = o.append
A(r"""\documentclass[border=0pt]{standalone}
\newcommand{\revlamina}{1}
\input{lamina_comun.tex}
\begin{document}
\begin{tikzpicture}[x=1mm,y=1mm]
\marco""")
A(r"\node[anchor=north west,inner sep=0pt] at (%.2f,%.2f) {\includegraphics[width=%.1fmm]{ve00_base.jpg}};" % (X0, Y0, WMM))
A(r"\draw[line width=0.4pt] (%.2f,%.2f) rectangle ++(%.1f,%.2f);" % (X0, Y0, WMM, -H_PX * K))

# Ruta del alimentador AL-VE (S): nicho del transformador -> borde este de la nave -> celda eléctrica
ruta = [(425, 430), (500, 418), (500, 182), (446, 182), (446, 172)]
pts = ' -- '.join('(%.2f,%.2f)' % S(*p) for p in ruta)
A(r"\draw[ali,line width=1.6pt,dash pattern=on 3pt off 1.5pt] %s;" % pts)
L = sum(((ruta[i + 1][0] - ruta[i][0]) ** 2 + (ruta[i + 1][1] - ruta[i][1]) ** 2) ** 0.5 for i in range(len(ruta) - 1)) * MPP

# zona de la estación
x1, y1 = S(375, 148)
x2, y2 = S(435, 172)
A(r"\draw[yellow,line width=1.2pt,fill=yellow,fill opacity=0.25] (%.2f,%.2f) rectangle (%.2f,%.2f);" % (x1, y1, x2, y2))
# celda eléctrica
cx, cy = S(442, 166)
A(r"\filldraw[ali,draw=black,line width=0.3pt] (%.2f,%.2f) rectangle ++(2.2,-1.6);" % (cx - 1.1, cy + 0.8))

items = [
    # (px, py, etiqueta_x_mm, etiqueta_y_mm, texto, color)
    (405, 160, 120, 278, r'Estación de carga VE (VE-01): 4 puntos CA + 1 cargador CC de 60 kW (2 conectores)', 'yellow!70!black'),
    (442, 166, 150, 268, r'Celda eléctrica: TD-VE, T-VE 45 kVA, TD-AC, paro de emergencia', 'ali'),
    (425, 430, 150, 120, r'Transformador ICE N.\textsuperscript{o} 119688, 750 kVA, 34,5 kV/480Y/277 V, y nicho con IP-VE 200 A (posición según E01, aprox.)', 'ali'),
    (500, 300, 150, 150, r"Alimentador AL-VE: 3\#3/0 + N\#4 + EGC\#6 Cu en PVC 3'' + ducto de reserva, $\approx$%.0f m medidos (se adoptan 120 m)" % L, 'ali'),
    (88, 480, 40, 100, r'Edificio CAA-TEC (Proyecto 2)', 'exist'),
    (290, 400, 60, 130, r'Nave UTN (existente)', 'exist'),
    (250, 75, 40, 278, r'Calle interna del campus (acceso vehicular a la estación)', 'exist'),
    (260, 160, 40, 268, r'Parqueo existente de la UTN (asfalto, espacios a 90°)', 'exist'),
]
for n, (px, py, lx, ly, t, col) in enumerate(items, 1):
    x, y = S(px, py)
    A(r"\draw[%s,line width=0.5pt] (%.2f,%.2f) -- (%.2f,%.2f);" % (col, x, y, lx, ly - 1.5))
    A(r"\filldraw[%s,draw=black,line width=0.3pt] (%.2f,%.2f) circle (1.0);" % (col, x, y))
    A(r"\node[anchor=west,fill=white,draw=%s,line width=0.4pt,inner sep=1.2pt,font=\fontsize{6}{7}\selectfont,text width=%s] at (%.2f,%.2f) {\textbf{%d}~ %s};"
      % (col, '60mm' if lx > 100 else '55mm', lx, ly, n, t))

# flecha de acceso
ax, ay = S(20, 75)
A(r"\draw[-{Latex[length=3mm]},line width=1.2pt,white] (%.2f,%.2f) -- ++(10,0);" % (ax - 8, ay))
A(r"\node[font=\fontsize{5.5}{6}\selectfont\bfseries,white,anchor=south west] at (%.2f,%.2f) {acceso};" % (ax - 8, ay + 0.6))

# norte y escala
A(r"\begin{scope}[shift={(%.2f,%.2f)}]" % (X0 + WMM - 10, Y0 - H_PX * K + 12))
A(r"\filldraw[fill=white,draw=black,line width=0.4pt] (0,0) circle (6);")
A(r"\fill[black] (0,5.2) -- (-2.2,-3.8) -- (0,-2.2) -- cycle; \draw[black,line width=0.4pt,fill=white] (0,5.2) -- (2.2,-3.8) -- (0,-2.2) -- cycle;")
A(r"\node[font=\fontsize{8}{9}\selectfont\bfseries] at (0,8.2) {N};")
A(r"\end{scope}")
sb = 20 / MPP * K            # 20 m en mm
ys = Y0 - H_PX * K - 8
A(r"\foreach \i in {0,1,2,3}{\filldraw[fill=\ifodd\i white\else black\fi,draw=black,line width=0.3pt] (%.2f+\i*%.3f,%.2f) rectangle ++(%.3f,1.6);}" % (X0, sb, ys, sb))
for i in range(5):
    A(r"\node[font=\fontsize{5.5}{6}\selectfont,anchor=north] at (%.2f,%.2f) {%d};" % (X0 + i * sb, ys - 0.5, i * 20))
A(r"\node[font=\fontsize{5.5}{6}\selectfont,anchor=west] at (%.2f,%.2f) {m (escala gráfica, $\pm$5 \%%)};" % (X0 + 4 * sb + 2, ys + 0.8))

# Texto derecho
A(r"""\node[anchor=north west,font=\fontsize{9}{11}\selectfont\bfseries] at (222,283) {DATOS DEL EMPLAZAMIENTO};
\node[anchor=north west,font=\fontsize{6.2}{7.8}\selectfont,align=left,text width=180mm] at (222,276) {%
\begin{tabular}{@{}p{38mm}p{140mm}@{}}
Provincia / cantón & Alajuela / Alajuela (Central), Sede Central UTN, Villa Bonita ($\approx$960 msnm)\\
Coordenadas de la estación & 10,0065\,°N; 84,2155\,°O (imagen satelital, $\pm$10 m)\\
Propietario / usuario & Universidad Técnica Nacional (catastro A-652521-2000) / comunidad universitaria UTN--TEC y visitantes\\
Uso & Estación de carga de uso público en parqueo institucional (acceso controlado con tarjeta RFID o aplicación)\\
Distribuidora & ICE. Transformador de pedestal N.\textsuperscript{o} 119688, 750 kVA, 34,5 kV/480Y/277 V (lámina E01 del CAA)\\
Servicio nuevo & 480Y/277 V, 3F 4H, medición indirecta del ICE independiente del CAA, IP-VE 200 A\\
Puntos de carga & AC-1, AC-2: CA 208 V, J1772, 8,3 kW (40 A) $\cdot$ AC-3, AC-4: CA 208 V, GB/T, 6,7 kW (32 A)\\
 & DC-1: CC 60 kW, CCS1 + CHAdeMO (30 + 30 kW con dos vehículos)\\
Demanda máxima & 94,5 kW sin gestión; 60 kW con el sistema de gestión de carga (NEC 625.42)\\
\end{tabular}};
\node[anchor=north west,font=\fontsize{9}{11}\selectfont\bfseries] at (222,216) {ÍNDICE DE LÁMINAS};
\node[anchor=north west,font=\fontsize{6.4}{8}\selectfont,align=left] at (222,209) {%
\textbf{VE-00}\quad Plano general de ubicación (esta lámina)\\
\textbf{VE-01}\quad Planta de la estación: puntos de carga, estacionamientos, celda eléctrica, canalizaciones y accesos (1:100)\\
\textbf{VE-02}\quad Diagrama unifilar desde el transformador del ICE hasta cada cargador\\
\textbf{VE-03}\quad Detalles de montaje, zanja, puesta a tierra, rotulación y medidas de emergencia};
\node[anchor=north west,font=\fontsize{9}{11}\selectfont\bfseries] at (222,180) {NOTAS};
\node[anchor=north west,font=\fontsize{6.2}{7.6}\selectfont,align=left,text width=183mm] at (222,173) {%
1. Imagen base: Esri World Imagery (Maxar), nivel de zoom 19, descargada el 1/11/2026; resolución 0,29 m/px. Norte arriba.\\
2. La posición del transformador del ICE y del nicho de 480 V se transcribió de la lámina E01 (as-built del CAA, Proyecto 2); en la imagen queda bajo vegetación y debe confirmarse en sitio (supuesto S).\\
3. La ruta del alimentador evita la nave y los árboles: va por el costado este de la nave y por el borde del parqueo. Longitud medida $\approx$@L@ m; se adoptan 120 m para el cálculo (holgura del 20 \%, subidas y registros).\\
4. La estación ocupa seis espacios existentes en el extremo este de la fila sur del parqueo, junto a la franja verde: no reduce la circulación de la calle interna.\\
5. El servicio de la estación es independiente del servicio del CAA (Proyecto 2): no se toma carga del transformador TS-01 ni del tablero TP, que ya trabajan cerca de su capacidad.\\
6. La capacidad remanente del transformador 119688 no se conoce: se requiere el estudio de capacidad del ICE (supuesto S: $\ge$ 100 kVA disponibles). Con la gestión de carga la estación demanda como máximo 60 kW.};
""".replace("@L@", "%.0f" % L))
A(r"\node[anchor=north west,font=\fontsize{10}{12}\selectfont\bfseries] at (15,%.2f) {PLANO GENERAL DE UBICACIÓN -- CAMPUS SEDE CENTRAL UTN, VILLA BONITA DE ALAJUELA};" % (ys - 6))
A(r"\cajetin{VE-00}{Plano general de ubicación de la estación de carga,}{ruta del alimentador y transformador del ICE}{Escala gráfica ($\approx$1:730)}{1 de 4}")
A(r"\end{tikzpicture}")
A(r"\end{document}")
open('VE-00.tex', 'w').write('\n'.join(o))
print('VE-00.tex generado; ruta = %.1f m' % L)
