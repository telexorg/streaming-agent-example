import os
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
import a2a.types as a2a_types
from a2a_parts.agent_card import get_card
from a2a_parts.handle_messaging import handle_message_stream

load_dotenv()
app = FastAPI()

@app.post("/")
def handle_rpc(request_data: dict):
    try:
        rpc_request = a2a_types.A2ARequest.validate_python(request_data)

        if isinstance(rpc_request, a2a_types.StreamMessageRequest):
            print("Recieved message/stream")
            return  handle_message_stream(params=rpc_request.params)
        elif isinstance(rpc_request, a2a_types.GetTaskRequest):
            print("Received tasks/get")
        else:
            raise HTTPException(status_code=400, detail="Method not supported")
            
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=400, detail="Could not handle task")


@app.get("/.well-known/agent.json")
def agent_card(request: Request):
    external_base = request.headers.get("x-external-base-url", "")
    base_url = str(request.base_url).rstrip("/") + external_base

    return get_card(base_url)

if __name__ == "__main__":
    import uvicorn

    PORT = int(os.getenv("PORT", 7001))

    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)
