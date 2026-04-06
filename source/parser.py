import re
from bs4 import BeautifulSoup
from datetime import datetime, timezone

BASE_URL = "https://www.transfermarkt.es"

# NIVEL 1: Página de LaLiga → enlaces a los 20 equipos

def get_team_links(html):
    """
    Extrae los 20 enlaces a los equipos de LaLiga desde la página principal
    de la competición. Filtra duplicados y URLs inválidas.
    Devuelve lista de tuplas (nombre_equipo, url).
    """
    soup = BeautifulSoup(html, "html.parser")
    seen = set()
    links = []

    for a in soup.select("table.items td.hauptlink a"):
        href = a.get("href", "")
        if "/startseite/verein/" in href:
            full_url = BASE_URL + href
            if full_url not in seen:
                seen.add(full_url)
                team_name = a.get_text(strip=True)
                links.append((team_name, full_url))

    return links

# HELPERS

def _parse_market_value(raw):
    """
    Convierte strings de valor de mercado de Transfermarkt a entero en euros.
    Ejemplos: '180,00 mill. €' -> 180000000 | '850 mil €' -> 850000
    """
    if not raw:
        return None
    raw = raw.strip().replace("\xa0", " ").replace("\u202f", " ")
    match = re.search(r"([\d,.]+)\s*(mill\.|mil)?", raw)
    if not match:
        return None
    # Limpiamos el número: los puntos son separadores de miles, la coma es decimal
    num_str = match.group(1).replace(".", "").replace(",", ".")
    number = float(num_str)
    unit = match.group(2)
    if unit == "mill.":
        return int(number * 1_000_000)
    elif unit == "mil":
        return int(number * 1_000)
    else:
        return int(number)


def _parse_birth_and_age(raw):
    """
    Extrae fecha de nacimiento y edad desde strings como '11/05/1992 (33)'.
    Devuelve tupla (fecha_str, edad_int) o (None, None).
    """
    if not raw:
        return None, None
    # Buscamos patrón DD/MM/YYYY (edad)
    match = re.search(r"(\d{2}/\d{2}/\d{4})\s*\((\d+)\)", raw)
    if match:
        return match.group(1), int(match.group(2))
    return None, None


def _parse_height(raw):
    """
    Convierte strings de altura como '2,00m' o '1,86m' a float en metros.
    """
    if not raw or raw.strip() == "-":
        return None
    match = re.search(r"(\d+),(\d+)", raw)
    if match:
        return float(f"{match.group(1)}.{match.group(2)}")
    return None


# NIVEL 2: Página de plantilla → datos completos de cada jugador

def parse_squad_table(html, team_name, temporada="2025/2026"):
    """
    Extrae los datos de TODOS los jugadores de un equipo desde la tabla
    de plantilla (/kader/plus/1).

    Campos extraídos directamente del HTML de la tabla:
      - club, player_name, position
      - birth_date, age
      - nationality
      - height_m, preferred_foot
      - signed_date, signed_from
      - contract_until
      - market_value_eur
      - is_injured (0/1), injury_info
      - is_captain (0/1)
      - player_profile_url, temporada, extraction_ts_UTC

    Estrategia: leemos todo desde la tabla resumen en una sola petición por
    equipo, evitando visitar ~25 perfiles individuales reduciendo el riesgo
    de bloqueo.
    """
    if html is None:
        return []

    soup = BeautifulSoup(html, "html.parser")

    # Timestamp de extracción — zona horaria UTC, formato ISO 8601
    extraction_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    players = []

    table = soup.select_one("table.items")
    if not table:
        print(f"    [parse] No se encontró table.items para {team_name}")
        return []

    for row in table.select("tbody tr.odd, tbody tr.even"):

        name_cell = row.select_one("td.posrela td.hauptlink a")
        if not name_cell:
            continue

        player_name = name_cell.get_text(strip=True)
        player_href = name_cell.get("href", "")
        player_url  = BASE_URL + player_href if player_href else None

        injury_span = name_cell.select_one("span.verletzt-table")
        is_injured  = 1 if injury_span else 0
        injury_info = injury_span.get("title", "").strip() if injury_span else None

        captain_span = name_cell.select_one("span.kapitaenicon-table")
        is_captain   = 1 if captain_span else 0

        position = None
        inline_rows = row.select("td.posrela table.inline-table tr")
        if len(inline_rows) >= 2:
            pos_td = inline_rows[1].select_one("td")
            if pos_td:
                position = pos_td.get_text(strip=True)

        birth_date = None
        age        = None
        for td in row.find_all("td", class_="zentriert"):
            text = td.get_text(strip=True)
            bd, ag = _parse_birth_and_age(text)
            if bd:
                birth_date = bd
                age        = ag
                break

        nationality = None
        flag_imgs = row.select("img.flaggenrahmen")
        if flag_imgs:
            nationality = flag_imgs[0].get("title", "").strip()

        height_m = None
        for td in row.find_all("td", class_="zentriert"):
            text = td.get_text(strip=True)
            if re.search(r"\d,\d{2}m", text):
                height_m = _parse_height(text)
                break

        preferred_foot = None
        foot_values = {"Derecho", "Izquierdo", "Ambidiestro"}
        for td in row.find_all("td", class_="zentriert"):
            text = td.get_text(strip=True)
            if text in foot_values:
                preferred_foot = text
                break

        signed_date = None
        signed_from = None

        zentriert_tds = row.find_all("td", class_="zentriert")
        for i, td in enumerate(zentriert_tds):
            text = td.get_text(strip=True)
            
            if re.fullmatch(r"\d{2}/\d{2}/\d{4}", text) and not signed_date:
                if text != birth_date:
                    signed_date = text
                    if i + 1 < len(zentriert_tds):
                        prev_club_tag = zentriert_tds[i + 1].select_one("a[title]")
                        if prev_club_tag:
                            title_raw = prev_club_tag.get("title", "")
                            signed_from = title_raw.split(":")[0].strip() if title_raw else None
                    break

        contract_until = None
        for td in reversed(row.find_all("td", class_="zentriert")):
            text = td.get_text(strip=True)
            if re.fullmatch(r"\d{2}/\d{2}/\d{4}", text):
                contract_until = text
                break

        market_value = None
        value_cell = row.select_one("td.rechts.hauptlink a")
        if not value_cell:
            value_cell = row.select_one("td.rechts a")
        if value_cell:
            market_value = _parse_market_value(value_cell.get_text(strip=True))

        players.append({
            "club":               team_name,
            "player_name":        player_name,
            "position":           position,
            "birth_date":         birth_date,
            "age":                age,
            "nationality":        nationality,
            "height_m":           height_m,
            "preferred_foot":     preferred_foot,
            "signed_date":        signed_date,
            "signed_from":        signed_from,
            "contract_until":     contract_until,
            "market_value_eur":   market_value,
            "is_injured":         is_injured,
            "injury_info":        injury_info,
            "is_captain":         is_captain,
            "player_profile_url": player_url,
            "temporada":          temporada,
            "extraction_ts_UTC":  extraction_ts,
        })

    return players