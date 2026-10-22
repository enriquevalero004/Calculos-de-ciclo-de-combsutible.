# CLAUDE.md — fcsim: simulador abierto del ciclo de combustible nuclear

## Qué es este proyecto

`fcsim` es una aplicación (Python + Streamlit) para simular escenarios de ciclo de combustible de un parque nuclear definido libremente por el usuario: qué reactores hay, con qué combustible, cómo evoluciona su potencia en el tiempo y si el ciclo es abierto o cerrado. Calcula los flujos de materiales (uranio natural, UTS, combustible fresco y gastado, Pu, U recuperado, HLW) y diagnostica si un ciclo cerrado es viable; si no lo es, propone el máximo despliegue sostenible.

Nace del TFG de Enrique Valero Domenech (UPM, 2026): *Análisis de las implicaciones de los objetivos de la COP28 en el ciclo de combustible mediante los códigos NFCSS y TR_EVOL*, y servirá como material suplementario del paper derivado.

Dos usos:
1. **Herramienta de diseño** (local): explorar sendas antes de ejecutar NFCSS.
2. **Material suplementario público** (Streamlit Cloud + GitHub + Zenodo con DOI). Debe mostrar siempre el aviso: *"Design model. Results reported in the paper were obtained with the IAEA NFCSS code."*

## Principios que no se negocian

- **Nunca inventar datos nucleares.** Secciones eficaces, periodos, rendimientos, energías por fisión, etc. llevan siempre su fuente en `data/**/README.md` (referencia completa + tabla/página). Si falta un dato, se marca como `PLACEHOLDER` en el fichero, se avisa en la UI y se pregunta a Enrique. No rellenar "de memoria".
- **Toda magnitud lleva unidades** en el nombre de la variable o en el docstring (`power_mwe`, `burnup_gwd_per_thm`, `mass_thm`).
- **Física separada de la UI.** `src/fcsim/` no importa Streamlit. Todo lo de la UI va en `app/`.
- **Cada módulo físico con tests** (pytest) que incluyan balances de masa cerrados (lo que entra = lo que sale + inventario) con tolerancia ≤ 1e-9 relativa.
- **Escenarios reproducibles:** todo escenario se serializa a YAML y una misma entrada da siempre la misma salida.
- Código, identificadores y docstrings en **inglés**. Comentarios de física pueden citar ecuaciones del TFG. UI en **inglés** por defecto (público internacional); dejar las cadenas en un diccionario para añadir español más adelante.

## Alcance

### v1 (este documento)
- Tecnologías: **LWR** (espectro térmico) y **SFR** (espectro rápido), como plantillas editables.
- Combustibles: **UOX**, **MOX** y **combustibles propios** definidos por composición isotópica.
- Un solo tipo de combustible por reactor.
- Parque libre: cada "flota" es un tipo de reactor con su senda de potencia; una flota puede ser un macro-reactor de la potencia que se quiera.
- Sendas de potencia por funciones y/o edición manual año a año.
- Pérdidas en cada etapa del ciclo.
- Ciclo abierto o cerrado (fracción reprocesada), con retardos.
- Motor de depleción a un grupo.
- Diagnóstico de viabilidad del ciclo cerrado (tres salidas, ver §7).
- Exportación de resultados (CSV) y figuras de calidad paper (PDF/PGF).
- Validación contra las Fases I–VI del TFG (NFCSS).

### v2 (no implementar todavía, pero no cerrar la puerta en la arquitectura)
- Torio (cadena Th-232 → Pa-233 → U-233), combustible con actínidos minoritarios, MSR (combustible líquido, alimentación continua), HTGR.
- Optimizador de sendas (minimizar U natural con Pu ≥ reserva).
- Regiones, capacidad de reprocesado como restricción dura (Fase VII), economía.

## Estructura del repositorio

```
fcsim/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── app/                         # Streamlit (solo UI)
│   ├── Home.py
│   └── pages/
│       ├── 1_Fuels.py
│       ├── 2_Reactors.py
│       ├── 3_Fleet_and_deployment.py
│       ├── 4_Fuel_cycle.py
│       ├── 5_Results.py
│       ├── 6_Closed_cycle_diagnostics.py
│       ├── 7_Validation.py
│       └── 8_Export.py
├── src/fcsim/
│   ├── models/                  # pydantic v2: Fuel, ReactorType, Fleet, CycleOptions, Scenario
│   ├── physics/
│   │   ├── nuclides.py          # lista de nucleidos, masas atómicas
│   │   ├── chains.py            # matriz de transmutación/desintegración
│   │   ├── xs.py                # carga de secciones eficaces a un grupo por espectro
│   │   ├── depletion.py         # Bateman a un grupo, potencia constante
│   │   ├── reactivity.py        # k∞(B), linear reactivity model
│   │   └── enrichment.py        # balance de enriquecimiento y UTS
│   ├── deployment/
│   │   ├── functions.py         # constante, lineal, exponencial, logarítmica, logística
│   │   └── path.py              # composición de tramos + ediciones manuales
│   ├── cycle/
│   │   ├── massflow.py          # cargas iniciales, recargas, descargas
│   │   ├── inventory.py         # stocks: enfriamiento, espera, Pu, RepU, U empobrecido, HLW
│   │   └── simulate.py          # bucle anual del escenario
│   ├── diagnostics/
│   │   └── closed_cycle.py      # viabilidad, máx. fracción de rápidos, año viable, capacidad
│   ├── io/                      # YAML de escenarios, exportación CSV
│   └── plotting/
│       ├── interactive.py       # plotly para la app
│       ├── paper.py             # matplotlib para el paper
│       └── paper.mplstyle
├── data/
│   ├── xs/                      # thermal_lwr.yaml, fast_sfr.yaml + README.md con fuentes
│   ├── decay/                   # periodos de semidesintegración + README.md
│   ├── templates/
│   │   ├── reactors/            # ap1000.yaml, esfr_smart.yaml (v1)
│   │   └── fuels/               # uox.yaml, mox.yaml
│   └── scenarios/               # phase_I.yaml … phase_VI.yaml
├── validation/
│   ├── nfcss/                   # salidas NFCSS en CSV (las aporta Enrique)
│   └── test_validation.py
└── tests/
```

Stack: Python ≥ 3.11, numpy, scipy, pandas, pydantic v2, pyyaml, streamlit, plotly, matplotlib, pytest. Sin dependencias pesadas de datos nucleares en v1.

## 1. Modelo de datos

### Fuel
- `name`, `kind` ∈ {`UOX`, `MOX`, `CUSTOM`} (v2: `THORIUM`, `MA`).
- `composition`: fracciones másicas sobre metal pesado (HM) por nucleido. Validar que suman 1 (tolerancia 1e-6).
- UOX: definido por `enrichment_wt` (U-235); U-234 opcional según correlación documentada o 0.
- MOX: definido por `pu_content_wt` (Pu total / HM), `pu_vector_source` ∈ {`stock`, `fixed`} y `u_matrix` ∈ {`depleted`, `natural`, `repU`}. Con `stock`, el vector isotópico del Pu es el del stock disponible ese año.
- CUSTOM: composición isotópica libre introducida por el usuario.

### ReactorType
Plantilla editable. Campos:

| Campo | Unidad | Notas |
|---|---|---|
| `spectrum` | — | `thermal` / `fast`: elige la biblioteca de secciones eficaces |
| `unit_power_mwe` | MWe | AP1000: 1117 (potencia real) |
| `thermal_efficiency` | — | |
| `load_factor` | — | |
| `discharge_burnup_gwd_per_thm` | GWd/tHM | |
| `residence_time_y` o `n_batches` | años / — | uno determina el otro |
| `core_mass_thm` | tHM | opcional; si no, se deriva de recarga × residencia |
| `initial_core_factor` | — | fracción de núcleo de equilibrio cargada al arrancar (NFCSS ≈ 0,63 para ESFR) |
| `lifetime_y` | años | solo si se activa la retirada automática |
| `fuel` | — | referencia a un `Fuel`; cada tecnología trae uno por defecto |
| `enrichment_wt` / `pu_content_wt` | — | **siempre editable** por el usuario (ver §3) |
| `tails_assay_wt` | — | |
| `cooling_time_y` | años | |
| `leakage_reactivity` | — | parámetro del LRM, calibrado por tecnología |

Plantillas v1: `ap1000.yaml` y `esfr_smart.yaml`, con los valores del TFG (Tabla 5-4 del TFG; Enrique los facilita). Excepción: potencia unitaria del AP1000 = 1117 MWe.

### Fleet
- `reactor_type`, `deployment: DeploymentPath`.
- `linked_to` opcional (flota, ratio): para tecnologías modeladas como varias entradas acopladas, p. ej. núcleo + mantas de un reproductor (v2, BN-1200 como CORE/AXIAL/RADIAL igual que en NFCSS). En v1 basta con que la estructura lo permita.
- `replaces` opcional: la potencia que se añade a esta flota se resta de otra (sustitución uno a uno, como en las Fases IV–VI).

### CycleOptions
- `type` ∈ {`open`, `closed`}; `reprocessed_fraction` ∈ [0, 1] por flota.
- Pérdidas (fracciones, todas editables): `mining_milling`, `conversion`, `enrichment_process` (aparte de la cola), `uox_fabrication`, `reprocessing_pu`, `reprocessing_u`, `mox_fabrication`.
- Retardos (años): `fabrication_lead`, `cooling` (por flota), `reprocessing`, `mox_fabrication`.
- `reprocessing_capacity_thm_per_y`: serie temporal o `unlimited` (por defecto en v1).
- `pu_reserve_t`: reserva mínima de Pu para el diagnóstico.
- `repU_recycling`: bool.
- `hlw_glass_factor`: m³ o t de vidrio por t de FP+AM (con fuente).

### Scenario
- `start_year`, `end_year` (hasta 2200), `fuels`, `reactor_types`, `fleets`, `cycle`, `initial_stocks` (Pu separado inicial con vector isotópico, combustible gastado inicial, U empobrecido).

## 2. Sendas de despliegue (`deployment/`)

Una `DeploymentPath` combina:

1. **Tramos funcionales** `[t0, t1]`, cada uno con una función y sus parámetros:
   - `constant` (se mantiene),
   - `linear`,
   - `exponential` (con parámetro k; crece o decrece),
   - `logarithmic` (con parámetro k; crece o decrece),
   - `logistic` (sigmoide; útil para despliegues realistas).

   Cada tramo se define por potencia inicial y final (o tasa) y es continuo con el anterior salvo que el usuario diga lo contrario. Las funciones crecientes y decrecientes son la misma familia con el signo de la variación.
2. **Ediciones manuales** año a año: `{año: ΔMWe}` para añadir o quitar potencia a mano, o `{año: MWe}` para fijar el valor. Se aplican después de los tramos.

En la UI: tabla editable (`st.data_editor`) + gráfico en vivo de la potencia. El número de unidades se calcula como potencia / `unit_power_mwe`, con opción de redondear a enteros.

Retirada automática por vida útil: desactivada por defecto. Las sendas son de potencia neta, como en NFCSS.

## 3. Enriquecimiento, contenido de Pu y coherencia con el quemado

- El usuario **siempre puede escribir** el enriquecimiento (UOX) o el contenido de Pu (MOX) que quiera.
- La app calcula y muestra al lado el **valor recomendado**: el que, según el LRM (§4.3), da el quemado de descarga pedido.
- Si el valor del usuario se desvía del recomendado más de un umbral configurable (por defecto ±10 % relativo), se muestra un aviso no bloqueante.
- Etiquetas informativas: LEU (< 5 %), LEU+ (5–10 %), HALEU (10–20 %); aviso si ≥ 20 %.
- Para MOX con `pu_vector_source = stock`, el recomendado se recalcula cada año con el vector del stock (Pu más degradado → más % de Pu). La serie temporal del % de Pu se muestra en Resultados.

## 4. Física

### 4.1 Frontal del ciclo (`enrichment.py`, `massflow.py`)
- Balance de enriquecimiento: F/P = (x_p − x_t)/(x_f − x_t), T = F − P.
- UTS: SWU = P·V(x_p) + T·V(x_t) − F·V(x_f), con V(x) = (2x − 1)·ln(x/(1 − x)).
- Pérdidas encadenadas hacia atrás desde el combustible cargado: fabricación → enriquecimiento → conversión → minería/molienda. Cada etapa: entrada = salida / (1 − pérdida).
- Recarga anual de equilibrio (tHM/año) = P_th[MWt] · LF · 365 / (B[GWd/tHM] · 1000).
- Carga inicial al arrancar unidades nuevas: `initial_core_factor` × masa del núcleo, fabricada `fabrication_lead` años antes.
- Al retirar potencia se descarga el núcleo completo correspondiente.

### 4.2 Depleción a un grupo (`depletion.py`)
- dN/dt = A(φ)·N, con A con absorción, captura, (n,2n) donde aplique y desintegración.
- Cadena v1: U-234/235/236/238, Np-237/239, Pu-238/239/240/241/242, Am-241/242m/243, Cm-242/243/244, más un **pseudo-producto de fisión** por fisionable para la reactividad y la masa de FP. Diseñar la cadena como datos (`chains.py` lee una tabla), para añadir la cadena del Th en v2 sin tocar el solver.
- Potencia específica constante = P_th / masa HM del núcleo. Se divide la irradiación en pasos (≥ 20 por residencia); en cada paso el flujo se renormaliza para dar esa potencia (Σ κ·σ_f·N·φ = potencia específica) y se avanza con `scipy.linalg.expm` (o CRAM si hace falta rendimiento).
- Salida: composición de descarga por tHM cargada, para cualquier composición de entrada. Cachear por (combustible, tecnología, quemado).

### 4.3 Reactividad (`reactivity.py`)
- k∞(B) = Σ ν·σ_f·N / Σ σ_a·N (incluye pseudo-FP).
- Linear reactivity model: con n lotes, B_descarga = 2n/(n+1) · B_1, donde B_1 cumple ρ(B_1) = `leakage_reactivity`.
- Valor recomendado (§3): resolver por bisección la composición inicial (enriquecimiento o % de Pu) que da el B_descarga pedido.
- `leakage_reactivity` se calibra por tecnología para que las plantillas reproduzcan los pares de referencia del TFG (AP1000: 4,5 % a 60 GWd/t; ESFR-SMART: 17,99 % de Pu a 100 GWd/t). Documentar que en el SFR el modelo a un grupo es aproximado.

### 4.4 Secciones eficaces (`data/xs/`)
- Una biblioteca a un grupo por espectro (`thermal_lwr.yaml`, `fast_sfr.yaml`) con σ_c, σ_f, ν y σ_(n,2n) por nucleido.
- **Origen:** primero valores de literatura abierta con referencia completa en `data/xs/README.md`. Enrique puede aportar una biblioteca precalculada, así que hay que soportar un formato de importación sencillo (CSV/YAML con nucleido, reacción, valor y fuente) y un selector de biblioteca en la UI.
- Calibración: factores de escala globales por espectro (p. ej. sobre σ_c del U-238 y σ_f del Pu-239) ajustados para que el combustible descargado del AP1000 y del ESFR-SMART coincida con NFCSS. Referencias del TFG: el UOX descargado lleva ≈ 1,05 % de Pu recuperable; el ESFR-SMART devuelve ≈ 95 % del Pu cargado (17,1 % frente a 17,99 %). Guardar los factores en el YAML con fecha y procedencia.

### 4.5 Final del ciclo e inventarios (`inventory.py`)
- Cohortes anuales de combustible gastado en enfriamiento, por flota y composición.
- Al terminar el enfriamiento: a reprocesado (fracción `reprocessed_fraction`, limitada por la capacidad si no es `unlimited`) o a almacén definitivo.
- Reprocesado: separa Pu (stock mezclado con vector isotópico medio ponderado; v1 = un único stock), U recuperado (a RepU; si `repU_recycling`, sustituye 1:1 U natural en la fabricación del año siguiente, como en NFCSS) y FP + AM → HLW. Aplicar pérdidas.
- Desintegración en los stocks: al menos la del Pu-241 → Am-241 durante enfriamiento y almacenamiento del Pu separado.
- El MOX se fabrica con Pu del stock `mox_fabrication` años antes de cargarse; si no hay Pu suficiente → déficit (registrar, no abortar).
- Comportamiento conocido de NFCSS que hay que poder reproducir: cuando no se fabrica UOX, la columna NatU sale negativa porque resta el U recuperado. En fcsim el U natural nunca es negativo; el U recuperado sobrante va a un stock aparte.

### 4.6 Bucle anual (`simulate.py`)
Para cada año: potencia por flota → unidades nuevas y retiradas → cargas iniciales, recargas y descargas → frontal (U nat, UTS, conversión) → enfriamiento → reprocesado → stocks → fabricación de MOX del año siguiente → registro de todas las series. Salida: `pandas.DataFrame` largo (año, flota, magnitud, valor, unidad) más un resumen.

## 5. Resultados (página 5)
- Potencia y unidades por flota; U natural anual y acumulado frente al recurso identificado (Libro Rojo 2024: 7,93 Mt U ≤ 260 USD/kgU; tramo ≤ 130 USD/kgU como segunda línea; editable); UTS; combustible fresco y gastado; stock de Pu con la reserva marcada; % de Pu del MOX en el tiempo; U recuperado; HLW; necesidad de reprocesado (tHM/año).
- Indicadores clave: U acumulado (Mt y % del recurso), año de fin de la minería, Pu mínimo (t y año), año del primer déficit, máximos de reprocesado y minería.
- Comparación de varios escenarios guardados en el mismo gráfico.

## 6. Exportación (página 8)
- Escenario a YAML (guardar y cargar).
- Series a CSV y Excel.
- Figuras con `plotting/paper.py` y `paper.mplstyle`: ancho de una o dos columnas, PDF y PGF para LaTeX, fuentes y tamaños homogéneos, paleta apta para daltónicos, sin títulos dentro de la figura (van en el caption).

## 7. Diagnóstico del ciclo cerrado (`diagnostics/closed_cycle.py`)
**Viabilidad:** el ciclo cerrado es viable si el stock de Pu ≥ `pu_reserve_t` en todos los años del horizonte, con los retardos y la capacidad de reprocesado vigentes. La salida es «viable / no viable», el año del primer déficit y el déficit máximo.

Si no es viable, se calculan tres salidas:
1. **Máxima fracción de rápidos sostenible.** Dos métodos, ambos visibles:
   - *Escalado:* multiplicar la senda de las flotas con MOX por α ∈ [0, 1] (bisección sobre α).
   - *Sustitución condicionada:* cada año solo se añade potencia de MOX si el Pu proyectado lo permite; si no, se congela (regla de la Fase V del TFG). Opción de seguir intentándolo en años posteriores en vez de congelar.

   Devuelve la fracción final y la senda resultante, aplicable con un clic como nuevo escenario.
2. **Primer año de inicio viable:** desplazar en el tiempo el inicio de las flotas con MOX y buscar el primer año sin déficit.
3. **Capacidad de reprocesado necesaria:** serie anual de tHM/año que hay que reprocesar para que no haya déficit (con capacidad ilimitada, el reprocesado «justo a tiempo»), más la capacidad constante mínima equivalente (bisección).

## 8. Validación (página 7 + `validation/`)
Enrique coloca las salidas NFCSS en `validation/nfcss/` (CSV, una por fase). Los escenarios `data/scenarios/phase_*.yaml` reproducen sus entradas. Objetivos de referencia (valores NFCSS del TFG y de la Fase VI):

| Fase | Magnitud | Valor NFCSS |
|---|---|---|
| I | U natural acumulado 2025–2100 | 3,95 Mt |
| II | U natural acumulado 2025–2100 | 10,56 Mt |
| III | año del primer déficit de Pu / stock 2100 | 2031 / −9.521 t |
| IV | año del primer déficit de Pu / stock 2100 | 2072 / −8.952 t |
| V | congelación de la sustitución / Pu mínimo / Pu 2100 | 2069 / +230 t / +2.321 t |
| VI | U natural acumulado / Pu mínimo tras 2080 / fin de minería | 7,87 Mt / 410 t (2141) / 2133 |

Tolerancias iniciales (revisar con Enrique): U natural ±5 %, años clave ±2 años, curvas de Pu con RMS reportado. Ojo: las Fases I–V del TFG usaron 1000 MWe por AP1000 y el paper usa 1117 MWe, así que los escenarios de validación deben llevar la potencia unitaria con la que se ejecutó NFCSS. La Fase VI necesita reproductores (núcleo + mantas): es objetivo de v2, aunque se deja la fila.

La página de validación superpone las curvas fcsim y NFCSS y muestra la tabla de desviaciones.

## Hitos de desarrollo

Cada hito termina con tests en verde y una demo en la app.

- **M0 — Esqueleto:** estructura, modelos pydantic, YAML de escenarios, páginas vacías navegables.
- **M1 — Sendas y frontal:** funciones de despliegue con edición manual, enriquecimiento/UTS, pérdidas, cargas y recargas. Validar U natural de las Fases I y II.
- **M2 — Depleción:** cadena, solver, k∞, LRM y valor recomendado de enriquecimiento/Pu. Calibrar contra la descarga NFCSS del AP1000 y del ESFR-SMART.
- **M3 — Ciclo cerrado:** inventarios, retardos, reprocesado, MOX con Pu del stock, RepU. Validar Fases III y IV.
- **M4 — Diagnóstico:** viabilidad y las tres salidas. Validar la congelación de la Fase V en 2069.
- **M5 — Publicación:** figuras del paper, exportación, README, aviso, despliegue en Streamlit Cloud, archivo en Zenodo.

## Cómo trabajar en este repo
- Antes de un hito, proponer un plan corto y esperar el visto bueno de Enrique.
- Cualquier decisión física no especificada aquí (una correlación, un valor por defecto, una simplificación) se consulta antes o se documenta en `docs/assumptions.md` con su justificación y fuente.
- Ejecutar `pytest` antes de cada commit. Commits pequeños y descriptivos.
- No tocar `validation/nfcss/`: son datos de referencia.
