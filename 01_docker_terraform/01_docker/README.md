# Docker Quick Reference Guide

## Basic Container Operations

### Run Containers
```bash
# Run a test container
docker run hello-world

# Run Ubuntu with interactive terminal
docker run -it ubuntu bash

# Run Python container
docker run -it python:3.9

# Run Python with custom entrypoint
docker run -it --entrypoint=bash python:3.9
```

### Container Management
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop <container_id>

# Remove a container
docker rm <container_id>
```

## Working with Images

### Basic Image Operations
```bash
# List images
docker images

# Remove an image
docker rmi <image_name>:<tag>

# Pull an image without running
docker pull <image_name>:<tag>
```

### Build Custom Images
Basic Python image with pandas:
```dockerfile
FROM python:3.9
RUN pip install pandas
```

Build and run:
```bash
# Build image
docker build -t myapp:pandas .

# Run container
docker run -it myapp:pandas
```

### Working with Files
Dockerfile with file copying:
```dockerfile
FROM python:3.9

RUN pip install pandas

WORKDIR /app
COPY pipeline.py .

ENTRYPOINT ["python", "pipeline.py"]
```

## Advanced Usage

### Volumes and Environment Variables
Run PostgreSQL with volume mounting:
```bash
docker run -it \
    -e POSTGRES_USER=root \
    -e POSTGRES_PASSWORD=root \
    -e POSTGRES_DB=ny_taxi \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5433:5432 \
    postgres:13
```

Common flags:
- `-e`: Set environment variables
- `-v`: Mount volumes
- `-p`: Port mapping (host:container)
- `-d`: Run in detached mode
- `--name`: Assign container name

### Database Operations

#### PostgreSQL CLI
```bash
# Connect to database
psql -h localhost -p 5433 -U root -d ny_taxi

# Common commands:
\dt                    # List tables
\d table_name          # Describe table
\q                     # Quit
```

#### Python Database Integration
```python
# Connect to PostgreSQL
from sqlalchemy import create_engine
engine = create_engine('postgresql://root:root@localhost:5433/ny_taxi')

# Create table from DataFrame
df.head(0).to_sql('table_name', con=engine, if_exists='replace')

# Load data in chunks
while True:
    try:
        df = next(df_iter)
        df.to_sql('table_name', con=engine, if_exists='append')
    except StopIteration:
        break
```

#### pgAdmin

Run pgAdmin with custom credentials:
```bash
docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p 8080:80 \
    dpage/pgadmin4
```

This will run pgAdmin on `localhost:8080` with the specified credentials, but won't be able to connect to the PostgreSQL container (since it's running on a different network).

### Creating a Network

Create a custom network and connect containers to it:
```bash
# Create network
docker network create pg-network

# Run containers in network
docker run -it --network=pg-network myapp:pandas

# Connect existing container to network
docker network connect pg-network <container_id>
```

In order to run the PostgreSQL and pgAdmin containers on the same network:
```bash
# Run PostgreSQL container
docker run -it \
    -e POSTGRES_USER=root \
    -e POSTGRES_PASSWORD=root \
    -e POSTGRES_DB=ny_taxi \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5433:5432 \
    --network=pg-network \
    --name pg-database \
    postgres:13

# Run pgAdmin container
docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p 8080:80 \
    --network=pg-network \
    --name pg-admin \
    dpage/pgadmin4
```

Now from pgAdmin (localhost:8080), you can connect to the PostgreSQL container using the network name (`pg-database`) by following these steps:
1. Add a new server
2. Hostname/address: `pg-database`
3. Port: `5432`
4. Username: `root`
5. Password: `root`

### Running the data ingestion pipeline

To run the Python data ingestion pipeline:
```bash
URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet"
python3.12 ingest-data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5433 \
    --db=ny_data \
    --table_name=yellow_taxi_data \
    --url=${URL}
```

```bash
URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet"
docker run -it \
    --network=pg-network \
    taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pg-database \
    --port=5432 \
    --db=ny_taxi \
    --table_name=yellow_taxi_data \
    --url=${URL}
```

### Docker Compose

A Docker Compose file to run the PostgreSQL and pgAdmin containers:
```yaml
services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
      - "5433:5432"
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    ports:
      - "8080:80"
```

To run the containers:
```bash
docker-compose up
```

To stop the containers:
```bash
docker-compose down
```

To run it in detached mode:
```bash
docker-compose up -d
```

To run the data ingestion pipeline:
```bash
URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet"
docker run -it \
    --network=01_docker_default \
    taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pgdatabase \
    --port=5432 \
    --db=ny_taxi \
    --table_name=yellow_taxi_data \
    --url=${URL}
```

## Best Practices

1. Use specific tags instead of `latest`
2. Include `.dockerignore` for unused files
3. Use multi-stage builds for smaller images
4. Always clean up unused containers/images
5. Store secrets in environment variables

## Common Issues

- **Permission denied**: Prefix commands with `sudo` or add user to docker group
- **Port already in use**: Change host port mapping
- **No space left**: Run `docker system prune` to clean up