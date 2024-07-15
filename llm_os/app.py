from dotenv import load_dotenv
import chainlit as cl

from langchain_core.messages import AIMessage, MessageLikeRepresentation

from langcode.jupyter import Jupyter

from .model import runnable

load_dotenv(".env")


@cl.on_chat_start
async def on_chat_start():
    messages: list[MessageLikeRepresentation] = []
    jupyter: Jupyter = Jupyter.local() # type: ignore (later fix the JupyterLocal != Jupyter issue.)

    cl.user_session.set("messages", messages)
    cl.user_session.set("jupyter", jupyter)

@cl.on_stop
async def on_stop():
    #TODO Stop jupyter + stop streaming.
    pass

@cl.on_chat_end
async def on_chat_end():
    jupyter: Jupyter = cl.user_session.get("jupyter") # type: ignore

    jupyter.close()

@cl.on_message
async def main(message: cl.Message):
    messages: list[MessageLikeRepresentation] = cl.user_session.get("messages") # type: ignore
    jupyter: Jupyter = cl.user_session.get("jupyter")  # type: ignore

    inputs = {
        "messages": messages,
        "temperature": 0.5,
        "jupyter": jupyter
    }

    response = cl.Message(content="")

    async for output in runnable.astream_log(inputs, include_types=["llm"]):
        for op in output.ops:
            # if op["path"] == "/streamed_output/-":
            #     if op["value"].get("executor", None):
            #         for message in op["value"]["executor"]["messages"]:
            #             print("\n\n<output>")
            #             print(message.content[0]["text"])

            #             for image_base64_obj in message.content[1:]:
            #                 image_base64_str = image_base64_obj["image_url"]["url"].split(
            #                     ","
            #                 )[1]
            #                 image_data = base64.b64decode(image_base64_str)
            #                 display(Image(data=image_data))

            #             print("</output>\n")

            if op["path"].startswith("/logs/") and op["path"].endswith(
                "/streamed_output/-"
            ):
                await response.stream_token(op["value"].content)

    messages.append(AIMessage(content=response.content))