# Business analýza – Aplikácia na predpoveď počasia

## 1. Úvod

Cieľom projektu je vytvoriť jednoduchú webovú aplikáciu na správu a zobrazovanie predpovede počasia pre vybrané slovenské mestá. Projekt je realizovaný v rámci predmetu **Internetové a mobilné aplikácie 2**. Aplikácia demonštruje prácu s REST API, databázou a voliteľne aj s WebSocket technológiou pre živé aktualizácie dát.

## 2. Funkčný popis aplikácie

Frontend umožňuje používateľovi zadať počasie (predpoveď) na 3 dni pre vopred definované mestá (napr. Bratislava, Žilina, Košice). Predpoveď obsahuje denné a nočné hodnoty týchto parametrov:

- **Počasie**: zamračené / jasno / polojasno
- **Vietor**: sila vetra (číselná hodnota)
- **Slnko**: intenzita (voliteľný údaj, môže byť použitý neskôr)

Používateľ môže:
- Zadať novú predpoveď pre konkrétne mesto
- Zobraziť existujúcu predpoveď (načítanú z databázy)
- Automaticky získať aktualizované údaje (cez WebSocket)

## 3. REST API

### 3.1 `GET /weather?city=Bratislava`

**Popis**: Získanie aktuálnej trojdňovej predpovede pre dané mesto.

**Odpoveď**:
```json
{
  "city": "Bratislava",
  "forecast": [
    {
      "day": "2025-04-13",
      "daytime": {
        "weather": "slnečno",
        "wind": 3
      },
      "night": {
        "weather": "polojasno",
        "wind": 1
      }
    }
  ]
}
```

### 3.2 `POST /weather`

**Popis**: Zápis novej trojdňovej predpovede pre konkrétne mesto.

**Telo požiadavky**:
```json
{
  "city": "Žilina",
  "forecast": [
    {
      "day": "2025-04-14",
      "daytime": { "weather": "zamračené", "wind": 2 },
      "night": { "weather": "jasno", "wind": 1 }
    }
  ]
}
```

**Validácia**:
- Nie je povolené zadávať predpoveď do minulosti
- Každý deň môže mať maximálne jeden zápis pre dennú a nočnú časť

## 4. WebSocket komunikácia

WebSocket slúži na notifikáciu klientov o zmene predpovede. Klienti, ktorí majú otvorenú stránku, môžu dostať správu s aktualizovanými dátami bez potreby obnovenia.

**Formát správy cez WebSocket**:
```json
{
  "type": "update",
  "city": "Košice",
  "updatedForecast": [
    {
      "day": "2025-04-14",
      "daytime": { "weather": "slnečno", "wind": 2 },
      "night": { "weather": "jasno", "wind": 1 }
    }
  ]
}
```

## 5. Databázová štruktúra (SQLite)

```sql
CREATE TABLE forecast (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  city TEXT NOT NULL,
  date DATE NOT NULL,
  time_of_day TEXT CHECK(time_of_day IN ('day', 'night')),
  weather TEXT,
  wind INTEGER,
  UNIQUE(city, date, time_of_day)
);
```

- Každý záznam reprezentuje jeden časť dňa (deň alebo noc) pre dané mesto a dátum.
- Zabezpečená je jedinečnosť kombinácie `city + date + time_of_day`.

## 6. Backendová logika

- Pri zápise kontrolujeme platnosť dátumu a či daná kombinácia neexistuje.
- Predpoveď je automaticky generovaná na 3 dni od aktuálneho dňa (nastaviteľné).
- WebSocket môže byť použitý na pravidelné odosielanie aktualizácií každých X sekúnd.

## 7. Používateľské scenáre

**Scenár A – Pridanie predpovede**:
1. Používateľ zvolí mesto a vyplní denné/nočné počasie na 3 dni.
2. Aplikácia odošle `POST /weather`.
3. Predpoveď sa uloží do databázy a pošle cez WebSocket.

**Scenár B – Zobrazenie predpovede**:
1. Používateľ navštívi stránku a vyberie mesto.
2. Frontend pošle `GET /weather?city=Mesto`.
3. Zobrazia sa údaje na 3 dni dopredu.

**Scenár C – Živá aktualizácia**:
1. Klient je pripojený cez WebSocket.
2. Server pošle aktualizáciu predpovede.
3. UI sa zmení bez obnovy stránky.

## 8. Technologický stack

- **Frontend**: HTML + JavaScript / React (voliteľné)
- **Backend**: Python (FastAPI / Flask) + SQLite
- **WebSocket server**: `websockets` knižnica v Pythone
- **Databáza**: SQLite – ľahká a vhodná pre malý projekt

## 9. Bezpečnostné a validačné kontroly

- Kontrola, že sa nezadávajú historické dáta
- Overenie požadovaných polí pri POST požiadavke
- Obmedzenie zápisu pre tie isté kombinácie dátum + časť dňa
- Odolnosť WebSocket servera voči výpadkom klientov

## 10. Možnosti rozšírenia

- Získavanie dát z verejného API (napr. OpenWeatherMap)
- Predikcia počasia pomocou strojového učenia
- Možnosť upraviť predpoveď alebo ju vymazať
- Pridanie prihlasovania a správy používateľov
- Pridanie mobilnej verzie alebo PWA

---

Tento dokument slúži ako komplexná analýza návrhu aplikácie a zároveň ako podklad pre implementáciu backendovej aj frontendovej časti.