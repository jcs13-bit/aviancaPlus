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
    flight_start_id = data['flight_start_id']  if 'flight_start_id' in data else None
    flight_end_id = data['flight_end_id']  if 'flight_end_id' in data else None
    hotel_id = data['hotel_id']  if 'hotel_id' in data else None
    start_date = data['start_date']  if 'start_date' in data else None
    end_date = data['end_date']  if 'end_date' in data else None
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
        bookings = getBookingsArray()  
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
        cursor.close()
        conn.close()

        if reserva:
            logging.info("Going into deleteBookingsRecursive from borrar_reserva")
            deleteBookingsRecursive(reserva)
        logging.info(f"Returning to borrar_reserva")
        
        return jsonify(reserva), 200
    except Exception as e:
        return jsonify({'error in borrar_reserva': str(e)}), 500

def deleteBookingsRecursive(booking):
    logging.info(f"Deleting booking recursive: {booking['id']}")
    parentBookings= getParentBookings(booking['id'])
    if parentBookings:
       for parentBooking in parentBookings:
           return deleteBookingsRecursive(parentBooking)
    if not parentBookings:
     
        deletedBooking = deleteIndividualBooking(booking['id'])
        linked_bookings = booking["linked_bookings"] if isinstance(booking["linked_bookings"], list) else json.loads(booking["linked_bookings"])
        logging.info(f"reserve borrada y volvio al recursive delete with id {deletedBooking['id']}")
        childBookings = getBookingsById(linked_bookings)
        logging.info(f"Child bookings for booking with id: {booking['id'], childBookings}")
        if childBookings:
            for childBooking in childBookings:
                logging.info(f"Deleting child with id {childBooking['id']}")
                return deleteBookingsRecursive(childBooking)
        if not childBookings:
            logging.info(f"no childs, returning deleted booking")
            return deletedBooking
           

def getParentBookings(booking_id):

    bookings = getBookingsArray()
    filtered_bookings = [booking for booking in bookings if booking_id in booking['linked_bookings']]

    return filtered_bookings

def getBookingsArray():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM bookings  ')
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return bookings

    
def getBookingsById(ids):
    allBookings = getBookingsArray()
    logging.info(f"getting bookings with ids {ids}")
    bookings = [booking for booking in allBookings if booking['id'] in ids]  
    return bookings 


def deleteIndividualBooking(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Obtener la reserva actual
    cursor.execute('SELECT * FROM bookings WHERE id = %s', (id,))
    reserva = cursor.fetchone()
    logging.info(f"Reserva a borrar: {id}")

    if reserva:
        # Verificar y convertir los campos JSON a cadenas si es necesario
        payments = reserva["payments"] if isinstance(reserva["payments"], str) else json.dumps(reserva["payments"])
        linked_bookings = reserva["linked_bookings"] if isinstance(reserva["linked_bookings"], str) else json.dumps(reserva["linked_bookings"])

        # Insertar la reserva cancelada en bookings_borradas
        cursor.execute(
            'INSERT INTO bookings_borradas (user_id, flight_start_id, flight_end_id, hotel_id, start_date, end_date, payments, linked_bookings, status, deleted_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())',
            (reserva['user_id'], reserva['flight_start_id'], reserva['flight_end_id'], reserva['hotel_id'], reserva['start_date'], reserva['end_date'], payments, linked_bookings, 'cancelled')
        )
        # Eliminar la reserva
        cursor.execute('DELETE FROM bookings WHERE id = %s RETURNING *', (id,))
        conn.commit()

        # Log de borrado de reserva
        logging.info(f"Reserva borrada: {reserva}")

    cursor.close()
    conn.close()
    return reserva
    







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

