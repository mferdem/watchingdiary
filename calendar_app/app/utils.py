import time
from functools import wraps
import os
import requests
from imdb import IMDb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTER_DIR = os.path.join(BASE_DIR, 'static', 'img', 'posters')

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration_ms = round((time.time() - start) * 1000, 2)
        print(f"{func.__name__} executed in {duration_ms} ms")
        return result
    return wrapper

def download_poster(imdb_id):
    """
    IMDb id ile posteri indirir ve kaydeder.
    """
    if not imdb_id:
        return
    save_path = os.path.join(POSTER_DIR, f"{imdb_id}.jpg")
    if os.path.exists(save_path):
        return  # Poster zaten var, indirme
    try:
        ia = IMDb()
        movie = ia.get_movie(imdb_id.replace('tt', ''))
        cover_url = movie.get('full-size cover url')
        if cover_url:
            os.makedirs(POSTER_DIR, exist_ok=True)
            response = requests.get(cover_url, timeout=20)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                print(f"{imdb_id}: Poster indirildi")
            else:
                print(f"{imdb_id}: Poster indirilemedi (HTTP {response.status_code})")
        else:
            print(f"{imdb_id}: Poster bulunamadı")
    except Exception as e:
        print(f"{imdb_id}: Poster indirme hatası! {e}")