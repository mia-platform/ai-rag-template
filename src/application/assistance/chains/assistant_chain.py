from typing import Any, Dict, List, Optional, Type, Union

from langchain.chains.base import Chain
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationTokenBufferMemory
from langchain_core.callbacks import CallbackManagerForChainRun
from langchain_core.documents import Document
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.utils import create_model

from src.application.assistance.chains.assistant_prompt import AssistantPromptBuilder, AssistantPromptTemplate
from src.application.assistance.chains.retriever_chain import RetrieverChain


class AssistantChain(Chain):

    retriever_chain: RetrieverChain
    aggregate_docs_chain: BaseCombineDocumentsChain
    llm: Union[
        Runnable[LanguageModelInput, str],
        Runnable[LanguageModelInput, BaseMessage],
    ]
    prompt_template: AssistantPromptTemplate | None = None

    query_key: str = "query"  #: :meta private:
    chat_history_key: str = "chat_history"  #: :meta private:
    response_key: str = "text"  #: :meta private:
    references_key: str = "input_documents"  #: :meta private:
    chat_history_max_token_limit: int = 2000
    prompt_custom_variables_key: str = "input_custom_variables"  #: :meta private:

    @property
    def input_keys(self) -> List[str]:
        return [self.query_key, self.chat_history_key]

    @property
    def output_keys(self) -> List[str]:
        return [self.response_key, self.references_key]

    def get_input_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[BaseModel]:
        return create_model(
            "AssistantChainInput",
            **{
                self.query_key: (
                    str,  # query
                    None
                ),
                self.chat_history_key: (
                    str,  # chat_history
                    None
                ),
                self.prompt_custom_variables_key: (
                    Optional[Dict[str, Any]],  # custom variables
                    {}
                ),
            },  # type: ignore[call-overload]
        )

    def get_output_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[BaseModel]:
        return create_model(
            "AssistantChainOutput",
            **{
                self.response_key: (
                    str,  # model response
                    None
                ),
                self.references_key: (
                    List[Document],  # used documents
                    None
                ),
            },  # type: ignore[call-overload]
        )
        
    def _build_default_prompt(self) -> PromptTemplate:
        return AssistantPromptBuilder().build()

    def _create_llm_chain(self):
        if not self.prompt_template:
            self.prompt_template = self._build_default_prompt()

        return LLMChain(
            llm=self.llm,
            prompt=self.prompt_template
        )

    def _create_chain(self, llm_chain):
        return self.retriever_chain | self.aggregate_docs_chain | llm_chain

    def _invoke_chain(self, chain, chat_history, query, custom_prompt_variables):
        return chain.invoke(
            input={
                "chat_history": self._process_chat_history(chat_history),
                "query": query,
                **custom_prompt_variables
            },
            config=None
        )

    def _call(self, inputs: Dict[str, Any], run_manager: CallbackManagerForChainRun | None = None) -> Dict[str, Any]:
        query, chat_history = inputs[self.query_key], inputs[self.chat_history_key]
        custom_prompt_variables = inputs.get(self.prompt_custom_variables_key, {})

        llm_chain = self._create_llm_chain()
        chain = self._create_chain(llm_chain)
        chain_response = self._invoke_chain(chain, chat_history, query, custom_prompt_variables)

        return chain_response

    def _process_chat_history(self, chat_history: List[str]) -> str:
        memory = ConversationTokenBufferMemory(
            llm=self.llm,
            max_token_limit=self.chat_history_max_token_limit
        )

        for i in range(0, len(chat_history) - 1, 2):
            input_message = chat_history[i]
            output_message = chat_history[i + 1]

            memory.save_context(
                {"input": input_message},
                {"output": output_message}
            )

        memory_values = memory.load_memory_variables({})

        if len(memory_values.get("history")) > 0:
            return \
f"""
Referring to the previous conversation messages:

{memory_values["history"]}

---
"""

        return ""
