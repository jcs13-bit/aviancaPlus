from flask import Flask, request, jsonify

app = Flask(__name__)

hotels = []

@app.route('/hotels', methods=['GET'])
def get_hotels():
    return jsonify(hotels)

@app.route('/hotels', methods=['POST'])
def add_hotel():
    new_hotel = request.get_json()
    hotels.append(new_hotel)
    return jsonify(new_hotel), 201

@app.route('/hotels/<int:hotel_id>', methods=['DELETE'])
def delete_hotel(hotel_id):
    global hotels
    hotels = [hotel for hotel in hotels if hotel['id'] != hotel_id]
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
