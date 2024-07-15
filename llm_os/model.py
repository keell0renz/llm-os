from typing import TypedDict, Annotated, Sequence
import operator

import chainlit as cl

from langcode.jupyter import Jupyter

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage
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
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages")
    ]
)


def model(state: AgentState):
    chain = prompt | ChatAnthropic(temperature=state["temperature"], model="claude-3-5-sonnet-20240620")  # type: ignore

    response = chain.invoke(
        {
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
    )

    return {"messages": [response]}


async def executor(state: AgentState):
    xml = ToolParser.extract_and_parse_xml(state["messages"][-1].content)  # type: ignore
    jupyter: Jupyter = cl.user_session.get("jupyter")  # type: ignore

    for call in xml:
        if call.get("python", None):
            async with cl.Step(name="Jupyter Notebook") as step:
                step.input = call["python"]
                result = jupyter.run_cell(call["python"], timeout=600000)
                step.output = result.text

            images = []

            for image in result.images:
                images.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image.content_format};base64,{image.content}"
                        },
                    }
                )

            return {
                "messages": [
                    HumanMessage(
                        content=[{"type": "text", "text": result.text}] + images
                    )
                ]
            }


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
