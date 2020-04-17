#! /bin/bash

if [ -z "$1" ]
then
    echo "module parameter not set";
    exit 1;
fi

sudo docker-compose exec app bash -c "cd src && python manage.py test ${1} --verbosity 2"