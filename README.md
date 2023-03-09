# healthcare

### Commands
To start the Application:
```commandline
docker compose up --build
```

To run tests:
1. Build and run the containers
```commandline
docker compose up --build
```

2. Run the pytest command in payment-processor container
```commandline
docker-compose exec payment-processor pytest .
```

### URLS
- payment-processor: http://0.0.0.0:8000/docs
- claim-producer: http://0.0.0.0:8080/docs
- kafdrop: http://localhost:9000/

Note: Have used kafdrop for kafka testing