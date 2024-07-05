    CREATE TABLE bookings (id SERIAL PRIMARY KEY,user_id INT NOT NULL,hotel_id INT,vuelo_id INT,flight_start_id INT,flight_end_id INT,start_date TIMESTAMP,end_date TIMESTAMP,status VARCHAR(20) NOT NULL,linked_bookings JSON,payments JSON);

kubectl exec --stdin --tty bookings-service-deployment-78c69c698f-ktb2w -- /bin/bash

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
