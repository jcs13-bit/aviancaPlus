    bookings:
    CREATE TABLE bookings (id SERIAL PRIMARY KEY,user_id INT NOT NULL,hotel_id INT,vuelo_id INT,flight_start_id INT,flight_end_id INT,start_date TIMESTAMP,end_date TIMESTAMP,status VARCHAR(20) NOT NULL,linked_bookings JSON,payments JSON);




    flights:
    CREATE TABLE flights (id SERIAL PRIMARY KEY, start_date TIMESTAMP,end_date TIMESTAMP, start_address  VARCHAR(30),end_address VARCHAR(30), capacity INT NOT NULL);


    hotels:
    CREATE TABLE hotels (id SERIAL PRIMARY KEY, name VARCHAR(30), address VARCHAR(30), capacity INT NOT NULL);


    payments:
    CREATE TABLE payments (id SERIAL PRIMARY KEY,booking_id INT NOT NULL,payment_date TIMESTAMP NOT NULL,amount DECIMAL(10, 2) NOT NULL,payment_method VARCHAR(50) NOT NULL,status VARCHAR(20)NOT NULL,transaction_id VARCHAR(50));

    delete_bookings:
    CREATE TABLE bookings_borradas (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    flight_start_id INT,
    flight_end_id INT,
    hotel_id INT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    payments JSON,
    linked_bookings JSON,
    status VARCHAR(20) NOT NULL,
    deleted_at TIMESTAMP NOT NULL DEFAULT NOW()

);

kubectl exec -it postgres-deployment-7f8c99fdf-rmfvq -- /bin/bash

kubectl exec --stdin --tty bookings-service-deployment-78c69c698f-ktb2w -- /bin/bash

\c nombre_de_la_base_de_datos

Para buildear la imagen:

cd en el folder del servicio
docker build -t nombre_usuario/nombre_container:nombre_tag .

para pushear la imagen:

docker push nombre_usuario/nombre_container:nombre_tag

para borrar un servicio:

kubectl delete service service_name

para borrar un deployment:

kubectl delete deploy deployment_name

para aplicar los CRDs: cd en el folder del servicio, correr:

kubectl apply -f nombre_del_crd.yaml

para correr un servicio con minikube:

minikube service service_name

para ver los pods:

kubectl get pods

para ver los logs de un pod:

kubectl logs pod_id

para entrar en un container en bash:

kubectl exec --stdin --tty id_del_pod -- /bin/bash

para ver el archivo de logs:

cat nombre_del_archivo.log

todo list
crear endpoint de getBookingsByuserId
revisar como borrar las reservas
crear una función recursiva para borrar las reservas

CHECKOUT SERVICE

if flight_start_id or flight_end_id or (hotel_id && start_date && end_date){
//codigo para construir el query string;
const bookingRequestBody = {
user_id,
bookings,
payments
}

    tengo la respuesta del availability svc

    if(flight_start_id){
        //checkear en el availability que si este dispo
        flightStartAvailable = availabilityData["isFlighStartAvailable"]
        if not flightStartAvailable:
            return error 404 not available

        bookingRequest["flight_start_id"] = flight_start_id
    }

    //lo mismo para el hotel
    //y para el vuelo de venida


    //al final, quedamos con el happy path de que lo que buscamos si esta disponible

    bookingRequest =  requests.post.url etc

    retun 201 creado

} else return bad request;
