"""Fake LLM wrapper for testing purposes."""

from collections.abc import Mapping
from typing import Any, cast

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from pydantic import ValidationInfo, field_validator


class FakeLLM(LLM):
    """Fake LLM wrapper for testing purposes."""

    queries: Mapping | None = None
    sequential_responses: bool | None = False
    response_index: int = 0
    prompts_received: list[str] = []  # received prompts for testing

    @field_validator("queries", check_fields=True)
    # pylint: disable=no-self-argument
    def check_queries_required(cls, queries: Mapping | None, values: ValidationInfo) -> Mapping | None:
        if values.data.get("sequential_response") and not queries:
            raise ValueError("queries is required when sequential_response is set to True")
        return queries

    def get_num_tokens(self, text: str) -> int:
        """Return number of tokens."""
        return len(text.split())

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "fake"

    def _call(
        self,
        prompt: str,
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> str:
        self.prompts_received.append(prompt)  # store received prompts for testing
        if self.sequential_responses:
            return self._get_next_response_in_sequence
        if self.queries is not None:
            return self.queries[prompt]
        if stop is None:
            return "foo"
        return "bar"

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {}

    @property
    def _get_next_response_in_sequence(self) -> str:
        queries = cast(Mapping, self.queries)
        response = queries[list(queries.keys())[self.response_index]]
        self.response_index = self.response_index + 1
        return response

    @property
    def get_received_prompts(self) -> list[str]:
        return self.prompts_received

    def get_last_received_prompt(self) -> str:
        return self.prompts_received[-1] if len(self.prompts_received) > 0 else ""

    def clear_received_prompts(self):
        self.prompts_received = []
