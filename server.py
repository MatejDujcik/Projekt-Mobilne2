from flask import Flask
from flask_cors import CORS  # type: ignore

app = Flask(__name__)
CORS(app)  # povolí požiadavky z frontendovej časti (napr. cez fetch)

@app.route('/')
def home():
    return 'Ahoj'

@app.route('/api/test', methods=['GET'])
def test_api():
    print("Volanie API funguje zo servera.")
    return {'message': 'Funguje to zo servera'}, 200

if __name__ == '__main__':
    app.run(port=3000)