from typing import Any, Dict, List, Optional, Type

from attr import dataclass
from langchain.chains.base import Chain
from langchain_core.callbacks import CallbackManagerForChainRun
from langchain_core.embeddings import Embeddings
from langchain_core.runnables import RunnableConfig
from langchain_mongodb import MongoDBAtlasVectorSearch
from pydantic import BaseModel, create_model

from src.context import AppContext


@dataclass
class RetrieverChainConfiguration:
    mongodb_cluster_uri: str
    db_name: str
    collection_name: str
    embeddings: Embeddings
    index_name: str
    embedding_key: str
    relevance_score_fn: str
    text_key: str
    max_number_of_results: int
    max_score_distance: Optional[float] = None
    min_score_distance: Optional[float] = None


class RetrieverChain(Chain):

    context: AppContext
    configuration: RetrieverChainConfiguration

    query_key: str = "query"  #: :meta private:
    output_key: str = "input_documents"  #: :meta private:

    @property
    def input_keys(self) -> List[str]:
        return [self.query_key]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def get_input_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[BaseModel]:
        return create_model(
            "RetrieveChainInput",
            **{
                self.query_key: (
                    str,  # query
                    None
                ),
            },  # type: ignore[call-overload]
        )

    def get_output_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[BaseModel]:
        return create_model(
            "RetrieveChainOutput",
            **{self.output_key: (
                str,  # response
                None
            )},  # type: ignore[call-overload]
        )

    def _setup_vector_search(self):
        return MongoDBAtlasVectorSearch.from_connection_string(
            connection_string=self.configuration.mongodb_cluster_uri,
            namespace=f'{self.configuration.db_name}.{self.configuration.collection_name}',
            embedding=self.configuration.embeddings,
            index_name=self.configuration.index_name,
            embedding_key=self.configuration.embedding_key,
            relevance_score_fn=self.configuration.relevance_score_fn,
            text_key=self.configuration.text_key
        )
        
    def _get_post_filter_pipeline(self):
        if self.configuration.max_score_distance is not None:
            return [
                {
                    "$match": {
                        "score": {
                            "$lte": self.configuration.max_score_distance
                        }
                    },
                }
            ]
        if self.configuration.min_score_distance is not None:
            return [
                {
                    "$match": {
                        "score": {
                            "$gte": self.configuration.min_score_distance
                        }
                    },
                }
            ]
        return None

    def _call(self, inputs: Dict[str, Any], run_manager: CallbackManagerForChainRun | None = None) -> Dict[str, Any]:
        query = inputs[self.query_key]
        post_filter_pipeline = self._get_post_filter_pipeline()
        vector_search = self._setup_vector_search()
        result = vector_search.similarity_search(
            query,
            k=self.configuration.max_number_of_results,
            additional= {
                "similarity_score": True
            },
            post_filter_pipeline=post_filter_pipeline
        )
        return {
            self.output_key: result
        }
