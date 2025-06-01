import os
import re
import json
import ast
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.responses import JSONResponse
import server as srv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_SERVER_URL = "http://localhost:8000"  # Change if needed

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_api_key_here")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro-preview-05-06")

app = FastAPI()

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserQuery(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str


tools_list = {
    "total_expense": {
        "description": "Total Revenue by country name. (Ex: Total revenue of France)",
        "f" : srv.total_expense,
        "params": {"country": "string"}
    },
    "list_countries": {
        "description": "List available customer countries (Ex: List countries)",
        "f" : srv.list_countries,
        "params": {}
    },
    "find_customers": {
        "description": "Search Customer by name (Ex: Details of customer Wandernde)",
        "f" : srv.find_customers,
        "params": {"name": "string"}
    },
    "find_invoice_by_id": {
        "description": "Finds invoice using the given order ID (Ex: get invoice details for order 10248)",
        "f" : srv.find_invoice_by_id,
        "params": {"id": "integer"}
    },
    "find_product_by_id": {
        "description": "Gets product details by product ID (Ex: Details of product id 51)",
        "f" : srv.find_product_by_id,
        "params": {"id": "integer"}
    },
    "find_order_subtotal": {
        "description": "Returns subtotal for a given order ID(Ex: Order 10248 total amount)",
        "f" : srv.find_order_subtotal,
        "params": {"id": "integer"}
    }
}

def get_tool_list_with_description():
    return {
        tool_name: tool_info["description"]
        for tool_name, tool_info in tools_list.items()
    }

def get_tool_params():
    return {
        tool_name: { "description" : tool_info["description"] , "params" : tool_info["params"] }
        for tool_name, tool_info in tools_list.items()
    }

def dispatch_tool(tool_name: str, args: dict):
    func = tools_list.get(tool_name)["f"]
    if not func:
        return f"Error: Unknown tool '{tool_name}'"
    try:
        return func(**args)
    except Exception as e:
        logger.exception(f"Error executing tool '{tool_name}': {e}")
        return f"Error executing tool '{tool_name}': {e}"

def call_mcp_tool(tool_name, params=None):
    result = dispatch_tool(tool_name, params or {})
    return ChatResponse(response=str(result))

def safely_parse_json(json_str: str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            unescaped_str = json_str.encode('utf-8').decode('unicode_escape')
            return json.loads(unescaped_str)
        except Exception as e:
            logger.exception(f"Failed to parse JSON after unescaping: {e}")
            return []

def extract_product_ids_from_result(response_text):
    try:
        data = json.loads(response_text)
        return data.get("ProductIDs", [])
    except Exception:
        return []

def llm_decide_tools(user_query):
    prompt = f"""
You are an assistant for the Northwind MCP system. You must only use the available tools listed below, exactly as named. Do not make up new tools or change tool names.

Available tools and their descriptions:
{json.dumps(get_tool_params(), indent=2)}

Your task is to decide which tools to call and what parameters to pass, based on the following user query:

\"{user_query}\"

Return your response strictly in JSON format as a list of tool calls. Each item in the list should be of the form:
[
  {{
    "tool": "tool_name",
    "params": {{
      "param1": "value1",
      ...
    }}
  }}
]

Only include valid tools and reasonable parameters based on the query. Do not include explanations or additional text.
"""

    response = model.generate_content(prompt)
    content = response.candidates[0].content
    text = content.parts[0].text if hasattr(content, "parts") else getattr(content, "text", str(content))
    json_block = re.search(r"\[.*\]", text, flags=re.DOTALL)
    if json_block:
        return safely_parse_json(json_block.group(0))
    return []

def llm_process_results(result):
    try:
        raw_response = result.response if isinstance(result, ChatResponse) else str(result)
        try:
            parsed_result = ast.literal_eval(raw_response)
        except Exception:
            try:
                parsed_result = json.loads(raw_response)
            except Exception:
                parsed_result = raw_response

        if isinstance(parsed_result, (list, dict)):
            summary_prompt = f"""
You are a helpful assistant. Convert the following structured data into a concise natural language response.
Just provide the answer only.

Data:
{json.dumps(parsed_result, indent=2)}

Answer:
"""
            summary_resp = model.generate_content(summary_prompt)
            summary_content = summary_resp.candidates[0].content
            summary_text = summary_content.parts[0].text.strip() if hasattr(summary_content, "parts") else getattr(summary_content, "text", str(summary_content)).strip()
            return ChatResponse(response=summary_text)

        return ChatResponse(response=str(parsed_result))

    except Exception as e:
        logger.exception("Error formatting result")
        return ChatResponse(response=f"Error formatting result: {e}")

@app.post("/chat")
def ask_mcp(user_query: UserQuery):
    logger.info(f"Received query: {user_query.query}")

    calls = llm_decide_tools(user_query.query)

    logger.info(f"LLM decided tool calls: {calls}")

    combined_results = []
    for call in calls:
        tool = call.get("tool")
        params = call.get("params", {})
        result = dispatch_tool(tool, params)
        combined_results.append({tool: result})

    final_answer = llm_process_results(ChatResponse(response=json.dumps(combined_results)))
    return final_answer

@app.get("/tools")
def get_available_tools():
    return JSONResponse(content=get_tool_list_with_description())


if __name__ == "__main__":
    import uvicorn
    import sys

    uvicorn.run(app, host="0.0.0.0", port=8000)
