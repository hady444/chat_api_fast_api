# first run
docker build -t test .

# then run
docker compose up

for testing all api's are working proberly there is test file in app/tests/test_api.py
run:
python test_api.py
