import base64
import json
import smtplib
import email
import ssl
import os

def lambda_handler(event, context):
    # config
    smtp_username = os.environ['SMTP_USERNAME']
    smtp_password = os.environ['SMTP_PASSWORD']
    aws_region = os.environ['AWS_REGION']
    from_address = os.environ['FROM_ADDRESS']
    spam_from_address = os.environ['SPAM_FROM_ADDRESS']
    forward_address = os.environ['FORWARDED_ADDRESS']

    # Connect to SES SMTP endpoint
    with smtplib.SMTP_SSL(f"email-smtp.{region}.amazonaws.com", timeout=5) as smtp:
        smtp.login(smtp_username, smtp_password)
    
        for record in event['Records']:
            # Get SES message
            ses_message = json.loads(record['Sns']['Message'])

            # Log
            common_headers = ses_message['mail']['commonHeaders']
            receipt = ses_message['receipt']
            print('forwarding email:', {'common_headers': common_headers, 'receipt': receipt})

            # Parse email
            raw_message = base64.b64decode(ses_message['content'])
            message = email.message_from_bytes(raw_message)

            # Preserve From header
            message['original-from'] = message['from']
            if 'reply-to' not in message:
                message['reply-to'] = message['from']
            
            # Delete headers that require verified identities https://docs.aws.amazon.com/ses/latest/dg/verify-addresses-and-domains.html
            del message['from']
            del message['source']
            del message['sender']
            del message['return-path']
            
            # Rewrite From header
            if (
                receipt.get('spamVerdict', {}).get('status') == 'FAIL' or
                receipt.get('virusVerdict', {}).get('status') == 'FAIL'
            ):
                message['from'] = spam_from_address
            else:
                message['from'] = from_address

            # Send email
            smtp.send_message(message, from_addr=from_address, to_addrs=[forward_address])

    return {
        'statusCode': 200,
        'body': json.dumps('Email forwarded successfully')
    }
