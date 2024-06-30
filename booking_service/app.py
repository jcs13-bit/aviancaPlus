from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'reservations')
DB_USER = os.getenv('DB_USER', 'user')
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
        return jsonify(new_reserva), 201
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
        cursor.close()
        conn.close()
        return jsonify(deleted_reserva), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)