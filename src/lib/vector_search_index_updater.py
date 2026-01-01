from logging import Logger

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.operations import SearchIndexModel

from src.configurations.service_model import RelevanceScoreFn
from src.constants import DEFAULT_NUM_DIMENSIONS_VALUE, DIMENSIONS_DICT, VECTOR_INDEX_TYPE
from src.context import AppContext


class VectorSearchIndexUpdater:
    def __init__(self, app_context: AppContext):
        self.app_context: AppContext = app_context
        self.logger: Logger = app_context.logger
        self.embedding_key = app_context.configurations.vectorStore.embeddingKey
        self.index_name = app_context.configurations.vectorStore.indexName

        self.collection: Collection = None
        self._init_collection()

    def _init_collection(self) -> None:
        mongo_cluster_uri = self.app_context.env_vars.MONGODB_CLUSTER_URI
        db_name = self.app_context.configurations.vectorStore.dbName
        collection_name = self.app_context.configurations.vectorStore.collectionName

        try:
            client = MongoClient(mongo_cluster_uri)
            db = client.get_database()
        # pylint: disable=broad-except
        except Exception:
            db = client[db_name]

        # Create the collection if it does not exist
        if collection_name not in db.list_collection_names():
            self.logger.info(f'Collection "{collection_name}" missing, it will be created now')
            db.create_collection(collection_name)
        self.collection = db[collection_name]

    def _create_vector_index(self, new_index_definition: SearchIndexModel) -> None:
        self.logger.info(
            f'Vector Search index "{self.index_name}" missing in {self.collection.name}, it will be created now'
        )
        self.logger.debug(
            f'Creating Vector Search index to the following definition: "{new_index_definition.document.get("definition")}"'
        )
        self.collection.create_search_index(model=new_index_definition)
        self.logger.info(f'Created Vector Search index "{self.index_name}"')

    def _update_vector_index(self, current_index_definition: SearchIndexModel, new_index_definition: SearchIndexModel):
        self.logger.info(f'Check of MongoDB Vector Search index "{self.index_name}"')

        current_fields = current_index_definition.document.get("definition")
        new_fields = new_index_definition.document.get("definition")

        if current_fields == new_fields:
            self.logger.info("Vector Search index is up-to-date, no further action required")
            return

        self.logger.debug(f'Updating Vector Search index to the following definition: "{new_fields.get("fields")}"')
        self.collection.update_search_index(self.index_name, new_fields)
        self.logger.info(f'Updated Vector Search index "{self.index_name}" in collection {self.collection.name}')

    def _get_current_vector_index_definition(self) -> SearchIndexModel | None:
        indexes = self.collection.list_search_indexes()

        vector_index = next((index for index in indexes if index["name"] == self.index_name), None)

        if vector_index is None:
            return None

        return SearchIndexModel(
            definition=vector_index.get("latestDefinition"), name=vector_index.get("name"), type="vectorSearch"
        )

    def _get_updated_vector_index_definition(self) -> SearchIndexModel:
        configured_similarity_fn = (
            self.app_context.configurations.vectorStore.relevanceScoreFn or RelevanceScoreFn.cosine
        )
        num_dimensions = DIMENSIONS_DICT.get(
            self.app_context.configurations.embeddings.name, DEFAULT_NUM_DIMENSIONS_VALUE
        )

        return SearchIndexModel(
            definition={
                "fields": [
                    {
                        "numDimensions": num_dimensions,
                        "path": self.embedding_key,
                        "similarity": configured_similarity_fn.value,
                        "type": "vector",
                    }
                ]
            },
            name=self.index_name,
            type=VECTOR_INDEX_TYPE,
        )

    def update_vector_search_index(self) -> None:
        try:
            current_vector_index_definition = self._get_current_vector_index_definition()
            new_vector_index_definition = self._get_updated_vector_index_definition()

            if current_vector_index_definition is None:
                self._create_vector_index(new_vector_index_definition)
            else:
                self._update_vector_index(current_vector_index_definition, new_vector_index_definition)
        # pylint: disable=broad-except
        except Exception as ex:
            self.logger.warning(f'Unable to update Vector Search index "{self.index_name}".')
            self.logger.warning(ex)
            self.logger.warning("Service will continue to run, but you might experience unwanted behaviors.")
