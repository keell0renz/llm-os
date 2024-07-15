from typing import TypedDict, Annotated, Sequence
import operator

from langcode.jupyter import Jupyter

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage

from llm_os.prompt import SYSTEM_PROMPT
from llm_os.info import *


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    temperature: int
    jupyter: Jupyter


