from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import logging
from flask_cors import CORS, cross_origin

# Configuración de logging
logging.basicConfig(filename='hotel.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

DB_HOST = os.getenv('DB_HOST', 'postgres-service')
DB_NAME = os.getenv('DB_NAME', 'hotels')
DB_USER = os.getenv('DB_USER', 'postgresuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_PORT = os.getenv('DB_PORT', '5432')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn



@app.route('/api/v1/hotel', methods=['POST'])
@cross_origin()
def create_hotel():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'No JSON data found in request'}), 400
    name = data['name']
    address = data['address']
    capacity = data['capacity']
    logging.info(f"Parametros de creacion: {name,address,capacity}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'INSERT INTO  hotels (name, address, capacity) VALUES (%s, %s, %s) RETURNING *',
            (name, address, capacity))
        new_hotel = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        # Log de creación de hotel
        logging.info(f"Hotel creado: {new_hotel}")

        return jsonify(new_hotel), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/hotel', methods=['GET'])
@cross_origin()
def get_hotels():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM hotels  ')
        hotels = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(hotels), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/hotel/<int:id>', methods=['GET'])
@cross_origin()
def get_hotel(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM hotels WHERE id = %s', (id,))
        hotel = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(hotel), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

