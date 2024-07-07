from flask import Flask, request, jsonify
import logging
import time
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
        flight_id = int(flight_id)
        flight = requests.get(f"http://flights-service:5000/api/v1/flight/{flight_id}")
        flightData = flight.json()
        capacity = int(flightData["capacity"])
        matches = 0

        for booking in bookings:
            start_id = int(booking["flight_start_id"]) if booking["flight_start_id"] is not None else 0

            end_id = int(booking["flight_end_id"]) if booking["flight_end_id"] is not None else 0
            logging.info(f"BOOKING FSID: {start_id}, TARGET ID : {flight_id}, CAPACITY {capacity}, MATCHES:{matches}")
            if start_id == flight_id:
                logging.info(f"added one match")
                matches = matches + 1 
            if end_id == flight_id:
                logging.info(f"added one match")
                matches = matches + 1 

        

        

        # Verificar la disponibilidad en base a la capacidad
        return matches < capacity
    return False



def checkHotelAvailability(hotel_id, start_date, end_date, bookings):
    hotel_url = f'http://hotels-service:5000/api/v1/hotel/{hotel_id}'
    hotel_id = int(hotel_id)

    # Obtener datos del hotel
    response = requests.get(hotel_url)
    hotel_data = response.json()
    hotel_capacity = hotel_data['capacity'] 

    

    start_date_unix = datetime.fromisoformat(start_date).timestamp() 
    end_date_unix = datetime.fromisoformat(end_date).timestamp() 
    current_bookings = 0

    for booking in bookings:

        booking_hotel= int(booking["hotel_id"]) if booking["hotel_id"] is not None else 0

        logging.info(f"BOOKING HID: {booking_hotel}, TARGET ID : {hotel_id}, sdu {start_date_unix}, edu:{end_date_unix}, bookings: {current_bookings}")
        
        if booking_hotel == hotel_id:
            logging.info("Match in hotel bookings")
            booking_start_date_obj = datetime.strptime(booking['start_date'], "%a, %d %b %Y %H:%M:%S %Z")
            # Convertir el objeto datetime a un timestamp Unix
            # time.mktime() requiere un objeto struct_time, que se puede obtener usando date_obj.timetuple()
            booking_start_unix = time.mktime(booking_start_date_obj.timetuple())
            booking_end_date_obj = datetime.strptime(booking['end_date'], "%a, %d %b %Y %H:%M:%S %Z")
            # Convertir el objeto datetime a un timestamp Unix
            # time.mktime() requiere un objeto struct_time, que se puede obtener usando date_obj.timetuple()
            booking_end_unix = time.mktime(booking_end_date_obj.timetuple())
            logging.info(f"sdu {start_date_unix}, edu:{end_date_unix}, bsdu: { booking_start_unix }, bedu: {booking_end_unix}")
        
            if booking_start_unix >= start_date_unix and booking_start_unix <= end_date_unix:
                current_bookings += 1
            if booking_end_unix >= start_date_unix and booking_end_unix <= end_date_unix:
                current_bookings += 1

 
    return current_bookings < hotel_capacity

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)






