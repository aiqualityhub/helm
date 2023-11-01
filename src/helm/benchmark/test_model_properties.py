"""Temporary test for preserving invariants during the model / tokenizer / window service refactor.

Delete this after the refactor is done."""

from tempfile import TemporaryDirectory
from typing import Any
from helm.benchmark.model_deployment_registry import ClientSpec, ModelDeployment, WindowServiceSpec
from helm.benchmark.tokenizer_config_registry import TokenizerConfig, TokenizerSpec
from helm.benchmark.window_services.test_utils import get_tokenizer_service

from helm.benchmark.window_services.window_service_factory import WindowServiceFactory
from helm.proxy.clients.auto_client import AutoClient
from helm.proxy.models import ALL_MODELS
from collections import defaultdict


_BUILT_IN_TOKENIZER_CONFIGS = [
    TokenizerConfig(
        name="neurips/local",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.http_model_tokenizer.HTTPModelTokenizer"),
        end_of_text_token="<|endoftext|>",
        prefix_token="<|endoftext|>",
    ),
    TokenizerConfig(
        name="ai21/j1",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.ai21_tokenizer.AI21Tokenizer"),
        end_of_text_token=" ",
        prefix_token="",
    ),
    TokenizerConfig(
        name="AlephAlpha/luminous-base",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.aleph_alpha_tokenizer.AlephAlphaTokenizer"),
        end_of_text_token="",
        prefix_token="",
    ),
    TokenizerConfig(
        name="AlephAlpha/luminous-extended",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.aleph_alpha_tokenizer.AlephAlphaTokenizer"),
        end_of_text_token="",
        prefix_token="",
    ),
    TokenizerConfig(
        name="AlephAlpha/luminous-supreme",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.aleph_alpha_tokenizer.AlephAlphaTokenizer"),
        end_of_text_token="",
        prefix_token="",
    ),
    TokenizerConfig(
        name="huggingface/gpt2",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="<|endoftext|>",
        prefix_token="<|endoftext|>",
    ),
    TokenizerConfig(
        name="anthropic/claude",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.anthropic_tokenizer.AnthropicTokenizer"),
        end_of_text_token="<|endoftext|>",
        prefix_token="<|endoftext|>",
    ),
    TokenizerConfig(
        name="bigscience/bloom",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="</s>",
    ),
    TokenizerConfig(
        name="bigscience/T0pp",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="",
    ),
    TokenizerConfig(
        name="cohere/cohere",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.cohere_tokenizer.CohereTokenizer"),
        end_of_text_token="",
        prefix_token=":",
    ),
    TokenizerConfig(
        name="EleutherAI/gpt-j-6B",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="<|endoftext|>",
        prefix_token="<|endoftext|>",
    ),
    TokenizerConfig(
        name="EleutherAI/gpt-neox-20b",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="<|endoftext|>",
        prefix_token="<|endoftext|>",
    ),
    TokenizerConfig(
        name="hf-internal-testing/llama-tokenizer",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="<s>",
    ),
    TokenizerConfig(
        name="meta-llama/Llama-2-7b-hf",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="<s>",
    ),
    TokenizerConfig(
        name="mistralai/Mistral-7B-v0.1",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="<s>",
    ),
    TokenizerConfig(
        name="tiiuae/falcon-7b",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="<|endoftext|>",
        prefix_token=None,
    ),
    TokenizerConfig(
        name="bigcode/santacoder",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="<|endoftext|>",
        prefix_token="<|endoftext|>",
    ),
    TokenizerConfig(
        name="bigcode/starcoder",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="<|endoftext|>",
        prefix_token="<|endoftext|>",
    ),
    TokenizerConfig(
        name="google/t5-11b",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="",
    ),
    TokenizerConfig(
        name="google/flan-t5-xxl",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="",
    ),
    TokenizerConfig(
        name="google/ul2",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="",
    ),
    TokenizerConfig(
        name="facebook/opt-66b",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="</s>",
    ),
    TokenizerConfig(
        name="openai/cl100k_base",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.tiktoken_tokenizer.TiktokenTokenizer"),
        end_of_text_token="<|endoftext|>",
        prefix_token="<|endoftext|>",
    ),
    TokenizerConfig(
        name="TsinghuaKEG/ice",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.ice_tokenizer.ICETokenizer"),
        end_of_text_token="</s>",
        prefix_token="",
    ),
    TokenizerConfig(
        name="Yandex/yalm",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.yalm_tokenizer.YaLMTokenizer"),
        end_of_text_token="</s>",
        prefix_token="</s>",
    ),
    TokenizerConfig(
        name="HuggingFaceM4/idefics-9b",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="<s>",
    ),
    TokenizerConfig(
        name="HuggingFaceM4/idefics-9b-instruct",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="<s>",
    ),
    TokenizerConfig(
        name="HuggingFaceM4/idefics-80b",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="<s>",
    ),
    TokenizerConfig(
        name="HuggingFaceM4/idefics-80b-instruct",
        tokenizer_spec=TokenizerSpec(class_name="helm.proxy.tokenizers.huggingface_tokenizer.HuggingFaceTokenizer"),
        end_of_text_token="</s>",
        prefix_token="<s>",
    ),
]


_BUILT_IN_MODEL_DEPLOYMENTS = [
    ModelDeployment(
        name="neurips/local",
        client_spec=ClientSpec(class_name="helm.proxy.clients.http_model_client.HTTPModelClient", args={}),
        tokenizer_name="neurips/local",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.http_model_window_service.HTTPModelWindowServce", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="ai21/j1-jumbo",
        client_spec=ClientSpec(class_name="helm.proxy.clients.ai21_client.AI21Client", args={}),
        tokenizer_name="ai21/j1",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.ai21_window_service.AI21WindowService", args={}
        ),
        max_sequence_length=2047,
    ),
    ModelDeployment(
        name="ai21/j1-grande",
        client_spec=ClientSpec(class_name="helm.proxy.clients.ai21_client.AI21Client", args={}),
        tokenizer_name="ai21/j1",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.ai21_window_service.AI21WindowService", args={}
        ),
        max_sequence_length=2047,
    ),
    ModelDeployment(
        name="ai21/j1-grande-v2-beta",
        client_spec=ClientSpec(class_name="helm.proxy.clients.ai21_client.AI21Client", args={}),
        tokenizer_name="ai21/j1",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.ai21_window_service.AI21WindowService", args={}
        ),
        max_sequence_length=2047,
    ),
    ModelDeployment(
        name="ai21/j1-large",
        client_spec=ClientSpec(class_name="helm.proxy.clients.ai21_client.AI21Client", args={}),
        tokenizer_name="ai21/j1",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.ai21_window_service.AI21WindowService", args={}
        ),
        max_sequence_length=2047,
    ),
    ModelDeployment(
        name="ai21/j2-jumbo",
        client_spec=ClientSpec(class_name="helm.proxy.clients.ai21_client.AI21Client", args={}),
        tokenizer_name="ai21/j1",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.wider_ai21_window_service.AI21Jurassic2JumboWindowService",
            args={},
        ),
        max_sequence_length=6000,
    ),
    ModelDeployment(
        name="ai21/j2-grande",
        client_spec=ClientSpec(class_name="helm.proxy.clients.ai21_client.AI21Client", args={}),
        tokenizer_name="ai21/j1",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.ai21_window_service.AI21WindowService", args={}
        ),
        max_sequence_length=2047,
    ),
    ModelDeployment(
        name="ai21/j2-large",
        client_spec=ClientSpec(class_name="helm.proxy.clients.ai21_client.AI21Client", args={}),
        tokenizer_name="ai21/j1",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.ai21_window_service.AI21WindowService", args={}
        ),
        max_sequence_length=2047,
    ),
    ModelDeployment(
        name="AlephAlpha/luminous-base",
        client_spec=ClientSpec(class_name="helm.proxy.clients.aleph_alpha_client.AlephAlphaClient", args={}),
        tokenizer_name="AlephAlpha/luminous-base",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.luminous_window_service.LuminousBaseWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="AlephAlpha/luminous-extended",
        client_spec=ClientSpec(class_name="helm.proxy.clients.aleph_alpha_client.AlephAlphaClient", args={}),
        tokenizer_name="AlephAlpha/luminous-extended",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.luminous_window_service.LuminousExtendedWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="AlephAlpha/luminous-supreme",
        client_spec=ClientSpec(class_name="helm.proxy.clients.aleph_alpha_client.AlephAlphaClient", args={}),
        tokenizer_name="AlephAlpha/luminous-supreme",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.luminous_window_service.LuminousSupremeWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="anthropic/stanford-online-all-v4-s3",
        client_spec=ClientSpec(class_name="helm.proxy.clients.anthropic_client.AnthropicClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.anthropic_window_service.LegacyAnthropicWindowService", args={}
        ),
        max_sequence_length=8192,
    ),
    ModelDeployment(
        name="anthropic/claude-2.0",
        client_spec=ClientSpec(class_name="helm.proxy.clients.anthropic_client.AnthropicClient", args={}),
        tokenizer_name="anthropic/claude",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.anthropic_window_service.AnthropicWindowService", args={}
        ),
        max_sequence_length=8000,
        max_sequence_and_generated_tokens_length=9016,
    ),
    ModelDeployment(
        name="anthropic/claude-v1.3",
        client_spec=ClientSpec(class_name="helm.proxy.clients.anthropic_client.AnthropicClient", args={}),
        tokenizer_name="anthropic/claude",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.anthropic_window_service.AnthropicWindowService", args={}
        ),
        max_sequence_length=8000,
        max_sequence_and_generated_tokens_length=9016,
    ),
    ModelDeployment(
        name="anthropic/claude-instant-v1",
        client_spec=ClientSpec(class_name="helm.proxy.clients.anthropic_client.AnthropicClient", args={}),
        tokenizer_name="anthropic/claude",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.anthropic_window_service.AnthropicWindowService", args={}
        ),
        max_sequence_length=8000,
        max_sequence_and_generated_tokens_length=9016,
    ),
    ModelDeployment(
        name="together/bloom",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="bigscience/bloom",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.bloom_window_service.BloomWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/t0pp",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="bigscience/T0pp",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.t0pp_window_service.T0ppWindowService", args={}
        ),
        max_sequence_length=1024,
    ),
    ModelDeployment(
        name="cohere/xlarge-20220609",
        client_spec=ClientSpec(class_name="helm.proxy.clients.cohere_client.CohereClient", args={}),
        tokenizer_name="cohere/cohere",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.cohere_window_service.CohereWindowService", args={}
        ),
        max_sequence_length=2047,
        max_request_length=2048,
    ),
    ModelDeployment(
        name="cohere/xlarge-20221108",
        client_spec=ClientSpec(class_name="helm.proxy.clients.cohere_client.CohereClient", args={}),
        tokenizer_name="cohere/cohere",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.cohere_window_service.CohereWindowService", args={}
        ),
        max_sequence_length=2047,
        max_request_length=2048,
    ),
    ModelDeployment(
        name="cohere/large-20220720",
        client_spec=ClientSpec(class_name="helm.proxy.clients.cohere_client.CohereClient", args={}),
        tokenizer_name="cohere/cohere",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.cohere_window_service.CohereWindowService", args={}
        ),
        max_sequence_length=2047,
        max_request_length=2048,
    ),
    ModelDeployment(
        name="cohere/medium-20220720",
        client_spec=ClientSpec(class_name="helm.proxy.clients.cohere_client.CohereClient", args={}),
        tokenizer_name="cohere/cohere",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.cohere_window_service.CohereWindowService", args={}
        ),
        max_sequence_length=2047,
        max_request_length=2048,
    ),
    ModelDeployment(
        name="cohere/medium-20221108",
        client_spec=ClientSpec(class_name="helm.proxy.clients.cohere_client.CohereClient", args={}),
        tokenizer_name="cohere/cohere",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.cohere_window_service.CohereWindowService", args={}
        ),
        max_sequence_length=2047,
        max_request_length=2048,
    ),
    ModelDeployment(
        name="cohere/small-20220720",
        client_spec=ClientSpec(class_name="helm.proxy.clients.cohere_client.CohereClient", args={}),
        tokenizer_name="cohere/cohere",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.cohere_window_service.CohereWindowService", args={}
        ),
        max_sequence_length=2047,
        max_request_length=2048,
    ),
    ModelDeployment(
        name="cohere/command-medium-beta",
        client_spec=ClientSpec(class_name="helm.proxy.clients.cohere_client.CohereClient", args={}),
        tokenizer_name="cohere/cohere",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.cohere_window_service.CohereCommandWindowService", args={}
        ),
        max_sequence_length=2019,
        max_request_length=2020,
    ),
    ModelDeployment(
        name="cohere/command-xlarge-beta",
        client_spec=ClientSpec(class_name="helm.proxy.clients.cohere_client.CohereClient", args={}),
        tokenizer_name="cohere/cohere",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.cohere_window_service.CohereCommandWindowService", args={}
        ),
        max_sequence_length=2019,
        max_request_length=2020,
    ),
    ModelDeployment(
        name="together/gpt-j-6b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-j-6B",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptj_window_service.GPTJWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/gpt-neox-20b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="eleutherai/pythia-1b-v0",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="eleutherai/pythia-2.8b-v0",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="eleutherai/pythia-6.9b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="eleutherai/pythia-12b-v0",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="meta/llama-7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="hf-internal-testing/llama-tokenizer",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.llama_window_service.LlamaWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="meta/llama-13b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="hf-internal-testing/llama-tokenizer",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.llama_window_service.LlamaWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="meta/llama-30b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="hf-internal-testing/llama-tokenizer",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.llama_window_service.LlamaWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="meta/llama-65b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="hf-internal-testing/llama-tokenizer",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.llama_window_service.LlamaWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="meta/llama-2-7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="meta-llama/Llama-2-7b-hf",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.llama_window_service.Llama2WindowService", args={}
        ),
        max_sequence_length=4096,
        max_request_length=1000000000000000019884624838656,
    ),
    ModelDeployment(
        name="meta/llama-2-13b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="meta-llama/Llama-2-7b-hf",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.llama_window_service.Llama2WindowService", args={}
        ),
        max_sequence_length=4096,
        max_request_length=1000000000000000019884624838656,
    ),
    ModelDeployment(
        name="meta/llama-2-70b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="meta-llama/Llama-2-7b-hf",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.llama_window_service.Llama2WindowService", args={}
        ),
        max_sequence_length=4096,
        max_request_length=1000000000000000019884624838656,
    ),
    ModelDeployment(
        name="stanford/alpaca-7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="hf-internal-testing/llama-tokenizer",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.llama_window_service.LlamaWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="lmsys/vicuna-7b-v1.3",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="hf-internal-testing/llama-tokenizer",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.llama_window_service.LlamaWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="lmsys/vicuna-13b-v1.3",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="hf-internal-testing/llama-tokenizer",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.llama_window_service.LlamaWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="mistralai/mistral-7b-v0.1",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="mistralai/Mistral-7B-v0.1",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.huggingface_window_service.HuggingFaceWindowService", args={}
        ),
        max_sequence_length=1000000000000000019884624838656,
    ),
    ModelDeployment(
        name="mosaicml/mpt-7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="mosaicml/mpt-instruct-7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="mosaicml/mpt-30b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="mosaicml/mpt-instruct-30b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="tiiuae/falcon-7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="tiiuae/falcon-7b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.huggingface_window_service.HuggingFaceWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="tiiuae/falcon-7b-instruct",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="tiiuae/falcon-7b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.huggingface_window_service.HuggingFaceWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="tiiuae/falcon-40b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="tiiuae/falcon-7b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.huggingface_window_service.HuggingFaceWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="tiiuae/falcon-40b-instruct",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="tiiuae/falcon-7b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.huggingface_window_service.HuggingFaceWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="gooseai/gpt-neo-20b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.goose_ai_client.GooseAIClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="gooseai/gpt-j-6b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.goose_ai_client.GooseAIClient", args={}),
        tokenizer_name="EleutherAI/gpt-j-6B",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptj_window_service.GPTJWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="huggingface/gpt2",
        client_spec=ClientSpec(class_name="helm.proxy.clients.huggingface_client.HuggingFaceClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gpt2_window_service.GPT2WindowService", args={}
        ),
        max_sequence_length=1024,
        max_request_length=1025,
    ),
    ModelDeployment(
        name="huggingface/gpt-j-6b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.huggingface_client.HuggingFaceClient", args={}),
        tokenizer_name="EleutherAI/gpt-j-6B",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptj_window_service.GPTJWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="huggingface/santacoder",
        client_spec=ClientSpec(class_name="helm.proxy.clients.huggingface_client.HuggingFaceClient", args={}),
        tokenizer_name="bigcode/santacoder",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.santacoder_window_service.SantaCoderWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="huggingface/starcoder",
        client_spec=ClientSpec(class_name="helm.proxy.clients.huggingface_client.HuggingFaceClient", args={}),
        tokenizer_name="bigcode/starcoder",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.starcoder_window_service.StarCoderWindowService", args={}
        ),
        max_sequence_length=8192,
    ),
    ModelDeployment(
        name="together/t5-11b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="google/t5-11b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.t511b_window_service.T511bWindowService", args={}
        ),
        max_sequence_length=511,
    ),
    ModelDeployment(
        name="together/flan-t5-xxl",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="google/flan-t5-xxl",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.flan_t5_window_service.FlanT5WindowService", args={}
        ),
        max_sequence_length=511,
    ),
    ModelDeployment(
        name="together/ul2",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="google/ul2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.ul2_window_service.UL2WindowService", args={}
        ),
        max_sequence_length=511,
    ),
    ModelDeployment(
        name="together/h3-2.7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gpt2_window_service.GPT2WindowService", args={}
        ),
        max_sequence_length=1024,
        max_request_length=1025,
    ),
    ModelDeployment(
        name="together/opt-175b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="facebook/opt-66b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.opt_window_service.OPTWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/opt-66b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="facebook/opt-66b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.opt_window_service.OPTWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/opt-6.7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="facebook/opt-66b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.opt_window_service.OPTWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/opt-1.3b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="facebook/opt-66b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.opt_window_service.OPTWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="microsoft/TNLGv2_530B",
        client_spec=ClientSpec(class_name="helm.proxy.clients.microsoft_client.MicrosoftClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.mt_nlg_window_service.MTNLGWindowService", args={}
        ),
        max_sequence_length=2047,
        max_request_length=2048,
    ),
    ModelDeployment(
        name="microsoft/TNLGv2_7B",
        client_spec=ClientSpec(class_name="helm.proxy.clients.microsoft_client.MicrosoftClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.mt_nlg_window_service.MTNLGWindowService", args={}
        ),
        max_sequence_length=2047,
        max_request_length=2048,
    ),
    ModelDeployment(
        name="openai/davinci",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/curie",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/babbage",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/ada",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/text-davinci-003",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.wider_openai_window_service.WiderOpenAIWindowService", args={}
        ),
        max_sequence_length=4000,
        max_request_length=4001,
    ),
    ModelDeployment(
        name="openai/text-davinci-002",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.wider_openai_window_service.WiderOpenAIWindowService", args={}
        ),
        max_sequence_length=4000,
        max_request_length=4001,
    ),
    ModelDeployment(
        name="openai/text-davinci-001",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/text-curie-001",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/text-babbage-001",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/text-ada-001",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/code-davinci-002",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.wider_openai_window_service.WiderOpenAIWindowService", args={}
        ),
        max_sequence_length=4000,
        max_request_length=4001,
    ),
    ModelDeployment(
        name="openai/code-davinci-001",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/code-cushman-001",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/gpt-4-0314",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/gpt-4-32k-0314",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/gpt-4-0613",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/gpt-4-32k-0613",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/gpt-3.5-turbo-0301",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="openai/cl100k_base",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.wider_openai_window_service.GPTTurboWindowService", args={}
        ),
        max_sequence_length=4000,
        max_request_length=4001,
    ),
    ModelDeployment(
        name="openai/gpt-3.5-turbo-0613",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="openai/cl100k_base",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.wider_openai_window_service.GPTTurboWindowService", args={}
        ),
        max_sequence_length=4000,
        max_request_length=4001,
    ),
    ModelDeployment(
        name="openai/gpt-3.5-turbo-16k-0613",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="openai/cl100k_base",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.wider_openai_window_service.GPTTurbo16KWindowService", args={}
        ),
        max_sequence_length=16000,
        max_request_length=16001,
    ),
    ModelDeployment(
        name="openai/text-similarity-davinci-001",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/text-similarity-curie-001",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/text-similarity-babbage-001",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/text-similarity-ada-001",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="openai/text-embedding-ada-002",
        client_spec=ClientSpec(class_name="helm.proxy.clients.openai_client.OpenAIClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/gpt-jt-6b-v1",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-j-6B",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptj_window_service.GPTJWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/gpt-neoxt-chat-base-20b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/redpajama-incite-base-3b-v1",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/redpajama-incite-instruct-3b-v1",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/redpajama-incite-base-7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/redpajama-incite-instruct-7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="together/glm",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="TsinghuaKEG/ice",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.ice_window_service.ICEWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="writer/palmyra-base",
        client_spec=ClientSpec(class_name="helm.proxy.clients.palmyra_client.PalmyraClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.palmyra_window_service.PalmyraWindowService", args={}
        ),
        max_sequence_length=2048,
        max_sequence_and_generated_tokens_length=2048,
    ),
    ModelDeployment(
        name="writer/palmyra-large",
        client_spec=ClientSpec(class_name="helm.proxy.clients.palmyra_client.PalmyraClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.palmyra_window_service.PalmyraWindowService", args={}
        ),
        max_sequence_length=2048,
        max_sequence_and_generated_tokens_length=2048,
    ),
    ModelDeployment(
        name="writer/palmyra-instruct-30",
        client_spec=ClientSpec(class_name="helm.proxy.clients.palmyra_client.PalmyraClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.palmyra_window_service.PalmyraWindowService", args={}
        ),
        max_sequence_length=2048,
        max_sequence_and_generated_tokens_length=2048,
    ),
    ModelDeployment(
        name="writer/palmyra-e",
        client_spec=ClientSpec(class_name="helm.proxy.clients.palmyra_client.PalmyraClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.palmyra_window_service.PalmyraWindowService", args={}
        ),
        max_sequence_length=2048,
        max_sequence_and_generated_tokens_length=2048,
    ),
    ModelDeployment(
        name="writer/silk-road",
        client_spec=ClientSpec(class_name="helm.proxy.clients.palmyra_client.PalmyraClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.palmyra_window_service.LongerPalmyraWindowService", args={}
        ),
        max_sequence_length=8192,
        max_sequence_and_generated_tokens_length=8192,
    ),
    ModelDeployment(
        name="writer/palmyra-x",
        client_spec=ClientSpec(class_name="helm.proxy.clients.palmyra_client.PalmyraClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.palmyra_window_service.LongerPalmyraWindowService", args={}
        ),
        max_sequence_length=8192,
        max_sequence_and_generated_tokens_length=8192,
    ),
    ModelDeployment(
        name="together/yalm",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="Yandex/yalm",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.yalm_window_service.YaLMWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="google/palm",
        client_spec=ClientSpec(class_name="helm.proxy.clients.google_client.GoogleClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="nvidia/megatron-gpt2",
        client_spec=ClientSpec(class_name="helm.proxy.clients.megatron_client.MegatronClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.megatron_window_service.MegatronWindowService", args={}
        ),
        max_sequence_length=1024,
    ),
    ModelDeployment(
        name="databricks/dolly-v2-3b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="databricks/dolly-v2-7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="databricks/dolly-v2-12b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.GPTNeoXWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
    ModelDeployment(
        name="stabilityai/stablelm-base-alpha-3b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.StableLMAlphaWindowService", args={}
        ),
        max_sequence_length=4096,
        max_request_length=4097,
    ),
    ModelDeployment(
        name="stabilityai/stablelm-base-alpha-7b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.together_client.TogetherClient", args={}),
        tokenizer_name="EleutherAI/gpt-neox-20b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.gptneox_window_service.StableLMAlphaWindowService", args={}
        ),
        max_sequence_length=4096,
        max_request_length=4097,
    ),
    ModelDeployment(
        name="HuggingFaceM4/idefics-9b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.vision_language.idefics_client.IDEFICSClient", args={}),
        tokenizer_name="HuggingFaceM4/idefics-9b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.huggingface_window_service.HuggingFaceWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="HuggingFaceM4/idefics-9b-instruct",
        client_spec=ClientSpec(class_name="helm.proxy.clients.vision_language.idefics_client.IDEFICSClient", args={}),
        tokenizer_name="HuggingFaceM4/idefics-9b-instruct",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.huggingface_window_service.HuggingFaceWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="HuggingFaceM4/idefics-80b",
        client_spec=ClientSpec(class_name="helm.proxy.clients.vision_language.idefics_client.IDEFICSClient", args={}),
        tokenizer_name="HuggingFaceM4/idefics-80b",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.huggingface_window_service.HuggingFaceWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="HuggingFaceM4/idefics-80b-instruct",
        client_spec=ClientSpec(class_name="helm.proxy.clients.vision_language.idefics_client.IDEFICSClient", args={}),
        tokenizer_name="HuggingFaceM4/idefics-80b-instruct",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.huggingface_window_service.HuggingFaceWindowService", args={}
        ),
        max_sequence_length=2048,
    ),
    ModelDeployment(
        name="simple/model1",
        client_spec=ClientSpec(class_name="helm.proxy.clients.simple_client.SimpleClient", args={}),
        tokenizer_name="huggingface/gpt2",
        window_service_spec=WindowServiceSpec(
            class_name="helm.benchmark.window_services.openai_window_service.OpenAIWindowService", args={}
        ),
        max_sequence_length=2048,
        max_request_length=2049,
    ),
]


_INT_MAX: int = 2**31 - 1


def _full_class_name(obj: Any) -> str:
    return f"{obj.__class__.__module__}.{obj.__class__.__name__}"


def test_all_models_have_window_services():
    auto_client = AutoClient(defaultdict(str), "", "")
    model_deployments = {model_deployment.name: model_deployment for model_deployment in _BUILT_IN_MODEL_DEPLOYMENTS}
    tokenizer_configs = {tokenizer_config.name: tokenizer_config for tokenizer_config in _BUILT_IN_TOKENIZER_CONFIGS}
    with TemporaryDirectory() as tmpdir:
        tokenizer_service = get_tokenizer_service(tmpdir)
        for model in ALL_MODELS:
            # Can't test lit-gpt client because it requires manual dependencies
            if "lit-gpt" in model.name:
                continue

            client = auto_client._get_client(model.name)
            window_service = WindowServiceFactory.get_window_service(model.name, tokenizer_service)
            tokenizer_name = window_service.tokenizer_name
            tokenizer = auto_client._get_tokenizer(tokenizer_name)

            client_class_name = _full_class_name(client)
            tokenizer_class_name = _full_class_name(tokenizer)
            window_service_class_name = _full_class_name(window_service)

            prefix_token = window_service.prefix_token
            end_of_text_token = window_service.end_of_text_token

            max_sequence_length = window_service.max_sequence_length
            max_request_length = (
                window_service.max_request_length
                if window_service.max_request_length != window_service.max_sequence_length
                else None
            )
            max_sequence_and_generated_tokens_length = (
                window_service.max_sequence_and_generated_tokens_length
                if window_service.max_sequence_and_generated_tokens_length != _INT_MAX
                else None
            )

            model_deployment = ModelDeployment(
                name=model.name,
                client_spec=ClientSpec(class_name=client_class_name),
                tokenizer_name=tokenizer_name,
                window_service_spec=WindowServiceSpec(class_name=window_service_class_name),
                max_sequence_length=max_sequence_length,
                max_request_length=max_request_length,
                max_sequence_and_generated_tokens_length=max_sequence_and_generated_tokens_length,
            )
            tokenizer_config = TokenizerConfig(
                name=tokenizer_name,
                tokenizer_spec=TokenizerSpec(class_name=tokenizer_class_name),
                end_of_text_token=end_of_text_token,
                prefix_token=prefix_token,
            )
            # NOTE: To generate the _BUILT_IN_MODEL_DEPLOYMENT and _BUILT_IN_TOKENIZER_CONFIGS lists above,
            # simply print tokeniezr_config and model_deployment.

            assert model_deployments[model.name] == model_deployment
            # PalmyraWindowService overrides the huggingface/gpt2 tokenizer with different special tokens,
            # so there are currently two tokenizers named huggingface/gpt2
            # TODO: Give PalmyraWindowService's tokenizer a different name e.g. writer/palmyra
            if tokenizer_name != "huggingface/gpt2":
                assert tokenizer_configs[tokenizer_name] == tokenizer_config
