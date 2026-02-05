from langchain_openai import ChatOpenAI
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from dotenv import load_dotenv
from langchain_core.tools import Tool, StructuredTool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
import os
import requests

load_dotenv()

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
# Token URL we need to get from well known endpoint
TOKEN_URL = "https://ap-south-1jol9pvrcu.auth.ap-south-1.amazoncognito.com/oauth2/token"
GATEWAY_URL = "https://gateway-quick-start-df7244-aijajbwxya.gateway.bedrock-agentcore.ap-south-1.amazonaws.com/mcp"
access_token = None


class TravelPackageInput(BaseModel):
    city: str = Field(description="Name of the city")


def get_access_token(client_id, client_secret, token_url):
    response = requests.post(
        token_url,
        data="grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}".format(client_id=client_id, client_secret=client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print("Token Response :: ", response)
    return response.json()["access_token"]


def discover_tools_from_gateway():
    print(":: Get Tools Call ::")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": "list-tools",
        "method": "tools/list"
    }
    
    response = requests.post(GATEWAY_URL, headers=headers, json=payload).json()
    tools = []
    
    for tool in response.get("result", {}).get("tools", []):
        # Here tool is a json node/dict, so we cannot directly pass the entire object
        print("Tool :: ", tool)
        tools.append(StructuredTool(
            name=tool["name"],
            description=tool["description"],
            # func=lambda tool_input, name=tool["name"]: invoke_gateway_tool(tool_name=name, tool_input=tool_input),
            func=lambda name=tool["name"], **kwargs: invoke_gateway_tool(tool_name=name, tool_input=kwargs),
            args_schema=TravelPackageInput
        ))
    
    return tools

        
def invoke_gateway_tool(tool_name, tool_input):
    print(":: Invoke Tool ::")
    print("Tool Name :: ", tool_name)
    print("Tool Args :: ", tool_input)
    print("Tool Args Type :: ", type(tool_input))
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": "call-tool",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": tool_input if isinstance(tool_input, dict) else {"input": tool_input}
        }
    }
    
    response = requests.post(GATEWAY_URL, headers=headers, json=payload).json()
    print("Tool Call Response :: ", response)
    return response.get("result", {}).get("content", [{}])[0].get("text", "Error Calling tool")
    

access_token = get_access_token(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)
print("Access Token :: ", access_token)

app = BedrockAgentCoreApp()

llm = ChatOpenAI(model="gpt-4o-mini")
tools = discover_tools_from_gateway()
agent_executor = create_react_agent(llm, tools=tools)


# @app.invoke()
def handle_request(event):
    prompt = event.get("input")
    input = {"messages": [("user", prompt)]}
    result = agent_executor.invoke(input=input)
    return result


if __name__ == "__main__":
    # app.run()
    # print("Final Response", handle_request({"input": "give me travel packages for chennai"}))
    print("Final Response", handle_request({"input": "Tell me about Elon Musk in 2 points"}))