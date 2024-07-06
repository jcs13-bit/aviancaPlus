from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import logging
from flask_cors import CORS, cross_origin

# Configuración de logging
logging.basicConfig(filename='payments.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

DB_HOST = os.getenv('DB_HOST', 'postgres-service')
DB_NAME = os.getenv('DB_NAME', 'payments')
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



@app.route('/api/v1/payment', methods=['POST'])
@cross_origin()
def create_hotel():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'No JSON data found in request'}), 400
    bookingId= data["bookingId"]
    paymentDate= data["paymentDate"]
    amount = data["amount"]
    paymentMethod=data["paymentMethod"]
    status=data["status"]
    transactionId=data["transactionId"]

    
    logging.info(f"Parametros de creacion: {bookingId,paymentDate,amount,paymentMethod,status,transactionId}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'INSERT INTO  payments (bookingId,paymentDate,amount,paymentMethod,status,transactionId) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *',
            (bookingId,paymentDate,amount,paymentMethod,status,transactionId))
        new_payment = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        # Log de creación de payment
        logging.info(f"Payment creado: {new_payment}")

        return jsonify(new_payment), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/payment', methods=['GET'])
@cross_origin()
def get_payments():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM payments  ')
        payments = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(payments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/payment/<int:id>', methods=['GET'])
@cross_origin()
def get_payment(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM payments WHERE id = %s', (id,))
        payment = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(payment), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

