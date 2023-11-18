import asyncio

class ChatSession():
    def __init__(self, chat_id=None, websocket=None, assistant = None, user_proxy = None):
        self.websocket = websocket
        self.chat_id = chat_id
        self.client_sent_queue = asyncio.Queue()
        self.client_receive_queue = asyncio.Queue()
        if assistant is None:
            raise Exception("AssistantAgent is missing...")
        if user_proxy is None:
            raise Exception("UserProxy is missing...")
        self.assistant = assistant
        self.user_proxy = user_proxy
        # add the queues to communicate
        self.user_proxy.set_queues(self.client_sent_queue, self.client_receive_queue)

    async def begin_conversation(self, message):
        await self.user_proxy.a_initiate_chat(
        self.assistant,
        clear_history=True,
        message=message
        )

    async def send_to_client(chat_session):
        while True:
            reply = await chat_session.client_receive_queue.get()
            if reply and reply == "DO_FINISH":
                chat_session.client_receive_queue.task_done()
                break
            await chat_session.websocket.send_text(reply)
            chat_session.client_receive_queue.task_done()
            await asyncio.sleep(1)

    async def receive_from_client(chat_session):
    while True:
        data = await chat_session.websocket.receive_text()
        if data and data == "DO_FINISH":
            await chat_session.client_receive_queue.put("DO_FINISH")
            await chat_session.client_sent_queue.put("DO_FINISH")
            break
        await chat_session.client_sent_queue.put(data)
        await asyncio.sleep(1)