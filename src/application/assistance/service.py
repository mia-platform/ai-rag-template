
from dataclasses import dataclass
from typing import Dict, List
from pymongo.uri_parser import parse_uri

from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.embeddings import Embeddings
from langchain_openai import AzureChatOpenAI, OpenAIEmbeddings

from src.application.assistance.chains.assistant_prompt import AssistantPromptBuilder, AssistantPromptTemplate
from src.application.assistance.chains.assistant_chain import AssistantChain
from src.application.assistance.chains.combine_docs_chain import \
    AggregateDocsChunksChain
from src.application.assistance.chains.retriever_chain import (
    RetrieverChainConfiguration, RetrieverChain)
from src.context import AppContext

@dataclass
class AssistantServiceChatCompletionResponse:
    response: str
    references: List[Dict[str, str]]

@dataclass
class AssistantServiceConfiguration:
    prompt_template: AssistantPromptTemplate

class AssistantService:

    _chain: AssistantChain

    def __init__(
        self,
        app_context: AppContext,
        configuration: AssistantServiceConfiguration = None
    ) -> None:
        """ 
        Initialize the Assistant Service
        """
        self.app_context = app_context
        self.configuration = configuration or AssistantServiceConfiguration(prompt_template=None)
        self._setup_assistant()

    def _init_embeddings(self):
        # Load the embeddings model

        embeddings_config = self.app_context.configurations.embeddings
        embeddings_api_key = self.app_context.env_vars.EMBEDDINGS_API_KEY

        embeddings_model = OpenAIEmbeddings(
            openai_api_key=embeddings_api_key,
            model=embeddings_config.name
        )

        return embeddings_model

    def _init_llm(self):
        # Load the LLM model
        llm_config = self.app_context.configurations.llm
        llm_api_key = self.app_context.env_vars.LLM_API_KEY
        llm_url = self.app_context.configurations.llm.url
        self.app_context.logger.info(f"LLM url: {llm_url}")
        llm = AzureChatOpenAI(
            azure_deployment="dep-gpt-35-turbo",
            api_version="2024-05-01-preview",
            api_key=llm_api_key,
            temperature=0.7,
            max_tokens=50,
            timeout=None,
            max_retries=2,
            azure_endpoint=" https://cnh-we-pr-miarun-openai-01.openai.azure.com/"
            model_version="0301",
        )
        # llm = AzureOpenAI(
        #     model=llm_config.name,
        #     api_key=llm_api_key,
        #     azure_endpoint=llm_url if llm_url else None,
        #     temperature=llm_config.temperature,
        #     api_version='2024-05-01-preview'
        # )
        self.app_context.logger.info(llm)

        return llm

    def _init_retriever_chain(self, embeddings: Embeddings):
        """
        Initialize the retriever
        """
        vector_store_configurations = self.app_context.configurations.vectorStore
        vector_store_cluster_uri = self.app_context.env_vars.MONGODB_CLUSTER_URI

        db_name = \
            vector_store_configurations.dbName or \
            parse_uri(vector_store_cluster_uri).get('database')
        
        if db_name is None:
            raise ValueError("Database name is not provided in the configuration or the cluster URI")

        configuration = RetrieverChainConfiguration(
            mongodb_cluster_uri=vector_store_cluster_uri,
            db_name=db_name,
            collection_name=vector_store_configurations.collectionName,
            embeddings=embeddings,
            index_name=vector_store_configurations.indexName,
            embedding_key=vector_store_configurations.embeddingKey,
            relevance_score_fn=vector_store_configurations.relevanceScoreFn,
            text_key=vector_store_configurations.textKey,
            max_number_of_results=vector_store_configurations.maxDocumentsToRetrieve,
            max_score_distance=vector_store_configurations.maxScoreDistance,
            min_score_distance=vector_store_configurations.minScoreDistance
        )

        retriever_chain = RetrieverChain(
            context=self.app_context,
            configuration=configuration
        )

        return retriever_chain

    def _init_documentation_aggregator(self):
        """
        Initialize the documentation aggregator
        """
        tokenizer_config = self.app_context.configurations.tokenizer
        chain_config = self.app_context.configurations.chain

        return AggregateDocsChunksChain(
            context=self.app_context,
            tokenizer_model_name=tokenizer_config.name,
            aggreate_max_token_number=chain_config.aggregateMaxTokenNumber
        )
        
    def _build_prompt(self) -> AssistantPromptTemplate:
        """ This function builds the prompt template for the Assistant 
            The fallback order is:
            1. Configuration
            2. Configuration file
            3. Default prompt
            
            # perf: this function at the moment is being called every time the Assistant is initialized and so one time per request
            We should consider caching the prompt template if it is not going to change during the lifetime of the software
            We could achieve this by storing the prompt template content inside app_context and only build it once
        """
        try: 
            if self.configuration.prompt_template:
                return self.configuration.prompt_template
        except AttributeError:
            pass
        try: 
            if self.app_context.configurations.chain.rag.promptsFilePath:
                builder = AssistantPromptBuilder()
                if self.app_context.configurations.chain.rag.promptsFilePath.system:
                    builder.load_system_template_from_file(self.app_context.configurations.chain.rag.promptsFilePath.system)
                if self.app_context.configurations.chain.rag.promptsFilePath.user:
                    builder.load_user_template_from_file(self.app_context.configurations.chain.rag.promptsFilePath.user)
                return builder.build()
        except AttributeError:
            pass
        return AssistantPromptBuilder().build() # default prompt  
        
    def _setup_assistant(self):
        # Load the embeddings model
        embeddings = self._init_embeddings()
        # Load the MongoDB Atlas Retriever
        mongo_retriever_chain = self._init_retriever_chain(
            embeddings=embeddings)
        # Load the documentation aggregator
        aggregate_docs_chain = self._init_documentation_aggregator()
        # Load the LLM
        llm = self._init_llm()
        # Extract the custom template if it exists
        prompt_template = self._build_prompt()
        # Load the Assistant Chain
        self._chain = AssistantChain(
            retriever_chain=mongo_retriever_chain,
            aggregate_docs_chain=aggregate_docs_chain,
            llm=llm,
            prompt_template=prompt_template
        )

    def chat_completion(
        self,
        query: str,
        chat_history: List[str],
        custom_template_variables: Dict[str, str] = None
    ) -> AssistantServiceChatCompletionResponse:
        """
        Chat completion using Assistant Chain
        """
        with get_openai_callback() as openai_callback:
            inputs = {
                self._chain.query_key: query,
                self._chain.chat_history_key: chat_history
            }
            if custom_template_variables:
                inputs[self._chain.prompt_custom_variables_key] = custom_template_variables

            chain_response = self._chain.invoke(inputs)
            
            self.app_context.metrics_manager.requests_tokens_consumed.inc(openai_callback.prompt_tokens)
            self.app_context.metrics_manager.reply_tokens_consumed.inc(openai_callback.completion_tokens)
            
            return AssistantServiceChatCompletionResponse(
                response=chain_response[self._chain.response_key],
                references=chain_response[self._chain.references_key]
            )
