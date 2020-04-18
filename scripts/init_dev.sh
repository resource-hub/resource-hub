#! /bin/bash

bash -c 'sleep 7 && firefox -new-tab -url http://localhost:8000 -new-tab -url http://localhost:8080 -new-tab -url http://localhost:5050' &
sudo docker-compose up