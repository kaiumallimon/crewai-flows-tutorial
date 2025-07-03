import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from configs.llm_config import generative_model
from crews.central_flow import CentralizedFlow

app = FastAPI()


@app.get("/", name="Root")
async def root():
    return {"message": "Hello, World!"}


@app.get("/health", name="Health")
async def health():
    return {"status": "ok"}


flow = CentralizedFlow()



@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")

    try:
        while True:
            user_input = await websocket.receive_text()
            print(f"Received: {user_input}")

            try:
                # Create a new flow instance and run it
                flow = CentralizedFlow()
                
                # Use kickoff() method for CrewAI Flows
                # In your WebSocket handler
                flow.state.latest_question = user_input
                flow_response = await flow.kickoff_async()


                if flow_response is None:
                    await websocket.send_text(
                        json.dumps({
                            "type": "error",
                            "content": None,
                            "message": "No course matched the query.",
                        })
                    )
                    continue
                else:
                    await websocket.send_text(
                        json.dumps({
                            "type": "response",
                            "content": str(flow_response),  # Convert to string
                            "message": "Course classification successful.",
                        })
                    )
            except Exception as e:
                print(f"Flow execution error: {e}")
                await websocket.send_text(
                    json.dumps({
                        "type": "error",
                        "content": None,
                        "message": f"Model error: {str(e)}",
                    })
                )
                break

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await websocket.close()
        print("WebSocket connection cleanup")