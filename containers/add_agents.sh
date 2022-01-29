#!/bin/bash

docker exec -it ejabberd bin/ejabberdctl register client localhost client_password
docker exec -it ejabberd bin/ejabberdctl register mathematician localhost mathematician_password
docker exec -it ejabberd bin/ejabberdctl register manager localhost manager_password
docker exec -it ejabberd bin/ejabberdctl register dummy localhost dummy_password

# Drivers
docker exec -it ejabberd bin/ejabberdctl register 1_driver localhost driver_password
docker exec -it ejabberd bin/ejabberdctl register 2_driver localhost driver_password
docker exec -it ejabberd bin/ejabberdctl register 3_driver localhost driver_password