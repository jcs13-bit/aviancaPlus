from flask import Flask, request, jsonify
import logging
import requests 
from datetime import datetime

# Configuración de logging
logging.basicConfig(filename='availability.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')

app = Flask(__name__)


@app.route('/api/v1/availability', methods=['GET'])
def checkAvailability():
    # Obtener los parámetros de la URL
    hotel_id = request.args.get('hotel_id')
    flight_start_id = request.args.get('flight_start_id')
    flight_end_id = request.args.get('flight_end_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    bookingsRequest = requests.get(
            "http://bookings-service:5000/api/v1/bookings"
    )
    bookings = bookingsRequest.json()

    response = {}

    if(flight_start_id):
        response["isFlightStartAvailable"] = checkFlightAvailability(flight_start_id, bookings)

    if(flight_end_id):
        response["isFlightEndAvailable"] = checkFlightAvailability(flight_end_id, bookings)

    if(hotel_id):
        response["isHotelAvailable"] = checkHotelAvailability(hotel_id, start_date, end_date, bookings)
    

    logging.info(f"Request:{response}")
    return jsonify(response) 


def checkFlightAvailability(flight_id, bookings):
    if(flight_id):
        flight = requests.get(f"http://flight-service/api/v1/flight/{flight_id}")
        capacity = flight["capacity"]

    matches = [each for each in bookings if each.get('flight_start_id') == flight_id or each.get('flight_end_id') == flight_id]

    # Verificar la disponibilidad en base a la capacidad
    return len(matches) < capacity

def checkHotelAvailability(hotel_id, start_date, end_date, bookings):
    hotel_url = f'http://hotel-service/api/v1/hotel/{hotel_id}'

    # Obtener datos del hotel
    response = requests.get(hotel_url)
    hotel_data = response.json()
    hotel_capacity = hotel_data['capacity']

    start_date_unix = datetime.fromisoformat(start_date).timestamp() * 1000
    end_date_unix = datetime.fromisoformat(end_date).timestamp() * 1000
    current_bookings = 0

    for booking in bookings:
        if booking['hotel_id'] == hotel_id:
            booking_start_unix = datetime.fromisoformat(booking['start_date']).timestamp() * 1000
            booking_end_unix = datetime.fromisoformat(booking['end_date']).timestamp() * 1000
            if booking_start_unix >= start_date_unix and booking_start_unix <= end_date_unix:
                current_bookings += 1
            if booking_end_unix >= start_date_unix and booking_end_unix <= end_date_unix:
                current_bookings += 1

 
    return current_bookings < hotel_capacity

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)






