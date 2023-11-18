from .chat_session import ChatSession


class ChatManager:
    def __init__(self):
        self.active_connections: list[ChatSession] = []

    async def add_connection(self, chat_session: ChatSession):
        await chat_session.websocket.accept()
        self.active_connections.append(chat_session)

    async def remove_connection(self, chat_session: ChatSession):
        chat_session.client_receive_queue.put_nowait("DO_FINISH")
        print(f"{chat_session.chat_id} disconnected")
        self.active_connections.remove(chat_session)
