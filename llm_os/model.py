from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langcode.jupyter import Jupyter
import operator


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    temperature: int
    jupyter: Jupyter
