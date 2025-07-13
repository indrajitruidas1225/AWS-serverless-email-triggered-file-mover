import boto3
import os
import time
import json

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    ses = boto3.client('ses')

    to_email = os.environ['TO_EMAIL'] #From environment variable
    from_email = os.environ['FROM_EMAIL']

    # Parse uploaded file info
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    file_url = f"https://{bucket}.s3.amazonaws.com/{key}"

    # Send email
    response = ses.send_email(
        Source=from_email,
        Destination={'ToAddresses': [to_email]},
        Message={
            'Subject': {'Data': 'New file uploaded'},
            'Body': {
                'Text': {
                    'Data': f"A new file has been uploaded: {file_url}\n\nReply with 'move' to move it within 2 minutes."
                }
            }
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Email sent ')
    }
