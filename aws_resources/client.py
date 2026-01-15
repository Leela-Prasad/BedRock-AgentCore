import requests
import json
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
TOKEN_URL = "https://ap-south-1vx9liixtt.auth.ap-south-1.amazoncognito.com/oauth2/token"

def fetch_access_token(client_id, client_secret, token_url):
  response = requests.post(
    token_url,
    data="grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}".format(client_id=client_id, client_secret=client_secret),
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
  )

  print("Access Token :: ", response.json()['access_token'])
  return response.json()['access_token']

def list_tools(gateway_url, access_token):
  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {access_token}"
  }

  payload = {
      "jsonrpc": "2.0",
    #   "id": "list-tools-request", #Any random string
      "id": "asfdkjhiou",
      "method": "tools/list"
  }

  response = requests.post(gateway_url, headers=headers, json=payload)
  return response.json()

def call_tool(gateway_url, access_token, tool_name, arguments):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    payload = {
        "jsonrpc": "2.0",
        "id": "call-tool-request-239",
        "method": "tools/call",
        "params": {
            "name": tool_name,  #Tool Name
            "arguments": arguments  #Tool args
        }
    }
    
    response = requests.post(gateway_url, headers=headers, json=payload)
    print("Tool Output", response.json())
    return response.json()

# Example usage
gateway_url = "https://travel-agentcore-gateway-3oddtafjiz.gateway.bedrock-agentcore.ap-south-1.amazonaws.com/mcp"
access_token = fetch_access_token(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)
tools = list_tools(gateway_url, access_token)
print(json.dumps(tools, indent=2))

#call the travel packages tool
tool_response = call_tool(gateway_url, access_token, "target-quick-start-fec33b___get_travel_packages", {"city": "Mumbai"})