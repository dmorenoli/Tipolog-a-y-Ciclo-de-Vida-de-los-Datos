# LaLiga Player Dataset — Web Scraper

Scraper desarrollado como parte de la **Práctica 1** de la asignatura *Tipología y Ciclo de Vida de los Datos* del Máster en Ciencia de Datos (UOC).

Extrae datos de los jugadores de los **20 clubes de LaLiga española** (temporada 2025/2026) desde [Transfermarkt.es](https://www.transfermarkt.es), generando un dataset en formato CSV.

---

## Estructura del repositorio

```
├── source/
│   ├── fetcher.py          # Descarga de páginas: robots.txt, headers, delays
│   ├── parser.py           # Extracción de datos con BeautifulSoup
│   └── scraper.py          # Orquestador principal
├── dataset/
│   └── laliga_jugadores_2025_26.csv
├── requirements.txt
└── README.md
```

---

## Dataset generado

**Título:** Plantillas LaLiga 2025/2026 — Valores de mercado, perfiles y estado de jugadores

**Fuente:** [https://www.transfermarkt.es](https://www.transfermarkt.es)

| Campo | Tipo | Descripción |
|---|---|---|
| `club` | Categórico | Nombre del equipo |
| `player_name` | Texto | Nombre completo del jugador |
| `position` | Categórico | Posición en el campo (ej: Portero, Lateral izquierdo) |
| `birth_date` | Fecha (DD/MM/YYYY) | Fecha de nacimiento |
| `age` | Numérico | Edad actual |
| `nationality` | Categórico | Nacionalidad principal |
| `height_m` | Numérico | Altura en metros (ej: 1.86) |
| `preferred_foot` | Categórico | Pie dominante (Derecho / Izquierdo / Ambidiestro) |
| `signed_date` | Fecha (DD/MM/YYYY) | Fecha de incorporación al club |
| `signed_from` | Texto | Club de procedencia |
| `contract_until` | Fecha (DD/MM/YYYY) | Fecha de fin de contrato |
| `market_value_eur` | Numérico | Valor de mercado en euros |
| `is_injured` | Binario (0/1) | 1 si el jugador está lesionado |
| `injury_info` | Texto | Descripción de la lesión y fecha estimada de vuelta |
| `is_captain` | Binario (0/1) | 1 si es el capitán del equipo |
| `player_profile_url` | Texto | URL del perfil en Transfermarkt |
| `temporada` | Texto | Temporada de los datos (2025/2026) |
| `extraction_ts_UTC` | Timestamp ISO 8601 | Fecha y hora de extracción (UTC) |

---

## Instalación

### Requisitos
- Python 3.9 o superior
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/dmorenoli/Tipolog-a-y-Ciclo-de-Vida-de-los-Datos.git
cd Tipolog-a-y-Ciclo-de-Vida-de-los-Datos

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear la carpeta de salida
mkdir dataset
```

---

## Uso

```bash
cd source
python scraper.py
```

El script imprime el progreso por equipo y guarda el CSV en `dataset/laliga_jugadores_2025_26.csv`.

**Tiempo estimado de ejecución:** 5–10 minutos (20 equipos × delay de 3–6 s por petición).

---

## Funcionamiento del scraper

El proceso de extracción navega de forma autónoma en **2 niveles**:

```
Nivel 1: Página de LaLiga
    https://www.transfermarkt.es/laliga/startseite/wettbewerb/ES1/saison_id/2025
    → Descubre los 20 equipos y sus URLs

Nivel 2: Página de plantilla de cada equipo
    https://www.transfermarkt.es/{equipo}/kader/verein/{id}/saison_id/2025/plus/1
    → Extrae todos los jugadores con sus datos completos
```

### Módulos

**`fetcher.py`** — Gestiona las peticiones HTTP de forma responsable:
- Verifica `robots.txt` antes de cada petición (cacheado para evitar requests extra)
- Aplica delays aleatorios de 3–6 segundos entre peticiones
- Usa un User-Agent identificado como scraper académico
- Maneja errores HTTP sin detener la ejecución

**`parser.py`** — Extrae los datos con BeautifulSoup:
- `get_team_links()`: obtiene los 20 equipos de la tabla de LaLiga
- `parse_squad_table()`: extrae todos los campos de cada jugador desde la tabla de plantilla (`table.items`), incluyendo posición, edad, lesiones y capitanía

**`scraper.py`** — Orquesta el flujo completo y guarda el CSV final

---

## Consideraciones éticas y legales

- Se respeta el archivo `robots.txt` de Transfermarkt antes de cada petición
- Se aplican delays aleatorios para no saturar el servidor
- El User-Agent identifica el scraper como uso académico no comercial
- Los datos extraídos son públicos y de carácter deportivo (sin datos personales sensibles)
- El dataset se usa exclusivamente con fines educativos en el marco de la UOC

---

## Dependencias

| Librería | Versión | Uso |
|---|---|---|
| `requests` | 2.33.0 | Peticiones HTTP |
| `beautifulsoup4` | 4.14.3 | Parsing HTML |
| `pandas` | 3.0.1 | Construcción y exportación del CSV |

Librerías estándar usadas (sin instalación): `re`, `urllib`, `datetime`, `time`, `random`, `os`

---

## Licencia del dataset

El dataset resultante se publica bajo licencia **CC BY-NC-SA 4.0** (Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional).

Los datos originales pertenecen a Transfermarkt GmbH & Co. KG. Este dataset se genera con fines exclusivamente académicos.

---

## Autores

Práctica realizada en el marco del Máster en Ciencia de Datos — UOC  
Asignatura: *Tipología y Ciclo de Vida de los Datos*

Estudiantes:
Daniel Francisco Moreno Linares
Victor Benito Buendía
