import os
import boto3

S3_BUCKET = os.getenv("S3_BUCKET")

s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT_URL"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

def upload_to_s3(csv_path: str):
    file_name  = os.path.basename(csv_path)
    s3.upload_file(Filename=csv_path, Bucket=S3_BUCKET, Key=file_name)

    return S3_BUCKET

def download_csv(bucket, key, local_path):
    s3.download_file(bucket, key, local_path)