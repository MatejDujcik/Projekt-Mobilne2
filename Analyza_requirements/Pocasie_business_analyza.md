
# Biznis analýza – Aplikácia na predpoveď počasia

## Účel a cieľ aplikácie

Cieľom aplikácie je umožniť používateľovi evidovať meteorologické údaje o rôznych mestách, ako sú:
- sila vetra,
- množstvo zrážok (v mm),
- teplota (v °C).

## Architektúra systému

### Backend
Backend je implementovaný v jazyku Python s využitím knižnice `http.server` a databázy SQLite. Slúži ako REST API pre klientskú aplikáciu.
- **Jazyk**: Python 3
- **Server**: `http.server`
- **Databáza**: SQLite (`pocasie.db`)
- **API štýl**: RESTful JSON API
---

### Frontend
- **Technológie**: HTML5, CSS3, JavaScript (ES6+)
- **Knižnice**: Bootstrap 5
- **Komunikácia**: Fetch API
- **Štruktúra**: Single Page Application (SPA)

## Databázová štruktúra

Používa sa databáza SQLite `pocasie.db`, ktorá obsahuje tabuľku:

### `mesta`
| Stĺpec       | Typ     | Popis                        |
|--------------|----------|------------------------------|
| `id`         | INTEGER  | Primárny kľúč, autoinkrement |
| `nazov`      | TEXT     | Unikátny názov mesta         |
| `sila_vetra` | REAL     | Sila vetra (napr. km/h)      |
| `mm_zrazky`  | REAL     | Zrážky v mm                  |
| `teplota`    | REAL     | Teplota v °C                 |

---

## Frontendové komponenty

### 1. Hlavná stránka
```html
<div id="main-content">
  <div class="row" id="cityCards">
    <!-- Dynamicky generované karty miest -->
  </div>
</div>

---

### 2. Detail mesta

function showMestoDetail(id) {
  // Načíta detail mesta a zobrazí animáciu počasia
  // Používa weather-bg div pre vizualizáciu
}

---

### 3. Administračný panel
<div class="admin-panel">
  <input id="cityName" placeholder="Názov mesta">
  <input id="wind" type="number" placeholder="Vietor">
  <button id="addBtn">Pridať</button>
  <button id="editBtn">Upraviť</button>
  <button id="deleteBtn">Vymazať</button>
</div>

---

### REST API – dokumentácia

### `GET /api/mesta`
- Získa zoznam všetkých miest (iba `id` a `nazov`).
- **Status:** 200 OK
- **Výstup:**
```json
[
  { "id": 1, "nazov": "Bratislava" },
  { "id": 2, "nazov": "Košice" }
]
```

---

### `GET /api/mesto/<id>`
- Získa detailné informácie o konkrétnom meste podľa `id`.
- **Status:**
  - 200 OK – úspech
  - 400 Bad Request – ak `id` nie je číslo
  - 404 Not Found – ak mesto neexistuje
- **Výstup:**
```json
{
  "id": 1,
  "nazov": "Bratislava",
  "sila_vetra": 10.2,
  "mm_zrazky": 5.0,
  "teplota": 22.4
}
```

---

### `POST /api/mesto`
- Vytvorí nové mesto s predpoveďou.
- **Vstup (JSON body):**
```json
{
  "nazov": "Bratislava",
  "sila_vetra": 8.5,
  "mm_zrazky": 1.0,
  "teplota": 21.5
}
```
- **Status:**
  - 201 Created – mesto vytvorené
  - 400 Bad Request – chýbajúce údaje
  - 409 Conflict – mesto už existuje

---

### `PUT /api/mesto/<id>`
- Aktualizuje počasie existujúceho mesta.
- **Vstup (JSON body):**
```json
{
  "sila_vetra": 9.0,
  "mm_zrazky": 0.5,
  "teplota": 23.0
}
```
- **Status:**
  - 200 OK – úspešne aktualizované
  - 400 Bad Request – neplatné ID alebo chýbajúce údaje
  - 404 Not Found – mesto neexistuje

---

### `DELETE /api/mesto/<id>`
- Vymaže mesto podľa ID.
- **Status:**
  - 200 OK – mesto zmazané
  - 400 Bad Request – neplatné ID
  - 404 Not Found – mesto neexistuje

---

## Vizualizácia počasia
- Frontend implementuje dynamické pozadie podľa aktuálnych podmienok: 

if (mm_zrazky >= 10 && teplota > 0) {
  animation = "rain.gif";
} else if (mm_zrazky >= 10 && teplota <= 0) {
  animation = "snow.gif";
} else if (sila_vetra > 5) {
  animation = "wind.gif";
} else {
  animation = "sun.gif";
}

---

## Responzívny dizajn
Media queries pre rôzne veľkosti obrazoviek

@media (max-width: 767px) {
  .city-card {
    width: 100%;
  }
}

## Validácie a kontroly

- `id` sa overuje, či je číselné
- Mesto musí mať unikátny názov
- Overujú sa povinné hodnoty pri `POST` a `PUT`
- Chyby sú vrátené ako štruktúrované JSON odpovede

---

## Scenáre použitia

1. **Pridanie nového mesta:**
   - Klient odošle `POST /api/mesto`
   - Server uloží mesto do databázy

2. **Úprava údajov o počasí:**
   - Klient odošle `PUT /api/mesto/3` s novými údajmi

3. **Získanie zoznamu všetkých miest:**
   - Klient volá `GET /api/mesta`

4. **Zobrazenie detailu mesta:**
   - Klient volá `GET /api/mesto/2`

5. **Odstránenie mesta:**
   - Klient zavolá `DELETE /api/mesto/1`

---

## Testovacie scenáre

1. Pridanie mesta
  Vyplnenie formulára -> kontrola zobrazenia v zozname

2. Edit údajov 
  Zmena hodnôt -> kontrola aktualizácie

3. Mazanie záznamu
  Odstránenie mesta -> kontrola vymazania zo zoznamu

4. Chybové stavy: 
  Duplicitné mesto
  Neplatné hodnoty vstupov

## Možnosti budúceho rozšírenia

1. Autentifikácia:
Pridanie používateľských rolí

2. Historické údaje:
Zobrazovanie trendov počasia

3. Mapová integrácia:
Zobrazenie miest na interaktívnej mape