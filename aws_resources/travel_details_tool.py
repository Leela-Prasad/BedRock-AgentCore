import json
import boto3

def lambda_handler(event, context):
    client = boto3.client("dynamodb")
    city = event["city"]
    response = client.get_item(
        TableName="travel-packages",
        Key={"city": {"S": city}}
    )

    return {
        'statusCode': 200,
        'body': json.dumps(response["Item"])
    }
