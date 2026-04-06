import os
import pandas as pd
from fetcher import get_page
from parser import get_team_links, parse_squad_table

LALIGA_URL  = "https://www.transfermarkt.es/laliga/startseite/wettbewerb/ES1/saison_id/2025"
TEMPORADA   = "2025/2026"
OUTPUT_DIR  = "dataset"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "laliga_jugadores_2025_26.csv")

COLUMNS = [
    "club",
    "player_name",
    "position",
    "birth_date",
    "age",
    "nationality",
    "height_m",
    "preferred_foot",
    "signed_date",
    "signed_from",
    "contract_until",
    "market_value_eur",
    "is_injured",
    "injury_info",
    "is_captain",
    "player_profile_url",
    "temporada",
    "extraction_ts_UTC",
]


def scrape_laliga():
    """
    Orquesta el scraping en 2 niveles:
      1. Página de LaLiga  → descubre los 20 equipos (nombre + URL)
      2. Página de plantilla de cada equipo → extrae todos los jugadores
         con sus datos desde la tabla resumen (sin visitar perfiles individuales)
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Nivel 1: obtener los 20 equipos
    print("[1/2] Descargando página principal de LaLiga...")
    html = get_page(LALIGA_URL)
    if html is None:
        print("ERROR FATAL: No se pudo descargar la página de LaLiga.")
        return

    team_list = get_team_links(html)
    print(f"       {len(team_list)} equipos encontrados.\n")

    all_players = []

    # Nivel 2: extraer plantilla de cada equipo
    for i, (team_name, team_url) in enumerate(team_list, 1):

        kader_url = team_url.replace("/startseite/", "/kader/") + "/plus/1"

        print(f"[2/2] Equipo {i:02d}/{len(team_list)}: {team_name}")
        print(f"      URL: {kader_url}")

        html = get_page(kader_url)
        if html is None:
            print(f"      ✗ No se pudo descargar la plantilla. Se omite.\n")
            continue

        players = parse_squad_table(html, team_name=team_name, temporada=TEMPORADA)

        if not players:
            print(f"      ✗ No se extrajeron jugadores. Revisa los selectores.\n")
            continue

        all_players.extend(players)
        print(f"       {len(players)} jugadores extraídos. "
              f"Total acumulado: {len(all_players)}\n")

    # Guardar dataset 
    if not all_players:
        print("ERROR: No se extrajo ningún jugador. El dataset está vacío.")
        return

    df = pd.DataFrame(all_players)
    df = df[[c for c in COLUMNS if c in df.columns]]
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("─" * 60)
    print(f"  Dataset guardado en: {OUTPUT_FILE}")
    print(f"  Total jugadores : {len(df)}")
    print(f"  Columnas        : {list(df.columns)}")
    print(f"\nPrimeras 3 filas:")
    print(df.head(3).to_string())
    print("─" * 60)


if __name__ == "__main__":
    scrape_laliga()