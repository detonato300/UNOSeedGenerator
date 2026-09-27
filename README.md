# UNO Seed Generator

Fork projektu [Rav3nPL/SeedGenerator](https://github.com/Rav3nPL/SeedGenerator): generator mnemonica zgodnego z BIP39, w którym entropia pochodzi z **fizycznie potasowanej talii kart** oraz z czasu, w jakim klikasz kolejne karty. Ten fork przenosi wersję HTML na **talię UNO** i dodaje w pełni offline'owy kreator.

Również nie ufasz generatorom losowości z komputera? O to właśnie chodzi: komputer niczego tu nie losuje.

> **English summary:** fork of Rav3nPL/SeedGenerator. Generates a BIP39 mnemonic from a physically shuffled UNO deck plus click-timing jitter. `uno-seed-studio.html` is a single-file, fully offline wizard (PL/EN). See the disclaimer below: unaudited, no warranty, use only on an offline machine.

## ⚠️ Zastrzeżenia (disclaimer)

- **Brak jakiejkolwiek gwarancji.** Oprogramowanie jest dostarczane „tak jak jest”. Używasz go na własne ryzyko. Autorzy nie odpowiadają za utratę środków.
- **Kod nie przeszedł audytu bezpieczeństwa.** To projekt hobbystyczny/eksperymentalny, nie produkt kryptograficzny.
- Generuj seed **na komputerze odłączonym od sieci** (najlepiej z systemu live, np. Tails), a po wygenerowaniu zamknij przeglądarkę.
- Seed zapisuj **wyłącznie na papierze lub metalu**. Nigdy nie rób zdjęć, zrzutów ekranu, nie wklejaj go do chmury, menedżera haseł online ani komunikatora.
- Zanim wpłacisz większą kwotę: zaimportuj seed do **zaufanego portfela** (najlepiej sprzętowego), zapisz pierwszy adres, usuń portfel i odtwórz go z kartki. Adres musi być identyczny.
- Mnemonic z tej aplikacji jest zgodny z BIP39, ale **nie da się go odtworzyć z samych kart**: czas kliknięć jest częścią entropii. Kartka z 12–24 słowami jest jedyną kopią.
- To jest nieoficjalny fork; oryginalny autor nie jest odpowiedzialny za zmiany wprowadzone tutaj.

## Zawartość repozytorium

| Plik | Co to jest |
|---|---|
| `uno-seed-studio.html` | **Zalecany.** Samodzielny kreator w jednym pliku: edytor talii, instrukcja tasowania, wybieranie kart (z cofaniem i skrótami klawiszowymi), wynik oraz sprawdzenie zapisu. PL/EN, jasny/ciemny motyw, FAQ o BIP39 dla początkujących. |
| `index.html` | Prostszy port HTML+JS oryginalnego programu, dostosowany do talii UNO. |
| `INIT.py` | Konfigurator talii w konsoli (Python 3, bez zależności): pyta, ile masz kart każdego rodzaju, i zapisuje `deck.json`. |
| `deck.json` | Przykładowa konfiguracja: standardowa talia UNO, 108 kart. |
| `SeedGenerator/`, `SeedGenerator.sln` | Oryginalna aplikacja WinForms (.NET) autorstwa Rav3nPL, **bez zmian**, nadal na **52 karty do gry**. |

## Bezpieczeństwo wersji HTML

- **Działa w 100% offline.** `uno-seed-studio.html` ma politykę CSP (`default-src 'none'`), która blokuje przeglądarce każde połączenie sieciowe. Nie ma zewnętrznych czcionek, skryptów ani CDN, a lista słów BIP39 jest wbudowana w plik.
- **Sekrety nie są zapisywane.** Entropia, sól i słowa istnieją tylko w pamięci karty. `localStorage` przechowuje wyłącznie język, motyw, stan samouczka i konfigurację talii. „Nowy seed” oraz zamknięcie karty kasują wszystko.
- Przeglądarkowe `crypto.getRandomValues()` **nie wpływa na seed.** Służy tylko do tasowania kolejności pól w kroku sprawdzania.

## Jak używać (uno-seed-studio.html)

1. Pobierz repozytorium (lub sam plik) i przenieś je na komputer offline.
2. Otwórz `uno-seed-studio.html` w przeglądarce (dwuklik, `file://` działa). Jeśli przeglądarka blokuje `crypto.subtle` dla plików lokalnych, uruchom `python -m http.server` w folderze i wejdź na `http://localhost:8000/uno-seed-studio.html`.
3. **Krok 1, talia:** ustaw, ile kart każdego rodzaju fizycznie masz. Możesz wpisać notację (patrz niżej), wczytać lub wkleić `deck.json`.
4. **Krok 2, długość:** 12, 15, 18, 21 albo 24 słowa. Opcjonalnie wpisz własną sól (tylko drukowalne znaki ASCII).
5. **Krok 3, tasowanie:** potasuj talię metodą [riffle shuffle](https://en.wikipedia.org/wiki/Shuffling#Riffle) co najmniej 7 razy.
6. **Krok 4, karty:** dobieraj karty z wierzchu i klikaj je po kolei (kolor, potem wartość; dzikie karty bez koloru). Dla 24 słów aplikacja poprosi o ponowne potasowanie i drugą rundę.
7. **Krok 5, wynik:** odsłoń słowa, zapisz je na papierze, odhacz listę kontrolną.
8. **Krok 6, sprawdzenie:** słowa są ukryte, a pola pojawiają się w **losowej kolejności**. Wpisz każde słowo z kartki (z autouzupełnianiem z listy BIP39). Błędy są liczone i zaznaczane, więc od razu wiesz, czy zapis jest poprawny.

## Konfiguracja talii (INIT.py)

```
python INIT.py                     # tryb interaktywny, pyta o każdy rodzaj karty
python INIT.py "0 fcc1, 1-9 fcc2, +2,stop,reverse fcc2, wildcolor x4, wild+4 x4"
```

Notacja (ta sama działa w polu tekstowym kreatora):

- `fccN` to N sztuk w każdym kolorze (`fcd` jest akceptowane jako literówka),
- `R2 Y1 G2 B0` to liczby osobno dla kolorów,
- `xN` to liczba dzikich kart bez koloru (`wildcolor`, `wild+4`),
- rodzaje: `0`–`9`, zakresy typu `1-9`, `+2`, `stop`, `reverse`.

Przykład powyżej to standardowa talia UNO (108 kart), identyczna z dołączonym `deck.json`.

## Algorytm

Ten sam co w oryginale:

1. Każde kliknięcie dopisuje kod karty (np. `5R`, `+2Y`, `STOPG`, `REVB`, `WILD`, `WILD4`) do tekstu entropii.
2. Sól jest aktualizowana łańcuchowo: `sól = base64(SHA-512(sól + znacznik_czasu_kliknięcia))`.
3. Seed to `SHA-512(entropia + sól)` obcięte do 128/160/192/224/256 bitów, plus suma kontrolna z SHA-256. Całość jest dzielona na 11-bitowe fragmenty, a każdy fragment wskazuje słowo z angielskiej listy BIP39.

Liczba wymaganych kart jest skalowana do rozmiaru talii (proporcje z oryginalnej tabeli 35/41/47/52/52 z 52 kart). Dla 24 słów jest druga runda. Aktualizacje soli są kolejkowane, więc bardzo szybkie klikanie nie gubi żadnego ogniwa łańcucha.

## Aplikacja WinForms (oryginał)

Binarka oryginału: zakładka ["Releases"](https://github.com/Rav3nPL/SeedGenerator/releases) repozytorium Rav3nPL. Wymaga .NET, czyli Windows albo Linux/macOS z mono/wine. Ta wersja nadal używa dwóch przejść przez talię 52 kart.

## Autorzy

- Oryginalny SeedGenerator: [Rav3nPL](https://github.com/Rav3nPL/SeedGenerator). Tipbox autora oryginału: `1Rav3nkMayCijuhzcYemMiPYsvcaiwHni`
- Port UNO, kreator offline, INIT.py: ten fork.

## Wsparcie (donate)

Jeśli ten fork Ci się przydał, możesz wesprzeć jego rozwój:

| Waluta | Adres |
|---|---|
| **Bitcoin (BTC)** | `bc1qvclgxw9tc5gxre2gacegjcakh0rx9l6hgne0uu` |
| **USDC**, tylko sieć **Ethereum (ERC-20)** | `0x014151fbcfF87039D7D09810f981f9194E335135` |

- **USDC wysyłaj wyłącznie w sieci Ethereum (ERC-20).** Wpłaty w innych sieciach (np. Base, Arbitrum, Polygon, BNB Chain, Tron, Solana) nie są obsługiwane i mogą zostać utracone.
- USDT nie jest przyjmowany.

- Przed wysłaniem porównaj adres znak po znaku z tym README na GitHubie. Uważaj na złośliwe oprogramowanie podmieniające adresy w schowku.
- Wpłata jest dobrowolna i nie daje żadnych praw, wsparcia technicznego ani gwarancji (patrz „Zastrzeżenia”).
- Chcesz wesprzeć autora oryginalnego programu? Jego tipbox jest w sekcji „Autorzy” powyżej.

## Znaki towarowe i prawa autorskie

*Stan na 27.09.2026. Każde twierdzenie poniżej ma podane źródło. Ta sekcja ma charakter informacyjny i nie stanowi porady prawnej.*

### Znak UNO

- **UNO®** jest zarejestrowanym znakiem towarowym **Mattel, Inc.** W rejestrze USPTO: nr rejestracji **1005397** (zgłoszenie nr 73015277), zarejestrowany 25.02.1975 dla gier karcianych (klasa 28), status aktywny, ostatnio odnowiony 14.08.2024 ([USPTO TSDR](https://tsdr.uspto.gov/statusview/sn73015277)).
- Mattel wymienia UNO wśród swoich marek flagowych ([Mattel: Brand Portfolio](https://corporate.mattel.com/brand-portfolio)).
- Ten projekt **nie jest powiązany z Mattel, Inc.**, nie jest przez nią sponsorowany, zatwierdzony ani wspierany.
- Nazwa „UNO” jest tu użyta **wyłącznie opisowo**: mówi, z jaką talią kart działa aplikacja. Nie oznacza pochodzenia ani producenta oprogramowania.
- Repozytorium **nie zawiera żadnych grafik, logotypów, ilustracji kart ani innych materiałów Mattel**. Karty na ekranie to kolorowe prostokąty z tekstem (np. `5`, `+2`, `STOP`), rysowane w HTML/CSS.
- Do działania potrzebna jest własna, fizyczna talia. Repozytorium jej nie dostarcza ani nie zastępuje.
- Pozostałe nazwy (np. Microsoft, Windows, .NET, GitHub, Bitcoin) należą do ich właścicieli i są użyte opisowo.

### Kod oryginalny (Rav3nPL/SeedGenerator)

- Autorem oryginalnego programu (`SeedGenerator/`, `SeedGenerator.sln`, pierwotny `index.html` i algorytm) jest **Rav3nPL**. Prawa autorskie do tego kodu należą do niego.
- Oryginalne repozytorium **nie ma licencji**: brak pliku LICENSE, a API GitHuba zwraca dla niego `"license": null` ([repozytorium](https://github.com/Rav3nPL/SeedGenerator)).
- Bez licencji utwór jest domyślnie objęty wyłącznym prawem autorskim. Brak licencji oznacza zasadniczo brak zgody twórcy na używanie, modyfikowanie i udostępnianie kodu ([choosealicense.com: No License](https://choosealicense.com/no-permission/), serwis prowadzony przez GitHub).
- Regulamin GitHuba (sekcja D.5, wersja z 27.04.2026) daje innym użytkownikom tylko prawo do **przeglądania i forkowania** publicznego repozytorium **w ramach serwisu GitHub** ([GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service#5-license-grant-to-other-users)). Nie jest to licencja open source.
- W związku z tym **ten fork nie udziela żadnej licencji** na kod oryginału ani na utwory zależne od niego. Rozpowszechnianie poza GitHubem, modyfikowanie do własnych celów lub użycie komercyjne wymaga zgody autora oryginału.
- Zalecana droga, zgodnie z choosealicense.com: poprosić autora o dodanie licencji (np. przez issue w oryginalnym repozytorium).

### Zmiany w tym forku

- Nowe pliki i zmiany (`uno-seed-studio.html`, port UNO w `index.html`, `INIT.py`, `deck.json`, ten README) są opublikowane do wglądu i do weryfikacji, **bez żadnej gwarancji** (patrz sekcja „Zastrzeżenia”).
- Ponieważ `index.html` jest zmodyfikowaną wersją kodu Rav3nPL, a oryginał nie ma licencji, **licencja tego forka zostanie ustalona dopiero po wyjaśnieniu licencji oryginału**.

### Lista słów BIP39

- Angielska lista 2048 słów BIP39 (wbudowana w `index.html`, `uno-seed-studio.html` oraz `SeedGenerator/Resources/english.txt`) jest **identyczna** z oficjalnym plikiem [`bip-0039/english.txt`](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt) z repozytorium `bitcoin/bips`. Zgodność sprawdzono sumą SHA-256 wszystkich trzech kopii.
- Specyfikacja [BIP-0039](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) (autorzy: Marek Palatinus, Pavol Rusnak, Aaron Voisine, Sean Bowe) jest udostępniona na **licencji MIT** („This BIP falls under the MIT License.”).

### Kryptografia

- SHA-256 i SHA-512 to publiczne standardy (FIPS 180-4). W wersjach HTML liczy je wbudowane w przeglądarkę Web Crypto API (`crypto.subtle`), bez zewnętrznych bibliotek.

> **English summary:** UNO® is a registered trademark of Mattel, Inc. (USPTO Reg. No. 1005397, card games, live). This project is not affiliated with, sponsored or endorsed by Mattel; the name only describes the compatible card deck, and no Mattel artwork or assets are included. The original SeedGenerator is by Rav3nPL and its repository has no license (GitHub API: `license: null`); GitHub's Terms (D.5) only allow viewing and forking within GitHub, so this fork grants no license to the original code or derivatives. The BIP39 English wordlist is byte-for-byte identical (SHA-256 verified) to `bitcoin/bips` `bip-0039/english.txt`; BIP-0039 is MIT-licensed. Not legal advice.
