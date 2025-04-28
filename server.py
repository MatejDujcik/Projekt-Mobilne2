import sqlite3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

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
    cursor.execute('SELECT id, nazov FROM mesta')
    rows = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'nazov': row[1]} for row in rows]


def get_mesto_by_id(id):
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nazov, sila_vetra, mm_zrazky, teplota FROM mesta WHERE id = ?', (id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'nazov': row[1], 'sila_vetra': row[2], 'mm_zrazky': row[3], 'teplota': row[4]}
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

def update_mesto(id, sila_vetra, mm_zrazky, teplota):
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE mesta
        SET sila_vetra = ?, mm_zrazky = ?, teplota = ?
        WHERE id = ?
    ''', (sila_vetra, mm_zrazky, teplota, id))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0

def delete_mesto(id):
    conn = sqlite3.connect('pocasie.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mesta WHERE id = ?', (id,))
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
            id_str = parsed_path.path.split('/api/mesto/')[1]
            if not id_str.isdigit():
                self.respond_json(400, {'error': 'Neplatne ID'})
                return
            mesto = get_mesto_by_id(int(id_str))
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
            id_str = self.path.split('/api/mesto/')[1]
            if not id_str.isdigit():
                self.respond_json(400, {'error': 'Neplatne ID'})
                return
            data = self.read_json()
            if not all(key in data for key in ['sila_vetra', 'mm_zrazky', 'teplota']):
                self.respond_json(400, {'error': 'Chyba udajov'})
                return
            success = update_mesto(int(id_str), data['sila_vetra'], data['mm_zrazky'], data['teplota'])
            if success:
                self.respond_json(200, {'message': 'Mesto aktualizovane'})
            else:
                self.respond_json(404, {'error': 'Mesto nenajdene'})
        else:
            self.respond_json(404, {'error': 'Nespravna cesta'})

    def do_DELETE(self):
        if self.path.startswith('/api/mesto/'):
            id_str = self.path.split('/api/mesto/')[1]
            if not id_str.isdigit():
                self.respond_json(400, {'error': 'Neplatne ID'})
                return
            success = delete_mesto(int(id_str))
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
