# Resource Hub
Checkout the latest stable build on https://demo.resource-hub.eu/

## Install for development
* Download and install Docker and Docker-Compose for your OS/Distro: https://docs.docker.com/
* create .env file in root directory of project and fill these values:
```
DJANGO_PORT=8000
ALLOWED_HOSTS=*
SECRET_KEY={TODO: YOUR DJANGO SECRET KEY}
DB_NAME=django
DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_NAME=django
DB_USER=django
DB_PW=django
DB_HOST=postgres
DB_PORT=5432
EMAIL_USE_TLS=True
EMAIL_HOST={TODO}
EMAIL_HOST_USER={TODO}
EMAIL_HOST_PASSWORD={TODO}
EMAIL_PORT={TODO}
DEFAULT_FROM_EMAIL=Test Server <server@test.de>
REDIS_LOCATION=redis://redis:6379/0
REDIS_KEY_PREFIX=RD
GITLAB_TOKEN={TODO: OPTIONAL FOR BUG REPORTING}
MAP_API_TOKEN={TODO: MAPBOX API TOKEN}
```
* Run (instructions for unix shell):
```bash
cd /path/to/resource-hub
sudo docker-compose up
# optional: populate db with dummies
sudo docker-compose exec  app python src/manage.py init_demo --full
```