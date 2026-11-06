import requests

def pobierz_plik(url: str, nazwa_pliku: str = "latest.txt") -> None:
    """
    Pobiera plik z podanego URL i zapisuje go pod wskazaną nazwą.
    Jeśli nazwa nie zostanie podana, używa 'latest.csv'.
    """
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(nazwa_pliku, "wb") as plik:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        plik.write(chunk)
        print(f"Plik został zapisany jako: {nazwa_pliku}")
    except requests.exceptions.RequestException as e:
        print(f"Błąd pobierania: {e}")


if __name__ == "__main__":
    URL = "https://oleksandr-fedoruk.com/sggw/podyplomowe/file"

    # Wywołanie z jednym argumentem -> użyje domyślnej nazwy "latest.csv"
    pobierz_plik(URL)
    # pobierz_plik(URL, "moj_plik.csv")