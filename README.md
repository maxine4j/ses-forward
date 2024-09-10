# Ses Forwarder

## DNS

Set up MX record for domain pointing to
`inbound-smtp.ap-southeast-2.amazonaws.com.`

## SES Identities

You'll need to verify each of the from and to addresses you want to use, or the entire domain

https://ap-southeast-2.console.aws.amazon.com/ses/home?region=ap-southeast-2#/identities

## Lambda

We need a lambda to recieve the SNS notification and actually forward the email.
Create a new lambda function with the code in `lambda.py`

## Lambda IAM Role

You'll need to update the IAM role that was created for your lambda function and add the following policy:

```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"ses:SendRawEmail"
			],
			"Resource": "*"
		}
	]
}
```

## SES

Set up SES Email receiving rule and trigger an sns topic, then have the topic be consumed by the lambda
