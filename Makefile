S3_BUCKET = patient-intake
LOCALSTACK_ENDPOINT = http://localhost:4566

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

start: build up create-bucket wait-for-localstack 
	@echo "System is ready."

fast_start: up create-bucket wait-for-localstack 
	@echo "System is ready."

clean_uploads:
	rm -rf uploads/*

# -------------------------------
# Wait for LocalStack to be ready
# -------------------------------
wait-for-localstack:
	@echo "Waiting for LocalStack to start..."
	@until curl -s $(LOCALSTACK_ENDPOINT)/_localstack/health?reload | grep "\"s3\": \"running\"" > /dev/null; do \
		echo "LocalStack not ready yet..."; \
		sleep 2; \
	done
	@echo "LocalStack S3 service is ready."

# -------------------------------
# Create S3 bucket
# -------------------------------
create-bucket:
	@echo "Creating S3 bucket: $(S3_BUCKET)"
	@aws --endpoint-url=$(LOCALSTACK_ENDPOINT) s3 mb s3://$(S3_BUCKET) || true
