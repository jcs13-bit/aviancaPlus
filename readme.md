    CREATE TABLE bookings (id SERIAL PRIMARY KEY,user_id INT NOT NULL,hotel_id INT,vuelo_id INT,flight_start_id INT,flight_end_id INT,start_date TIMESTAMP,end_date TIMESTAMP,status VARCHAR(20) NOT NULL,linked_bookings INTEGER[],payments INTEGER[]);

kubectl exec --stdin --tty bookings-service-deployment-78c69c698f-ktb2w -- /bin/bash

todo list
crear endpoint de getBookingsByuserId
revisar como borrar las reservas
crear una función recursiva para borrar las reservas
