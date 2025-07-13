import boto3
import email
import os
import re

s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')

INBOX_BUCKET = os.environ['INBOX_BUCKET']  #From environment variable
UPLOAD_BUCKET = os.environ['UPLOAD_BUCKET']
DEST_BUCKET = os.environ['DEST_BUCKET']

def extract_key_from_url(body):
    # Regex to extract key from S3 URL
    match = re.search(r'https://[^/]+\.s3\.amazonaws\.com/([^\s]+)', body)
    if match:
        return match.group(1)
    return None

def lambda_handler(event, context):
    print("Received event:", event)

    for record in event.get('Records', []):
        key = record['s3']['object']['key']
        print(f"Object from: {INBOX_BUCKET}/{key}")
        
        obj = s3.get_object(Bucket=INBOX_BUCKET, Key=key)
        raw_email = obj['Body'].read().decode('utf-8')
        
        msg = email.message_from_string(raw_email)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8')
        
        print("Email body:\n", body)
        print("Email subject:", msg.get("Subject", ""))

        if 'move' in body.lower():
            source_key = extract_key_from_url(body)
            if not source_key:
                print("No valid source key found in email body. Aborting move.")
                return

            dest_key = source_key.replace("uploads/", "moved/")

            # Copy and delete
            s3_resource.Object(DEST_BUCKET, dest_key).copy_from(
                CopySource=f"{UPLOAD_BUCKET}/{source_key}"
            )
            s3_resource.Object(UPLOAD_BUCKET, source_key).delete()
            print(f"Moved {source_key} to {DEST_BUCKET}/{dest_key}")
        else:
            print("No action taken. 'move' not found in body.")
