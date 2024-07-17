from typing import Any, Literal, cast, List, Dict, Union
from dotenv import load_dotenv
import chainlit as cl

from langchain_core.messages import AIMessage, HumanMessage, MessageLikeRepresentation
from langgraph.graph.graph import CompiledGraph

from langcode.jupyter import Jupyter

from model import create_state_graph
from utils import image_to_base64

load_dotenv(".env")


@cl.on_chat_start
async def on_chat_start():
    messages: list[MessageLikeRepresentation] = []
    jupyter: Jupyter = Jupyter.local() # type: ignore (later fix the JupyterLocal != Jupyter issue.)
    runnable: CompiledGraph = create_state_graph()

    cl.user_session.set("messages", messages)
    cl.user_session.set("jupyter", jupyter)
    cl.user_session.set("runnable", runnable)

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
    runnable: CompiledGraph = cl.user_session.get("runnable") # type: ignore

    images = [file for file in message.elements if file.mime and "image" in file.mime]

    content = [{"type": "text", "text": message.content}] + [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_to_base64(file.path)}"
            },
        }
        for file in images
        if file.path
    ]

    content = cast(List[Union[str, Dict]], content)

    messages.append(HumanMessage(content=content))

    final_state = await runnable.ainvoke(
        {
            "messages": messages,
            "temperature": 0.5,
        }
    )

    cl.user_session.set("messages", final_state["messages"])
