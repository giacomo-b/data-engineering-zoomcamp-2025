# Module 1 Homework: Docker & SQL

## Question 1. Understanding docker first run 

Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`.

What's the version of `pip` in the image?

- [x] 24.3.1
- [ ] 24.2.1
- [ ] 23.3.1
- [ ] 23.2.1

### Solution
```bash
# Run the container
docker run -it --entrypoint=bash python:3.12.8

# From inside the container
pip --version

# Output
pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that **pgadmin** should use to connect to the postgres database? If there are more than one answers, select only one of them.

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin  

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

- [ ] postgres:5433
- [ ] localhost:5432
- [ ] db:5433
- [ ] postgres:5432
- [x] db:5432

### Solution

The `hostname` and `port` that **pgadmin** should use to connect to the postgres database are `db` (service name) and `5432` (internal port of the postgres container) respectively.

##  Prepare Postgres

Run Postgres and load data as shown in the videos
We'll use the green taxi trips from October 2019:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
```

You will also need the dataset with zones:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

Download this data and put it into Postgres.

You can use the code from the course. It's up to you whether
you want to use Jupyter or a python script.

### Preparation

```bash
# Launch the Postgres and pgAdmin containers
docker compose up -d

# Ingest the data (done locally with a Python script)
python upload_homework_data.py
```

## Question 3. Trip Segmentation Count

During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, **respectively**, happened:
1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles 

Answers:

- [ ] 104,802;  197,670;  110,612;  27,831;  35,281
- [x] 104,802;  198,924;  109,603;  27,678;  35,189
- [ ] 104,793;  201,407;  110,612;  27,831;  35,281
- [ ] 104,793;  202,661;  109,603;  27,678;  35,189
- [ ] 104,838;  199,013;  109,645;  27,688;  35,202

### Solution

Query:
```sql
SELECT 
    CASE 
        WHEN trip_distance IS NULL THEN 'unknown distance'
        WHEN trip_distance <= 1 THEN '0-1 miles'
        WHEN trip_distance > 1 AND trip_distance <= 3 THEN '1-3 miles'
        WHEN trip_distance > 3 AND trip_distance <= 7 THEN '3-7 miles'
        WHEN trip_distance > 7 AND trip_distance <= 10 THEN '7-10 miles'
        ELSE 'over 10 miles'
    END AS distance,
    COUNT(*) as trips
FROM green_taxi_data
WHERE lpep_dropoff_datetime >= '2019-10-01' 
    AND lpep_dropoff_datetime < '2019-11-01'
    AND lpep_pickup_datetime IS NOT NULL
    AND lpep_dropoff_datetime IS NOT NULL
GROUP BY 
    CASE 
        WHEN trip_distance IS NULL THEN 'unknown distance'
        WHEN trip_distance <= 1 THEN '0-1 miles'
        WHEN trip_distance > 1 AND trip_distance <= 3 THEN '1-3 miles'
        WHEN trip_distance > 3 AND trip_distance <= 7 THEN '3-7 miles'
        WHEN trip_distance > 7 AND trip_distance <= 10 THEN '7-10 miles'
        ELSE 'over 10 miles'
    END
ORDER BY 
    distance;
```

Output:

| distance      | trips  |
|---------------|--------|
| 0-1 miles     | 104802 |
| 1-3 miles     | 198924 |
| 3-7 miles     | 109603 |
| 7-10 miles    | 27678  |
| over 10 miles | 35189  |

## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance?
Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance. 

- [ ] 2019-10-11
- [ ] 2019-10-24
- [ ] 2019-10-26
- [x] 2019-10-31

### Solution

Query:
```sql
SELECT 
    DATE(lpep_pickup_datetime) as pickup_date,
    MAX(trip_distance) as longest_trip
FROM green_taxi_data
WHERE lpep_pickup_datetime >= '2019-10-01' 
    AND lpep_pickup_datetime < '2019-11-01'
    AND lpep_pickup_datetime IS NOT NULL
GROUP BY DATE(lpep_pickup_datetime)
ORDER BY longest_trip DESC
LIMIT 1;
```

Output:

| pickup_date | longest_trip |
|-------------|--------------|
| 2019-10-31  | 515.89       |


## Question 5. Three biggest pickup zones

Which were the top pickup locations with over 13,000 in
`total_amount` (across all trips) for 2019-10-18?

Consider only `lpep_pickup_datetime` when filtering by date.
 
- [x] East Harlem North, East Harlem South, Morningside Heights
- [ ] East Harlem North, Morningside Heights
- [ ] Morningside Heights, Astoria Park, East Harlem South
- [ ] Bedford, East Harlem North, Astoria Park

### Solution

Query:
```sql
SELECT 
	"Zone" as pickup_location,
    ROUND(CAST(SUM(total_amount) AS numeric), 2) AS total_amount
FROM green_taxi_data
	JOIN zones ON "PULocationID" = "LocationID"
WHERE DATE(lpep_pickup_datetime) = '2019-10-18'
GROUP BY "Zone"
HAVING SUM(total_amount) > 13000
ORDER BY total_amount DESC;
```

Output:

| pickup_location       | total_amount |
|-----------------------|--------------|
| East Harlem North     | 18686.68     |
| East Harlem South     | 16797.26     |
| Morningside Heights   | 13029.79     |


## Question 6. Largest tip

For the passengers picked up in October 2019 in the zone
name "East Harlem North" which was the drop off zone that had
the largest tip?

Note: it's `tip` , not `trip`

We need the name of the zone, not the ID.

- [ ] Yorkville West
- [x] JFK Airport
- [ ] East Harlem North
- [ ] East Harlem South

### Solution

Query:
```sql
SELECT 
	doz."Zone" AS dropoff_zone,
	tip_amount
FROM green_taxi_data t
	JOIN zones puz ON t."PULocationID" = puz."LocationID"
	JOIN zones doz ON t."DOLocationID" = doz."LocationID"
WHERE lpep_pickup_datetime >= '2019-10-01' 
    AND lpep_pickup_datetime < '2019-11-01'
    AND lpep_pickup_datetime IS NOT NULL
	AND puz."Zone" = 'East Harlem North'
    AND tip_amount IS NOT NULL
ORDER BY tip_amount DESC
LIMIT 1;
```

Output:

| dropoff_zone | tip_amount |
|--------------|------------|
| JFK Airport  | 87.3       |

## Terraform

In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform. 
Copy the files from the course repo
[here](../../../01-docker-terraform/1_terraform_gcp/terraform) to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.


## Question 7. Terraform Workflow

Which of the following sequences, **respectively**, describes the workflow for: 
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform

Answers:
- [ ] terraform import, terraform apply -y, terraform destroy
- [ ] teraform init, terraform plan -auto-apply, terraform rm
- [ ] terraform init, terraform run -auto-approve, terraform destroy
- [x] terraform init, terraform apply -auto-approve, terraform destroy
- [ ] terraform import, terraform apply -y, terraform rm


## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2025/homework/hw1