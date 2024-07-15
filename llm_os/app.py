from dotenv import load_dotenv
import chainlit as cl

from langchain_core.messages import AIMessage, HumanMessage, MessageLikeRepresentation
from langgraph.graph.graph import CompiledGraph

from langcode.jupyter import Jupyter

from model import create_state_graph

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

    inputs = {
        "messages": messages,
        "temperature": 0.5,
    }

    messages.append(HumanMessage(content=message.content))

    response = cl.Message(content="")

    async for output in runnable.astream_log(inputs, include_types=["llm"]):
        for op in output.ops:
            if op["path"].startswith("/logs/") and op["path"].endswith(
                "/streamed_output/-"
            ):
                await response.stream_token(op["value"].content)

    messages.append(AIMessage(content=response.content))
