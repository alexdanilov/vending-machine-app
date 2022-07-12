# Summary
This is a testing application written on Django and implements some endpoints to emulate vending machine.

# Installation 
## via poetry
`poetry install`

## via virtualenv
`virtualenv --python=python3 venv; source venv/bin/activate;pip install -r requirements.txt`

## via Docker

1. Build an image `docker build -t vending-machine .`
2. Run docker container `docker run -t -p 8000:8000 vending-machine`

# Running tests
## via poetry
`poetry run python manage.py test`

## via virtualenv
`python manage.py test`


## via Docker
1. Build an image `docker build -t vending-machine .`
2. Run docker command `docker run -t vending-machine python manage.py test`


# Documentation
You can run application and open link `http://localhost:8000/swagger/` for getting access to Swagger UI.
