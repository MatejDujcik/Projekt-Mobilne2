import sqlite3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, unquote

def create_db():
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

def get_all_mesta():
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nazov, sila_vetra, mm_zrazky, teplota FROM mesta')
    rows = cursor.fetchall()
    conn.close()
    return [{'nazov': row[0], 'sila_vetra': row[1], 'mm_zrazky': row[2], 'teplota': row[3]} for row in rows]

def get_mesto_by_name(nazov):
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nazov, sila_vetra, mm_zrazky, teplota FROM mesta WHERE nazov = ?', (nazov,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'nazov': row[0], 'sila_vetra': row[1], 'mm_zrazky': row[2], 'teplota': row[3]}
    else:
        return None

def insert_mesto(nazov, sila_vetra, mm_zrazky, teplota):
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mesta (nazov, sila_vetra, mm_zrazky, teplota)
        VALUES (?, ?, ?, ?)
    ''', (nazov, sila_vetra, mm_zrazky, teplota))
    conn.commit()
    conn.close()

def update_mesto(nazov, sila_vetra, mm_zrazky, teplota):
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE mesta
        SET sila_vetra = ?, mm_zrazky = ?, teplota = ?
        WHERE nazov = ?
    ''', (sila_vetra, mm_zrazky, teplota, nazov))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0

def delete_mesto(nazov):
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mesta WHERE nazov = ?', (nazov,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/mesta':
            mesta = get_all_mesta()
            self.respond_json(200, mesta)
        elif parsed_path.path.startswith('/api/mesto/'):
            nazov = unquote(parsed_path.path.split('/api/mesto/')[1])
            mesto = get_mesto_by_name(nazov)
            if mesto:
                self.respond_json(200, mesto)
            else:
                self.respond_json(404, {'error': 'Mesto nenajdene'})
        else:
            self.respond_json(404, {'error': 'Nespravna cesta'})

    def do_POST(self):
        if self.path == '/api/mesto':
            data = self.read_json()
            if not all(key in data for key in ['nazov', 'sila_vetra', 'mm_zrazky', 'teplota']):
                self.respond_json(400, {'error': 'Chyba udajov'})
                return
            try:
                insert_mesto(data['nazov'], data['sila_vetra'], data['mm_zrazky'], data['teplota'])
                self.respond_json(201, {'message': 'Mesto pridane'})
            except sqlite3.IntegrityError:
                self.respond_json(409, {'error': 'Mesto uz existuje'})
        else:
            self.respond_json(404, {'error': 'Nespravna cesta'})

    def do_PUT(self):
        if self.path.startswith('/api/mesto/'):
            nazov = unquote(self.path.split('/api/mesto/')[1])
            data = self.read_json()
            if not all(key in data for key in ['sila_vetra', 'mm_zrazky', 'teplota']):
                self.respond_json(400, {'error': 'Chyba udajov'})
                return
            success = update_mesto(nazov, data['sila_vetra'], data['mm_zrazky'], data['teplota'])
            if success:
                self.respond_json(200, {'message': 'Mesto aktualizovane'})
            else:
                self.respond_json(404, {'error': 'Mesto nenajdene'})
        else:
            self.respond_json(404, {'error': 'Nespravna cesta'})

    def do_DELETE(self):
        if self.path.startswith('/api/mesto/'):
            nazov = unquote(self.path.split('/api/mesto/')[1])
            success = delete_mesto(nazov)
            if success:
                self.respond_json(200, {'message': 'Mesto vymazane'})
            else:
                self.respond_json(404, {'error': 'Mesto nenajdene'})
        else:
            self.respond_json(404, {'error': 'Nespravna cesta'})

    def read_json(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        return json.loads(body)

    def respond_json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def run_server():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, MyHandler)
    print('Server bezi na porte 3000...')
    httpd.serve_forever()

if __name__ == '__main__':
    create_db()
    run_server()
