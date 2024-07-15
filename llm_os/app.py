from dotenv import load_dotenv
import chainlit as cl

load_dotenv(".env")

# On chat start: create a jupyter notebook.
# On each message: determine agent info state, retrieve chat history, stream, update chat history.
# On stop: stop streaming, stop jupyter notebook.
# On chat end: close the jupyter notebook.


@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...

    # Send a response back to the user
    await cl.Message(
        content=f"Received: {message.content}",
    ).send()
