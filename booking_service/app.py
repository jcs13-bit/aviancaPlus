from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import logging
import json
from flask_cors import CORS, cross_origin

# Configuración de logging
logging.basicConfig(filename='bookings.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

DB_HOST = os.getenv('DB_HOST', 'postgres-service')
DB_NAME = os.getenv('DB_NAME', 'bookings')
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

@app.route('/checkout', methods=['POST'])
@cross_origin()
def checkoutBooking():
    '''
     En este  punto, llamar al servicio de disponibilidad, en donde se verifica:
     1. Que no exista un numero mayor de bookings que contengan el vuelo con id especificado,
    '''

@app.route('/api/v1/bookings', methods=['POST'])
@cross_origin()
def crear_reserva():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'No JSON data found in request'}), 400
    user_id = data['user_id']
    
    logging.info(f"Reserva creada: {user_id}")
    flight_start_id = data['flight_start_id']
    flight_end_id = data['flight_end_id']
    hotel_id = data['hotel_id']
    start_date = data['start_date']
    end_date = data['end_date']
    payments = data.get('payments', [])
    linked_bookings = data.get('linked_bookings', [])
    logging.info(f"Reserva creada: {payments}")
    print(linked_bookings)

    status = 'Created'

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'INSERT INTO bookings (user_id, flight_start_id, flight_end_id, hotel_id, start_date, end_date, payments, linked_bookings, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *',
            (user_id, flight_start_id, flight_end_id, hotel_id, start_date, end_date, json.dumps(payments), json.dumps(linked_bookings), status)
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

@app.route('/api/v1/bookings', methods=['GET'])
@cross_origin()
def obtener_bookings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM bookings  ')
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(bookings), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/bookings/<int:id>', methods=['GET'])
@cross_origin()
def obtener_reserva(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM bookings WHERE id = %s', (id,))
        reserva = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(reserva), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/bookings/<int:id>', methods=['PUT'])
@cross_origin()
def modificar_reserva(id):
    data = request.get_json()
    user_id = data.get('user_id')
    flight_start_id = data.get('flight_start_id')
    flight_end_id = data.get('flight_end_id')
    client_id = data.get('client_id')
    hotel_id = data.get('hotel_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    payments = data.get('payments', [])
    linked_bookings = data.get('linked_bookings', [])
    status = data.get('status', 'Created')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'UPDATE bookings SET user_id = %s, flight_start_id = %s, flight_end_id = %s, hotel_id = %s, start_date = %s, end_date = %s, payments = %s, linked_bookings = %s, status = %s WHERE id = %s RETURNING *',
            (user_id, flight_start_id, flight_end_id, hotel_id, start_date, end_date, json.dumps(payments), json.dumps(linked_bookings), status, id)
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

@app.route('/api/v1/bookings/<int:id>', methods=['DELETE'])
@cross_origin()
def borrar_reserva(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Obtener la reserva actual
        cursor.execute('SELECT * FROM bookings WHERE id = %s', (id,))
        reserva = cursor.fetchone()

        if reserva:
            # Si hay relación entre hotel y vuelo, cancela ambos
            if reserva['linked_bookings']:
                for linked_booking_id in reserva['linked_bookings']:
                    cursor.execute('UPDATE bookings SET status = %s WHERE id = %s', ('cancelled', linked_booking_id))

            # Insertar la reserva cancelada en bookings_borradas
            cursor.execute(
                'INSERT INTO bookings_borradas (user_id, flight_start_id, flight_end_id, hotel_id, start_date, end_date, payments, linked_bookings, status, deleted_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())',
                (reserva['user_id'], reserva['flight_start_id'], reserva['flight_end_id'], reserva['hotel_id'], reserva['start_date'], reserva['end_date'], reserva['payments'], reserva['linked_bookings'], 'cancelled')
            )
            
            # Eliminar la reserva
            cursor.execute('DELETE FROM bookings WHERE id = %s RETURNING *', (id,))
            conn.commit()

            # Log de borrado de reserva
            logging.info(f"Reserva borrada: {reserva}")

        cursor.close()
        conn.close()
        return jsonify(reserva), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

