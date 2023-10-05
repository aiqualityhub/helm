from typing import List, Dict

from helm.common.cache import Cache, CacheConfig
from helm.common.request import Request, RequestResult, Sequence, Token
from helm.common.tokenization_request import (
    DecodeRequest,
    DecodeRequestResult,
    TokenizationRequest,
    TokenizationRequestResult,
    TokenizationToken,
)
from helm.proxy.tokenizers.tokenizer import Tokenizer
from .client import Client, wrap_request_time


class SimpleClient(Client):
    """Implements some "models" that just generate silly things quickly just to debug the infrastructure."""

    def __init__(self, tokenizer: Tokenizer, cache_config: CacheConfig):
        super().__init__(cache_config=cache_config, tokenizer=tokenizer)

    def make_request(self, request: Request) -> RequestResult:
        raw_request = {
            "engine": request.model_engine,
            "prompt": request.prompt,
            "n": request.num_completions,
        }

        if request.model_engine == "model1":

            def do_it():
                return self.invoke_model1(raw_request)

            cache_key = Client.make_cache_key(raw_request, request)
            response, cached = self.cache.get(cache_key, wrap_request_time(do_it))
            completions = [
                Sequence(
                    text=text,
                    logprob=logprob,
                    tokens=[Token(text=text, logprob=logprob, top_logprobs=response["completions"])],
                )
                for text, logprob in response["completions"].items()
            ]
        else:
            raise ValueError(f"Invalid model: {request.model}")

        return RequestResult(
            success=True,
            cached=False,
            request_time=0,
            request_datetime=response.get("request_datetime"),
            completions=completions,
            embedding=[],
        )

    def invoke_model1(self, raw_request: Dict) -> Dict:
        """
        Example: 7 2 4 6
        Completions (num_completions = 3):
        - 6
        - 4
        - 2
        """
        prompt_tokens: List[str] = SimpleClient.tokenize_by_space(raw_request["prompt"])
        choices = reversed(prompt_tokens[-raw_request["n"] :])
        response = {"completions": dict((text, -i) for i, text in enumerate(choices))}
        return response
