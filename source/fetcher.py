import requests, time, random
from urllib.robotparser import RobotFileParser

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 "
        "(academic-scraper; Práctica UOC; uso no comercial)"
    ),
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
 
BASE_URL = "https://www.transfermarkt.es"
 
_robot_parser = None
 
def _get_robot_parser():
    """Inicializa y cachea el parser de robots.txt."""
    global _robot_parser
    if _robot_parser is None:
        _robot_parser = RobotFileParser()
        _robot_parser.set_url(f"{BASE_URL}/robots.txt")
        try:
            _robot_parser.read()
        except Exception as e:
            print(f"[robots.txt] No se pudo leer: {e}. Se asume acceso permitido.")
    return _robot_parser
 
 
def check_robots(url):
    """Devuelve True si la URL está permitida según robots.txt."""
    return _get_robot_parser().can_fetch("*", url)
 
 
def get_page(url, delay_range=(3, 6)):
    """
    Descarga el HTML de una URL con:
    - Verificación previa de robots.txt
    - Delay aleatorio para no saturar el servidor
    - Manejo de errores HTTP
    Devuelve bytes del contenido o None si falla.
    """
    # Saltamos URLs inválidas o anclas
    if not url or url == BASE_URL or url.endswith("#"):
        return None
 
    if not check_robots(url):
        print(f"[robots.txt] Bloqueado: {url}")
        return None
 
    # Pausa aleatoria entre requests (uso responsable)
    delay = random.uniform(*delay_range)
    time.sleep(delay)
 
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.content
    except requests.exceptions.HTTPError as e:
        print(f"[HTTP Error] {e} — {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[Request Error] {e} — {url}")
        return None