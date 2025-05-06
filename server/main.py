from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import sqlite3
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Pocasie API", description="API pre spravu pocasia v mestach", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class MestoCreate(BaseModel):
    nazov: str
    sila_vetra: float
    mm_zrazky: float
    teplota: float

class MestoUpdate(BaseModel):
    sila_vetra: float
    mm_zrazky: float
    teplota: float

class MestoResponse(BaseModel):
    id: int
    nazov: str
    sila_vetra: float | None
    mm_zrazky: float | None
    teplota: float | None

class MestoListItem(BaseModel):
    id: int
    nazov: str

def create_db():
    """Initialize the SQLite database and create the mesta table."""
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mesta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nazov TEXT UNIQUE NOT NULL,
            sila_vetra REAL,
            mm_zrazky REAL,
            teplota REAL
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    """Run database initialization on application startup."""
    create_db()

@app.get("/api/mesta", response_model=List[MestoListItem], summary="Get all cities", 
         description="Retrieve a list of all cities with their IDs and names.")
async def get_all_mesta():
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nazov FROM mesta')
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "nazov": row[1]} for row in rows]

@app.get("/api/mesto/{id}", response_model=MestoResponse, summary="Get city by ID",
         description="Retrieve detailed weather information for a specific city by its ID.")
async def get_mesto_by_id(id: int):
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nazov, sila_vetra, mm_zrazky, teplota FROM mesta WHERE id = ?', (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesto nenajdene")
    return {
        "id": row[0],
        "nazov": row[1],
        "sila_vetra": row[2],
        "mm_zrazky": row[3],
        "teplota": row[4]
    }

@app.post("/api/mesto", status_code=status.HTTP_201_CREATED, summary="Create a new city",
          description="Add a new city with weather information to the database.")
async def create_mesto(mesto: MestoCreate):
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO mesta (nazov, sila_vetra, mm_zrazky, teplota)
            VALUES (?, ?, ?, ?)
        ''', (mesto.nazov, mesto.sila_vetra, mesto.mm_zrazky, mesto.teplota))
        conn.commit()
        return {"message": "Mesto pridane"}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Mesto uz existuje")
    finally:
        conn.close()

@app.put("/api/mesto/{id}", summary="Update city weather", 
         description="Update weather information for a specific city by its ID.")
async def update_mesto(id: int, mesto: MestoUpdate):
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE mesta
        SET sila_vetra = ?, mm_zrazky = ?, teplota = ?
        WHERE id = ?
    ''', (mesto.sila_vetra, mesto.mm_zrazky, mesto.teplota, id))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesto nenajdene")
    return {"message": "Mesto aktualizovane"}

@app.delete("/api/mesto/{id}", summary="Delete a city",
            description="Remove a city and its weather information from the database by its ID.")
async def delete_mesto(id: int):
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mesta WHERE id = ?', (id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesto nenajdene")
    return {"message": "Mesto vymazane"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)