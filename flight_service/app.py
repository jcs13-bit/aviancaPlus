from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import logging
from flask_cors import CORS, cross_origin

# Configuración de logging
logging.basicConfig(filename='flight.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

DB_HOST = os.getenv('DB_HOST', 'postgres-service')
DB_NAME = os.getenv('DB_NAME', 'flights')
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



@app.route('/api/v1/flight', methods=['POST'])
@cross_origin()
def create_flight():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'No JSON data found in request'}), 400
    start_date = data['start_date']
    end_date = data['end_date']
    start_address=data['start_address']
    end_address=data['end_address']
    capacity = data['capacity']
    logging.info(f"Parametros de creacion: {start_date,end_date,start_address,end_address,capacity}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'INSERT INTO  flights (start_date,end_date,start_address,end_address,capacity) VALUES (%s, %s, %s,%s,%s) RETURNING *',
            (start_date,end_date,start_address,end_address,capacity))
        new_flight = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        # Log de creación de flight
        logging.info(f"flight creado: {new_flight}")

        return jsonify(new_flight), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/flight', methods=['GET'])
@cross_origin()
def get_flights():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM flights  ')
        flights = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(flights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/flight/<int:id>', methods=['GET'])
@cross_origin()
def get_flight(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM flights WHERE id = %s', (id,))
        flight = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(flight), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/v1/flight/<int:id>', methods=['PUT'])
@cross_origin()
def update_flight(id):
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        start_address = data.get('start_address')
        end_address = data.get('end_address')
        capacity = data.get('capacity')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                'UPDATE flights SET start_date = %s, end_date = %s, start_address = %s, end_address = %s, capacity = %s WHERE id = %s RETURNING *',
                (start_date, end_date, start_address, end_address, capacity, id)
            )
            updated_flight = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()

            # Log de actualización de vuelo
            logging.info(f"flight actualizado: {updated_flight}")

            return jsonify(updated_flight), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/v1/flight/<int:id>', methods=['DELETE'])
@cross_origin()
def delete_flight(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
            # Obtener el vuelo actual
        cursor.execute('SELECT * FROM flights WHERE id = %s', (id,))
        flight = cursor.fetchone()

        if flight:
            cursor.execute('DELETE FROM flights WHERE id = %s RETURNING *', (id,))
            deleted_flight = cursor.fetchone()
            conn.commit()

                # Log de borrado de vuelo
            logging.info(f"flight borrado: {deleted_flight}")

            cursor.close()
            conn.close()
            return jsonify(deleted_flight), 200
        else:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Vuelo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500        
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)