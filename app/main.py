from supervisor_agent.agent import supervisor

from pretty_print import pretty_print_messages
from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket(path="/ws")
async def audioCallWithAgent(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            user_input = await websocket.receive_text()
            async for chunk in supervisor.astream({"messages": [{"role": "user", "content": user_input}]}):
                pass

    except WebSocketDisconnect:
        print(f"Client disconnected. Session ID: {session_id}")

    except Exception as e:
        print(f"Connection error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # print(supervisor.get_graph().draw_mermaid())
    while True:
        user_input = input("You: ")
        for chunk in supervisor.stream({"messages": [{"role": "user", "content": user_input}]}):
            # pretty_print_messages(chunk)
            if (ai_chunk := chunk.get('supervisor')):
                if (ai_msg := ai_chunk['messages'][-1]) and isinstance(ai_msg, AIMessage):
                    print(ai_msg.content)