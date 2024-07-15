from dotenv import load_dotenv
import chainlit as cl

load_dotenv(".env")

# On chat start: create a jupyter notebook.
# On each message: determine agent info state, retrieve chat history, stream, update chat history.
# On stop: stop streaming, stop jupyter notebook.
# On chat end: close the jupyter notebook.

@cl.on_chat_start
async def on_chat_start():
    pass

@cl.on_stop
async def on_stop():
    pass

@cl.on_chat_end
async def on_chat_end():
    pass

@cl.on_message
async def main(message: cl.Message):
    await cl.Message(
        content=f"Received: {message.content}",
    ).send()
