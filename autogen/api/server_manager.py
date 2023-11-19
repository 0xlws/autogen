from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket
from .chat_session import ChatSession, send_to_client, receive_from_client
from .chat_manager import ChatManager
import uvicorn
import asyncio

chat_manager = ChatManager()

class ServerManager:
    def __init__(self, assistant=None, user_proxy=None, chat_manager=None):
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            # allow_origins=["*"],  # Allows all origins
            allow_origins=["http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],  # Allows all methods
            allow_headers=["*"],  # Allows all headers
        )
        self.app.websocket("/ws/{chat_id}")(self.websocket_endpoint)
        if assistant is None:
            raise Exception("AssistantAgent missing")
        if user_proxy is None:
            raise Exception("UserProxyAPIAgent missing")
        if chat_manager is None:
            raise Exception("ChatManager missing")
        self.assistant = assistant
        self.user_proxy = user_proxy
        self.chat_manager = chat_manager
        

    async def websocket_endpoint(self, websocket: WebSocket, chat_id: str):
        chat_session = None
        try:
            chat_session = ChatSession(chat_id=chat_id, websocket=websocket, assistant=self.assistant, user_proxy=self.user_proxy)
            await self.chat_manager.add_connection(chat_session)
            data = await chat_session.websocket.receive_text()
            futures = asyncio.gather(send_to_client(chat_session), receive_from_client(chat_session))
            await chat_session.begin_conversation(data)
        except Exception as e:
            print("ERROR", str(e))
        finally:
            if chat_session:
                try:
                    await self.chat_manager.remove_connection(chat_session)
                except:
                    pass

    def start_server(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8042)


