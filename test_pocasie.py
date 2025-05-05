import pytest
from fastapi.testclient import TestClient
from main import app, create_db
import sqlite3
import os


@pytest.fixture
def client():
    """Create a test client with an in-memory database."""
    # Create a fresh in-memory database for each test
    create_db()
    yield TestClient(app)
    # Clean up database file if it exists
    if os.path.exists('pocasie.db'):
        os.remove('pocasie.db')


@pytest.fixture
def setup_test_data():
    """Set up test data in the database."""
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mesta (nazov, sila_vetra, mm_zrazky, teplota)
        VALUES (?, ?, ?, ?)
    ''', ('Bratislava', 5.5, 2.0, 15.0))
    conn.commit()
    conn.close()


def test_get_all_mesta_empty(client):
    """Test retrieving all cities when database is empty."""
    response = client.get("/api/mesta")
    assert response.status_code == 200
    assert response.json() == []


def test_create_mesto(client):
    """Test creating a new city."""
    mesto_data = {
        "nazov": "Bratislava",
        "sila_vetra": 5.5,
        "mm_zrazky": 2.0,
        "teplota": 15.0
    }
    response = client.post("/api/mesto", json=mesto_data)
    assert response.status_code == 201
    assert response.json() == {"message": "Mesto pridane"}


def test_create_mesto_duplicate(client):
    """Test creating a city that already exists."""
    mesto_data = {
        "nazov": "Bratislava",
        "sila_vetra": 5.5,
        "mm_zrazky": 2.0,
        "teplota": 15.0
    }
    client.post("/api/mesto", json=mesto_data)
    response = client.post("/api/mesto", json=mesto_data)
    assert response.status_code == 409
    assert response.json() == {"detail": "Mesto uz existuje"}


def test_get_all_mesta_with_data(client, setup_test_data):
    """Test retrieving all cities with existing data."""
    response = client.get("/api/mesta")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["nazov"] == "Bratislava"
    assert response.json()[0]["id"] == 1


def test_get_mesto_by_id(client, setup_test_data):
    """Test retrieving a specific city by ID."""
    response = client.get("/api/mesto/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "nazov": "Bratislava",
        "sila_vetra": 5.5,
        "mm_zrazky": 2.0,
        "teplota": 15.0
    }


def test_get_mesto_by_id_not_found(client):
    """Test retrieving a non-existent city."""
    response = client.get("/api/mesto/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Mesto nenajdene"}


def test_update_mesto(client, setup_test_data):
    """Test updating an existing city's weather information."""
    update_data = {
        "sila_vetra": 6.0,
        "mm_zrazky": 3.0,
        "teplota": 16.0
    }
    response = client.put("/api/mesto/1", json=update_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Mesto aktualizovane"}

    # Verify update
    response = client.get("/api/mesto/1")
    assert response.json()["sila_vetra"] == 6.0
    assert response.json()["mm_zrazky"] == 3.0
    assert response.json()["teplota"] == 16.0


def test_update_mesto_not_found(client):
    """Test updating a non-existent city."""
    update_data = {
        "sila_vetra": 6.0,
        "mm_zrazky": 3.0,
        "teplota": 16.0
    }
    response = client.put("/api/mesto/999", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Mesto nenajdene"}


def test_delete_mesto(client, setup_test_data):
    """Test deleting an existing city."""
    response = client.delete("/api/mesto/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Mesto vymazane"}

    # Verify deletion
    response = client.get("/api/mesto/1")
    assert response.status_code == 404


def test_delete_mesto_not_found(client):
    """Test deleting a non-existent city."""
    response = client.delete("/api/mesto/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Mesto nenajdene"}