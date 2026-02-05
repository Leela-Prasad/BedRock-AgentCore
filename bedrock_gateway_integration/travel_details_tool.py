import json

def lambda_handler(event, context):
    print("Event :: ", event)
    response = {
        "city": "Vijayawada",
        "duration": "3 days",
        "travel_plan": """Day1: Temple
        Day2: Hailaand
        Day3: Malls""",
        "vacation_cost": "$10-$50"
    }

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
    