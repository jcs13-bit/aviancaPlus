from flask import Flask
import logging
import requests 
# Configuración de logging
logging.basicConfig(filename='availability.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')

app = Flask(__name__)


@app.route('/checkout', methods=['POST'])
def checkoutBooking():
    '''
     En este  punto, llamar al servicio de disponibilidad, en donde se verifica:
     1. Que no exista un numero mayor de bookings que contengan el vuelo con id especificado,
    '''
    logging.info("success")
    response = requests.get(
            "http://bookings-service:5000/bookings"
    )
    logging.info(f"Request:{response.json}")
    return response.content    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

