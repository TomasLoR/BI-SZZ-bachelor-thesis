# license_checker - Nástroj pro detekci licencí a podmínek použití na webu

Na internetu existuje mnoho zdrojů, které lze využít pro další zpracování. Některé jsou však chráněny licencemi nebo podmínkami použití (ToS). Cílem knihovny `license_checker` je detekovat a zpracovávat licenční podmínky na webových stránkách. Knihovna je prezentována v rámci prototypu webové aplikace.

## Spuštění prototypu webové aplikace

### Požadavky
- Nainstalovaný Docker a Docker Compose
- Připojení k internetu
- Pro využití AI modelů jsou potřeba API klíče:
  - **Hugging Face API klíč** - pro použití Mistral modelu ([Jak získat Hugging Face API klíč](https://www.geeksforgeeks.org/how-to-access-huggingface-api-key/))
  - **Google AI API klíč** - pro použití Gemini modelu ([Jak získat Google Gemini API klíč](https://www.geeksforgeeks.org/how-to-use-google-gemini-api-key/))
    - Poznámka: Pokud používaný Gemini model již není podporovaný (nebo se změnili rate limit podmínky), stačí vybrat jiný model z [dokumentace limitů Google AI](https://ai.google.dev/gemini-api/docs/rate-limits) a jeho kód (např. `gemini-2.5-flash-preview-04-17`) vložit do souboru `src/license_checker/models/gemini.py` v konstruktoru třídy `Gemini`. Aktuální seznam modelů a jejich kódů je dostupný na [stránce dokumentace modelů](https://ai.google.dev/gemini-api/docs/models).
  

### Spuštění aplikace
Pro spuštění prototypu webové aplikace použijte Docker Compose:

```bash
docker compose -f deployment/docker-compose.yml up --build -d
```

Po spuštění bude aplikace dostupná na adrese: [http://localhost:5000](http://localhost:5000)

### Ukončení aplikace
Pro ukončení a odstranění kontejnerů aplikace použijte:

```bash
docker compose -f deployment/docker-compose.yml down
```

---

## Modul LicenseDetector

### Přehled

Třída `LicenseDetector` umožňuje skenovat webové stránky a vyhledávat v nich informace o licencích. Provádí následující úkoly:
- **Kontrola souboru `robots.txt`:** Ověří, zda je procházení stránky povoleno.
- **Stažení a analýza HTML:** Stáhne stránku a zpracuje její obsah.
- **Vyhledání licenčních odkazů a textů:** Zaměřuje se na sekci patičky, kde se obvykle nachází přímý odkaz na licenci, popřípadě na ToS.
- **Extrakce textu:** Extrahuje jen takové části textu, které obsahují vybraná klíčová slova.
- **Identifikace typu licence:** Pokud je přítomna Creative Commons licence, určí její typ.

---

### Veřejné metody

#### `__init__(user_agent=None)`
- Inicializuje instanci `LicenseDetector`, nastaví HTTP relaci a použije zadaný User-Agent.
- **Parametry:**
  - `user_agent` (*str*, volitelné): Vlastní User-Agent pro HTTP požadavky. Pokud není zadán, použije se výchozí hodnota z parametrů.

#### `scan_websites(sites)`
- Skenuje seznam webových stránek a hledá informace o licencích.
- **Parametry:**
  - `sites` (*list*): Seznam URL adres webových stránek (řetězce), které mají být prohledány.
- **Vrací:**
  - Seznam slovníků ve formátu JSON, kde každý obsahuje informace o prohledané stránce. Například:

    ```json
    [
        {
            "website": "https://example.com",
            "invalidUrl": false,
            "blockedByRobotsTxt": false,
            "licenseLink": null,
            "licenseType": "Unknown",
            "relevantLinks": ["https://example.com/terms"],
            "licenseMentions": ["Creative Commons (CC)"],
            "content": "Example.com provides a platform for sharing and discovering digital content..."
        },
        {
            "website": "invalid_url.com",
            "invalidUrl": true,
            "blockedByRobotsTxt": false,
            "licenseLink": null,
            "licenseType": null,
            "relevantLinks": [],
            "licenseMentions": [],
            "content": null
        },
        {
            "website": "https://exampleBlocked.com",
            "invalidUrl": false,
            "blockedByRobotsTxt": true,
            "licenseLink": null,
            "licenseType": null,
            "relevantLinks": [],
            "licenseMentions": [],
            "content": null
        }
    ]
    ```

---

## Modul ModelManager

### Přehled

Třída `ModelManager` poskytuje způsob, jak pracovat s různými AI modely (Hugging Face Mistral a Google Gemini). Umožňuje využití modelů pro různé úkoly, jako je generování shrnutí textu či odpovědi na otázky týkající se tohoto shrnutí.

---

### Veřejné metody

#### `__init__(self)`
- Inicializuje instanci `ModelManager` a přiřadí modely, které jsou k dispozici pro použití.
- **Parametry:**
  - Žádné.

#### `get_model(self, model_name, api_key=None)`
- Načítá instanci modelu podle zadaného názvu modelu.
- **Parametry:**
  - `model_name` (*str*): Název modelu (respektive API), který má být načten. Podporované hodnoty jsou `"huggingface"` pro Mistral a `"googleai"` pro Gemini.
  - `api_key` (*str*, volitelně): API klíč pro přístup k modelům, které jej vyžadují.
- **Vrací:**
  - Instanci modelu (Mistral nebo Gemini), pokud je název modelu platný.
  - `None`, pokud není nalezen model s daným názvem.

#### `set_api_key(self, model_name, api_key)`
- Nastaví nebo aktualizuje API klíč pro konkrétní model.
- **Parametry:**
  - `model_name` (*str*): Název modelu, pro který se má nastavit API klíč.
  - `api_key` (*str*): API klíč, který má být nastaven.
- **Vrací:**
  - `True`, pokud byl klíč úspěšně nastaven.
  - `False`, pokud model neexistuje.

---

### Instance modelů

Po získání instance modelu pomocí metody `get_model()` můžete použít následující metody, které jsou společné pro všechny modely:

#### `summarize(data)`
- Vytvoří shrnutí licenčního textu nebo podmínek použití.
- **Parametry:**
  - `data` (*dict*): Slovník obsahující informace o webové stránce s následujícími klíči:
    - `website` (*str*): URL adresa webové stránky
    - `content` (*str*): Textový obsah licenčních podmínek nebo podmínek použití
- **Vrací:**
  - Původní slovník `data` rozšířený o klíč `summary` obsahující generované shrnutí textu
- **Vyjímky:**
  - `ValueError`: Pokud chybí API klíč, data nejsou validní nebo došlo k chybě při komunikaci s API

#### `answer_question(data, question)`
- Zodpoví otázku ohledně shrnutí licenčních podmínek.
- **Parametry:**
  - `data` (*dict*): Slovník obsahující informace o webové stránce včetně již vygenerovaného shrnutí (musí obsahovat klíč `summary`)
  - `question` (*str*): Otázka týkající se licenčního textu nebo podmínek použití
- **Vrací:**
  - Řetězec obsahující odpověď na položenou otázku
- **Vyjímky:**
  - `ValueError`: Pokud chybí API klíč, shrnutí, otázka nebo došlo k chybě při komunikaci s API

---

### Příklad použití

Viz [src/examples/scripts/license_checker_example.py](src/examples/scripts/license_checker_example.py).