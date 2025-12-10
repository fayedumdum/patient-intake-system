# Patient Intake System (FastAPI + Temporal + LocalStack + PostgreSQL)

## Overview

This project implements a backend microservice system for ingesting structured healthcare data, storing it as CSV in S3, and processing it asynchronously into a PostgreSQL database. The system uses FastAPI, Docker, Makefile, Temporal/Celery, PostgreSQL, and AWS LocalStack.


This project implements a full backend ingestion pipeline using:

- FastAPI
- LocalStack S3
- Temporal
- PostgreSQL
- Docker Compose
- Makefile

## Setup
### 1. Clone the Repository
```bash
git clone <REPO_URL>
cd patient-intake-system
```

### 2. Rename sample.env to .env

### 3. This API's Makefile is intended for Linux. If you are running on a Windows machine, you need to use WSL:
```bash
wsl
```
### 4. Run necessary/needed makefile commands:
```bash
 make <command here>
```
#### Makefile Usage:
| Command                     | Description                                                                                             |
|-----------------------------|---------------------------------------------------------------------------------------------------------|
| `make build`                | Build all Docker containers                                                                             |
| `make up`                   | Start all services without dependency bootstrapping                                                     |
| `make down`                 | Stop all services                                                                                        |
| `make logs`                 | Display logs for all services                                                                           |
| `make start`                | Start the complete system with all dependencies initialized                                            |
| `make create-bucket`        | Creates the S3 bucket to be used by the API                                                            |
| `make wait-for-localstack`  | Waits for LocalStack to be fully ready, specifically ensuring the S3 service is running, before continuing with further setup or service startup |
| `make fast_start`  | Starts system without building images |
| `make clean_uploads`  | Deletes all files  the uploads folder |

## API usage example
### 1. Ingest Patient Data
**Endpoint:** `POST /ingest`  
**Description:** Accepts a JSON array where each object represents a visit record. The Medical Record Number (MRN) uniquely identifies a patient. The Visit Account Number uniquely identifies a visit.
Stores data into local CSV and upload CSV into s3 bucket. Once the file is uploaded to S3, the API must trigger a Temporal workflow that:
1. Fetch the CSV from S3
2. Parse each row
3. Resolve or create patients
4. Update person details
5. Insert visit records linked to the correct patient

**Sample Payload:**
```json
[
  {
    "mrn": "MRN-1001",
    "first_name": "John",
    "last_name": "Doe",
    "birth_date": "1990-02-14",
    "visit_account_number": "VST-9001",
    "visit_date": "2024-11-01",
    "reason": "Annual Checkup"
  }
]
```
**curl Example:**
```bash
curl -X POST http://localhost:8000/ingest \
-H "Content-Type: application/json" \
-d '[{"mrn":"MRN-1001","first_name":"John","last_name":"Doe","birth_date":"1990-02-14","visit_account_number":"VST-9001","visit_date":"2024-11-01","reason":"Annual Checkup"}]'
```

### 2. Get All Patients
**Endpoint:** `GET /patients`  
**Description:** Retrieves all patients with optional pagination and filtering by mrn, first_name, or last_name

**curl Example:**
```bash
curl http://localhost:8000/patients?mrn=MRN-1001
```

### 3. Get Patient by ID
**Endpoint:** `GET /patients/<id>`  
**Description:** Retrieves a single patient, including person and visit information.

**curl Example:**
```bash
curl http://localhost:8000/patients/1
```


## S3 verification steps
After ingesting data via the API, you can verify that the CSV files have been correctly uploaded to LocalStack S3.
Make sure the container is running before executing the commands.

### As a prerequisite, please install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

### 1. List all buckets
```bash
aws --endpoint-url=http://localhost:4566 s3 ls
```
Ensure that the bucket patient-intake exists.

### 2. List files in the bucket
```bash
aws --endpoint-url=http://localhost:4566 s3 ls s3://patient-intake/
```
This will show all CSV files uploaded by the API.

### 3. Download a CSV for inspection
```bash
aws --endpoint-url=http://localhost:4566 s3 cp s3://patient-intake/<csv_filename> .
```
Replace <csv_filename> with the name of the file you want to inspect.
Open the CSV locally to verify the contents match the ingested patient data.


## Workflow execution validation
After ingesting patient data via the API, the Temporal workflow should automatically process the CSV and update the database. 
Follow these steps to validate workflow execution:

We will use the included temporal web UI docker container for this part.

Just go to http://localhost:8080/ to browse and validate executed workflows

## Database verification guide

You can use any database client to connect and validate the database since the container’s database is bound to the host on port 5432. Just enter the required credentials, and you’ll be able to browse the database.

One example is using VSCode’s PostgreSQL extension. Enter the following:

**Host**: localhost

**Username**: postgres (or what you have defined in .env file)

**Password**: postgres (or what you have defined in .env file)

**Port**: 5432

**Database**: patient_intake
