# RabbitMQ-pub-sub
### Description
Simple application that produces and consumes data, using RabbitMQ as a message broker.
**sender.py**: An application that periodically sends data for calculation to RabbitMQ using routing.
**consumer.py**: An application that processes data, applying various operations and sleep, and writes the result to a log. If the operation failed, rejects the message to DLQ.
Data logs to "event.log" file.
_______________
### Setup
Enter `docker-compose build ` in project root folder to build the containers.
Enter `docker-compose up` in project root folder to run the containters.
In order to inspect DQL and DQX navigate to `localhost:15672/` and use login:rmuser, password:rmpassword. Go to queues link. DLQ is 'deadque' queue.
