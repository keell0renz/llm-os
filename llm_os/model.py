import base64
import dis
from typing import TypedDict, Annotated, Sequence
import operator
import os

import chainlit as cl

from langcode.jupyter import Jupyter, Base64ImageString

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph

from prompt import SYSTEM_PROMPT
from xml_parser import ToolParser
from info import *


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    temperature: int


prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), MessagesPlaceholder(variable_name="messages")]
)


# Recursion limit increase!
async def model(state: AgentState):
    chain = prompt | ChatAnthropic(temperature=state["temperature"], model="claude-3-5-sonnet-20240620")  # type: ignore

    result_text = ""

    ui_response_message = cl.Message(content="")

    await ui_response_message.send()

    inputs = {
        "messages": state["messages"],
        "os_uname_a": get_os_uname_a(),
        "date": get_date(),
        "time": get_time(),
        "timezone": get_timezone(),
        "country": get_country(),
        "city": get_city(),
        "username": get_username(),
        "users_real_name": get_users_real_name(),
        "users_email": get_users_email(),
        "access_to_the_internet": get_access_to_the_internet(),
        "cpu_load": get_cpu_load(),
        "ram_load": get_ram_load(),
    }

    async for chunk in chain.astream(inputs):
        result_text += str(chunk.content)
        # await ui_response_message.stream_token(str(chunk.content))
        ui_response_message.content = result_text.replace(
            "<python>", "```python"
        ).replace("</python>", "```")
        await ui_response_message.update()

    return {"messages": [AIMessage(content=result_text)]}


async def executor(state: AgentState):
    xml = ToolParser.extract_and_parse_xml(state["messages"][-1].content)  # type: ignore
    jupyter: Jupyter = cl.user_session.get("jupyter")  # type: ignore

    responses = []

    ask_for_code_execution = (
        True if os.environ["ASK_FOR_CODE_EXECUTION"] == "True" else False
    )

    res = None

    if ask_for_code_execution:
        res = await cl.AskActionMessage(
            content="Execute code?",
            actions=[
                cl.Action(name="execute", value="execute", label="Execute"),
                cl.Action(name="cancel", value="cancel", label="Cancel"),
            ],
        ).send()

    if (res and res.get("value", "") == "execute") or ask_for_code_execution == False:
        for call in xml:
            if call.get("python", None):
                images = []
                images_to_message = []

                ui_output_message = cl.Message(content="", language="txt")
                await ui_output_message.send()

                ui_output_buffer = ""

                for event in jupyter.stream_cell(call["python"], timeout=600000):
                    if event.content_format in ["base64/png", "base64/jpeg"]:
                        images.append(Base64ImageString(content_format=("png" if event.content_format == "base64/png" else "jpeg"), content=event.content))

                        ui_output_message.elements.append(cl.Image(content=base64.b64decode(event.content), display="inline", size="large")) # type: ignore
                        await ui_output_message.update()
                    else:
                        ui_output_buffer += event.content

                        ui_output_message.content = ui_output_buffer
                        await ui_output_message.update()

                for image in images:
                    images_to_message.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image.content_format};base64,{image.content}"
                            },
                        }
                    )

                responses.append(
                    HumanMessage(
                        content=[{"type": "text", "text": ui_output_buffer}] + images_to_message
                    )
                )

    else:
        return {
            "messages": [
                HumanMessage(
                    content="User has cancelled the execution, do not try to execute code again unless user asks so."
                )
            ]
        }

    return {"messages": responses}


def router(state: AgentState):
    xml = ToolParser.extract_and_parse_xml(state["messages"][-1].content.strip())  # type: ignore

    if xml:
        return "execute"
    else:
        return "end"


def create_state_graph() -> CompiledGraph:
    graph = StateGraph(AgentState)

    graph.add_node("model", model)
    graph.add_node("executor", executor)

    graph.add_conditional_edges("model", router, {"execute": "executor", "end": END})
    graph.add_edge("executor", "model")

    graph.set_entry_point("model")

    return graph.compile()
