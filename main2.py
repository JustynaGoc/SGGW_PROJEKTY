import requests
from pathlib import Path


# ---------- 1. Hierarchia wyjątków ----------

class DownloadError(Exception):
    """Bazowy wyjątek dla operacji pobierania plików."""
    pass


class NotFoundError(DownloadError):
    """Rzucany, gdy serwer zwraca 404 Not Found."""
    pass


class AccessDeniedError(DownloadError):
    """Rzucany, gdy serwer zwraca 403 Forbidden."""
    pass


# ---------- 2. Funkcja pobierająca ----------

def pobierz_plik(url: str, nazwa_pliku: str = "latest.csv") -> None:
    """
    Pobiera plik z podanego URL i zapisuje go na dysku jako CSV.
    Jeśli nazwa nie zostanie podana, używa 'latest.csv'.
    Jeśli podana nazwa nie ma rozszerzenia .csv, zostanie ono dodane.
    Rzuca NotFoundError dla 404 i AccessDeniedError dla 403.
    """
    # Wymuś rozszerzenie .csv
    if not nazwa_pliku.lower().endswith(".csv"):
        nazwa_pliku = f"{nazwa_pliku}.csv"

    try:
        with requests.get(url, stream=True) as response:
            # Obsługa kodów 404 i 403 -> własne wyjątki
            if response.status_code == 404:
                raise NotFoundError(f"Nie znaleziono zasobu (404): {url}")
            if response.status_code == 403:
                raise AccessDeniedError(f"Brak dostępu do zasobu (403): {url}")

            # Inne błędy HTTP (np. 500) -> standardowy wyjątek requests
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
            print(f"[INFO] Content-Type: {content_type}")

            sciezka = Path(nazwa_pliku).resolve()
            with open(sciezka, "wb") as plik:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        plik.write(chunk)

        print(f"[OK] Zapisano: {sciezka} ({sciezka.stat().st_size} bajtów)")

    except NotFoundError as e:
        print(f"[404] {e}")
    except AccessDeniedError as e:
        print(f"[403] {e}")
    except requests.exceptions.RequestException as e:
        print(f"[BŁĄD HTTP] {type(e).__name__}: {e}")


# ---------- 3. Testy ----------

if __name__ == "__main__":
    URL_404 = "http://oleksandr-fedoruk.com/sggw/podyplomowe/404"
    URL_403 = "http://oleksandr-fedoruk.com/sggw/podyplomowe/403"
    URL = "https://oleksandr-fedoruk.com/sggw/podyplomowe/file"

    # Test domyślnej nazwy -> latest.csv
    pobierz_plik(URL)

    # Test własnej nazwy bez rozszerzenia -> moj_plik.csv (rozszerzenie dodane automatycznie)
    pobierz_plik(URL, "moj_plik")

    # Test własnej nazwy z rozszerzeniem -> dane.csv
    pobierz_plik(URL, "dane.csv")

    print( 'test 404')
    pobierz_plik(URL_404, "danaae.csv")

    print( 'test 403')
    pobierz_plik(URL_403, "dadfne.csv")
