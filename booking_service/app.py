from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import logging

# Configuración de logging
logging.basicConfig(filename='reservas.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'reservations')
DB_USER = os.getenv('DB_USER', 'postgres1')
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

@app.route('/reservas', methods=['POST'])
def crear_reserva():
    data = request.get_json()
    user_id = data['user_id']
    hotel_id = data.get('hotel_id')
    vuelo_id = data.get('vuelo_id')
    fecha = data['fecha']

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'INSERT INTO reservas (user_id, hotel_id, vuelo_id, fecha) VALUES (%s, %s, %s, %s) RETURNING *',
            (user_id, hotel_id, vuelo_id, fecha)
        )
        new_reserva = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        # Log de creación de reserva
        logging.info(f"Reserva creada: {new_reserva}")

        return jsonify(new_reserva), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reservas', methods=['GET'])
def obtener_reservas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM reservas')
        reservas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(reservas), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reservas/<int:id>', methods=['GET'])
def obtener_reserva(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM reservas WHERE id = %s', (id,))
        reserva = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(reserva), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reservas/<int:id>', methods=['PUT'])
def modificar_reserva(id):
    data = request.get_json()
    user_id = data.get('user_id')
    hotel_id = data.get('hotel_id')
    vuelo_id = data.get('vuelo_id')
    fecha = data.get('fecha')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'UPDATE reservas SET user_id = %s, hotel_id = %s, vuelo_id = %s, fecha = %s WHERE id = %s RETURNING *',
            (user_id, hotel_id, vuelo_id, fecha, id)
        )
        updated_reserva = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        # Log de modificación de reserva
        logging.info(f"Reserva modificada: {updated_reserva}")

        return jsonify(updated_reserva), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reservas/<int:id>', methods=['DELETE'])
def borrar_reserva(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('DELETE FROM reservas WHERE id = %s RETURNING *', (id,))
        deleted_reserva = cursor.fetchone()
        if deleted_reserva:
            cursor.execute(
                'INSERT INTO reservas_borradas (user_id, hotel_id, vuelo_id, fecha, deleted_at) VALUES (%s, %s, %s, %s, NOW())',
                (deleted_reserva['user_id'], deleted_reserva['hotel_id'], deleted_reserva['vuelo_id'], deleted_reserva['fecha'])
            )
            conn.commit()

            # Log de borrado de reserva
            logging.info(f"Reserva borrada: {deleted_reserva}")

        cursor.close()
        conn.close()
        return jsonify(deleted_reserva), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)