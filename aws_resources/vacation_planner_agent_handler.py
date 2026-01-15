import json
import boto3
import uuid

def lambda_handler(event, context):
    client = boto3.client('bedrock-agentcore', region_name='ap-south-1')

    user_input = event.get("prompt")
    payload = json.dumps({"topic": user_input})
    session_id = f"lambda_sessio_{str(uuid.uuid4()).replace("-", "")}"

    print(f"Invoking AgentCore with payload: {payload} and session id: {session_id}")

    response = client.invoke_agent_runtime(
        agentRuntimeArn='arn:aws:bedrock-agentcore:ap-south-1:117915829123:runtime/vacation_planner_agent-6f30Yt2zJw',
        runtimeSessionId=session_id,
        payload=payload,
        qualifier="DEFAULT"
    )

    response_body = response["response"].read().decode("utf-8")
    print(f"Agent Response: {response_body}")
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
                    'result': response_body,
                    'session_id': session_id
                })
    }
