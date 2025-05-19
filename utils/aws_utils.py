import boto3
import uuid

def upload_to_s3(file, bucket):
    s3 = boto3.client('s3', region_name='us-east-1')  # Add region
    key = f"uploads/{uuid.uuid4().hex}_{file.filename}"
    s3.upload_fileobj(file, bucket, key)
    return key

def send_to_sqs(queue_url, message):
    sqs = boto3.client('sqs', region_name='us-east-1')  # Add region
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message
    )
