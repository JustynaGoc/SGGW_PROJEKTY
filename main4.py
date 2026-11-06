import csv
import time
import functools
import requests
from pathlib import Path


# ---------- Dekorator logujący czas ----------

def log_czas(func):
    """Dekorator: wypisuje czas przed i po wywołaniu funkcji oraz czas trwania."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        print(f"[START] {func.__name__} o {time.strftime('%H:%M:%S')}")
        wynik = func(*args, **kwargs)
        koniec = time.perf_counter()
        print(f"[KONIEC] {func.__name__} o {time.strftime('%H:%M:%S')} "
              f"(czas trwania: {koniec - start:.4f} s)")
        return wynik
    return wrapper


# ---------- Hierarchia wyjątków ----------

class DownloadError(Exception):
    pass


class NotFoundError(DownloadError):
    pass


class AccessDeniedError(DownloadError):
    pass


# ---------- Pobieranie pliku ----------

URL = "https://oleksandr-fedoruk.com/sggw/podyplomowe/file"
URL_404 = "http://oleksandr-fedoruk.com/sggw/podyplomowe/404"
URL_403 = "http://oleksandr-fedoruk.com/sggw/podyplomowe/403"


@log_czas
def pobierz_plik(url: str, nazwa_pliku: str = "latest.csv") -> Path:
    if not nazwa_pliku.lower().endswith(".csv"):
        nazwa_pliku = f"{nazwa_pliku}.csv"

    try:
        with requests.get(url, stream=True) as response:
            if response.status_code == 404:
                raise NotFoundError(f"Nie znaleziono zasobu (404): {url}")
            if response.status_code == 403:
                raise AccessDeniedError(f"Brak dostępu do zasobu (403): {url}")
            response.raise_for_status()

            sciezka = Path(nazwa_pliku).resolve()
            with open(sciezka, "wb") as plik:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        plik.write(chunk)

        print(f"[OK] Pobrano: {sciezka} ({sciezka.stat().st_size} bajtów)")
        return sciezka

    except NotFoundError as e:
        print(f"[404] {e}")
        raise
    except AccessDeniedError as e:
        print(f"[403] {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"[BŁĄD HTTP] {type(e).__name__}: {e}")
        raise


# ---------- Klasa ETL ----------

class ETLProcessor:
    def __init__(self, wejscie: Path, values_out: str = "values.csv",
                 missing_out: str = "missing_values.csv", delimiter: str = ","):
        self.wejscie = Path(wejscie)
        self.values_out = Path(values_out)
        self.missing_out = Path(missing_out)
        self.delimiter = delimiter

    def czytaj_linie(self):
        with open(self.wejscie, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            next(reader, None)
            for wiersz in reader:
                if wiersz and any(c.strip() for c in wiersz):
                    yield wiersz

    def przetworz_wiersz(self, wiersz: list[str]):
        try:
            numer = int(wiersz[0].strip())
        except (ValueError, IndexError):
            return None

        braki = [i for i, v in enumerate(wiersz)
                 if i > 0 and v.strip() in ("-", "")]

        wartosci = []
        for i, v in enumerate(wiersz):
            if i == 0 or v.strip() in ("-", ""):
                continue
            try:
                wartosci.append(float(v))
            except ValueError:
                braki.append(i)

        suma = sum(wartosci) if wartosci else 0.0
        srednia = (suma / len(wartosci)) if wartosci else 0.0
        return numer, suma, srednia, sorted(set(braki))

    def transformuj(self):
        for wiersz in self.czytaj_linie():
            wynik = self.przetworz_wiersz(wiersz)
            if wynik is not None:
                yield wynik

    # --- metoda przetwarzająca plik opakowana dekoratorem ---

    @log_czas
    def zapisz(self):
        with open(self.values_out, "w", newline="", encoding="utf-8") as fv, \
             open(self.missing_out, "w", newline="", encoding="utf-8") as fm:

            writer_v = csv.writer(fv)
            writer_m = csv.writer(fm)

            writer_v.writerow(["numer", "suma", "srednia"])
            writer_m.writerow(["numer", "brakujace_indeksy"])

            licznik = 0
            for numer, suma, srednia, braki in self.transformuj():
                writer_v.writerow([numer, suma, round(srednia, 2)])
                writer_m.writerow([numer, ";".join(map(str, braki))])
                licznik += 1

        print(f"[OK] Zapisano: {self.values_out.resolve()} ({licznik} wierszy)")
        print(f"[OK] Zapisano: {self.missing_out.resolve()} ({licznik} wierszy)")

    def run(self):
        self.zapisz()


# ---------- Uruchomienie ----------

URL = "https://oleksandr-fedoruk.com/sggw/podyplomowe/file"
URL_404 = "http://oleksandr-fedoruk.com/sggw/podyplomowe/404"
URL_403 = "http://oleksandr-fedoruk.com/sggw/podyplomowe/403"


if __name__ == "__main__":
    print("=== Test 1 - 403 ===")
    try:
        plik = pobierz_plik(URL_403)
        etl = ETLProcessor(plik)
        etl.run()
    except AccessDeniedError:
        print("[TEST OK] AccessDeniedError zgłoszony poprawnie")

    print("\n=== Test 2 - 404 ===")
    try:
        plik = pobierz_plik(URL_404)
        etl = ETLProcessor(plik)
        etl.run()
    except NotFoundError:uv
        print("[TEST OK] NotFoundError zgłoszony poprawnie")

    print("\n=== Test 3 - moj_plik ===")
    plik = pobierz_plik(URL, "moj_plik.csv")
    etl = ETLProcessor(plik)
    etl.run()

    print("\n=== Test 4 - latest ===")
    plik = pobierz_plik(URL)
    etl = ETLProcessor(plik)
    etl.run()


