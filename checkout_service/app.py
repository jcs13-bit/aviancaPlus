from flask import Flask, request, jsonify
import logging
import requests 
from datetime import datetime
from flask_cors import CORS, cross_origin

# Configuración de logging
logging.basicConfig(filename='checkout.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/api/v1/checkout', methods=['POST'])
@cross_origin()
def createCheckOut():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'No JSON data found in request'}), 400
    flight_start_id = data['flight_start_id'] if 'flight_start_id' in data else ""
    flight_end_id = data['flight_end_id'] if 'flight_end_id' in data else ""
    hotel_id = data['hotel_id'] if 'hotel_id' in data else ""
    start_date = data['start_date'] if 'start_date' in data else ""
    end_date = data['end_date'] if 'end_date' in data else ""
    
    queryString=""

    if flight_start_id or flight_end_id or (hotel_id and start_date and end_date):

        if flight_start_id:
            queryString += f"flight_start_id={flight_start_id}&"
        if flight_end_id:
            queryString += f"flight_end_id={flight_end_id}&"
        if hotel_id:
            queryString += f"hotel_id={hotel_id}&"
        if start_date:
            queryString += f"start_date={start_date}&"
        if end_date:
            queryString += f"end_date={end_date}&"

        
        
        # Elimina el último '&' si existe
        if queryString.endswith("&"):
            queryString = queryString[:-1]

        # Construye la URL completa
        url = f"http://availability-service:5000/api/v1/availability?{queryString}"


        # Realiza la solicitud GET
        availabilityRequest = requests.get(url)
        availabilityData = availabilityRequest.json()
        
        user_id = data['user_id']
        payments = data.get('payments', [])
        linked_bookings = data.get('linked_bookings', [])
       

        bookingRequestBody = {
            "user_id": user_id,
            "payments": payments,
            "linked_bookings": linked_bookings
        }
        if flight_start_id:
            isFlightStartAvailable = availabilityData["isFlightStartAvailable"]
            if not isFlightStartAvailable:
                return jsonify({"Error": "flight start is not available"}), 400
            bookingRequestBody["flight_start_id"] = flight_start_id        
        if flight_end_id:
            isFlightEndAvailable = availabilityData["isFlightEndAvailable"]
            if not isFlightEndAvailable:
                return jsonify({"Error": "flight end is not available"}), 400
            bookingRequestBody["flight_end_id"] = flight_end_id   
        if hotel_id:
            isHotelAvailable = availabilityData["isHotelAvailable"]
            if not isHotelAvailable:
                return jsonify({"Error": "hotel is not available"}), 400
            bookingRequestBody["hotel_id"] = hotel_id   
            bookingRequestBody["start_date"] = start_date
            bookingRequestBody["end_date"] = end_date


        logging.info(f"Booking details to send: {bookingRequestBody}")

            # Enviar la solicitud POST para crear la reserva
        try:
            booking_response = requests.post("http://bookings-service:5000/api/v1/bookings", json=bookingRequestBody)
            booking_response.raise_for_status()  # Lanzar una excepción si ocurre un error
                        # Registrar la respuesta del servicio de reservas
            logging.info(f"Booking service response status: {booking_response.status_code}")
            logging.info(f"Booking service response body: {booking_response.text}")
    

            return jsonify(booking_response.json()), 200
        except requests.RequestException as e:
            logging.error(f"Error in booking request: {e}")
            return jsonify({'error': 'Failed to create booking'}), 500
            


    return jsonify({"Error": "bad request"}), 400

  
    '''

    cuando hacen el checkout:

    

    1.Revisar disponibilidad
    2.crear pago(parametro amount en el request para poder mandarlo a payments)

    3.crear el booking y devolver la reserva

    
    

    cuando se edita:

    1.Revisar disponibilidad de nuevos ids y nuevas fechas

    2.crear un nuevo pago

    3.devolver el booking editado

    
    

    cuando se elimina:
    1.eliminar primero las bookings relacionadas

    2.eliminar las bookings padre
    3.eliminar la booking actual

    logging.info(f"Request availability-service:{url}")  

    



    logging.info(f"Request:{url}")
    return jsonify(url) 

    
    '''

@app.route('/api/v1/checkout/<int:id>', methods=['PUT'])
@cross_origin()
def editCheckOut(id):
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'No JSON data found in request'}), 400
    flight_start_id = data['flight_start_id'] if 'flight_start_id' in data else ""
    flight_end_id = data['flight_end_id'] if 'flight_end_id' in data else ""
    hotel_id = data['hotel_id'] if 'hotel_id' in data else ""
    start_date = data['start_date'] if 'start_date' in data else ""
    end_date = data['end_date'] if 'end_date' in data else ""
    
    queryString=""

    if flight_start_id or flight_end_id or (hotel_id and start_date and end_date):

        if flight_start_id:
            queryString += f"flight_start_id={flight_start_id}&"
        if flight_end_id:
            queryString += f"flight_end_id={flight_end_id}&"
        if hotel_id:
            queryString += f"hotel_id={hotel_id}&"
        if start_date:
            queryString += f"start_date={start_date}&"
        if end_date:
            queryString += f"end_date={end_date}&"

        
        
        # Elimina el último '&' si existe
        if queryString.endswith("&"):
            queryString = queryString[:-1]

        # Construye la URL completa
        url = f"http://availability-service:5000/api/v1/availability?{queryString}"


        # Realiza la solicitud GET
        availabilityRequest = requests.get(url)
        availabilityData = availabilityRequest.json()
        
        user_id = data['user_id']
        payments = data.get('payments', [])
        linked_bookings = data.get('linked_bookings', [])
       

        bookingRequestBody = {
            "user_id": user_id,
            "payments": payments,
            "linked_bookings": linked_bookings
        }
        if flight_start_id:
            isFlightStartAvailable = availabilityData["isFlightStartAvailable"]
            if not isFlightStartAvailable:
                return jsonify({"Error": "flight start is not available"}), 400
            bookingRequestBody["flight_start_id"] = flight_start_id        
        if flight_end_id:
            isFlightEndAvailable = availabilityData["isFlightEndAvailable"]
            if not isFlightEndAvailable:
                return jsonify({"Error": "flight end is not available"}), 400
            bookingRequestBody["flight_end_id"] = flight_end_id   
        if hotel_id:
            isHotelAvailable = availabilityData["isHotelAvailable"]
            if not isHotelAvailable:
                return jsonify({"Error": "hotel is not available"}), 400
            bookingRequestBody["hotel_id"] = hotel_id   
            bookingRequestBody["start_date"] = start_date
            bookingRequestBody["end_date"] = end_date


        logging.info(f"Booking details to send: {bookingRequestBody}")

            # Enviar la solicitud POST para crear la reserva
        try:
            booking_response = requests.put(F"http://bookings-service:5000/api/v1/bookings/{id}", json=bookingRequestBody)
            booking_response.raise_for_status()  # Lanzar una excepción si ocurre un error
                        # Registrar la respuesta del servicio de reservas
            logging.info(f"Booking service response status: {booking_response.status_code}")
            logging.info(f"Booking service response body: {booking_response.text}")
    

            return jsonify(booking_response.json()), 200
        except requests.RequestException as e:
            logging.error(f"Error in booking request: {e}")
            return jsonify({'error': 'Failed to edit booking'}), 500
            


    return jsonify({"Error": "bad request"}), 400

  
    '''

    cuando hacen el checkout:

    

    1.Revisar disponibilidad
    2.crear pago(parametro amount en el request para poder mandarlo a payments)

    3.crear el booking y devolver la reserva

    
    

    cuando se edita:

    1.Revisar disponibilidad de nuevos ids y nuevas fechas

    2.crear un nuevo pago

    3.devolver el booking editado

    
    

    cuando se elimina:
    1.eliminar primero las bookings relacionadas

    2.eliminar las bookings padre
    3.eliminar la booking actual

    logging.info(f"Request availability-service:{url}")  

    



    logging.info(f"Request:{url}")
    return jsonify(url) 

    
    '''

    
    



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)






