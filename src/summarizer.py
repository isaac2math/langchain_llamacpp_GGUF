import os.path
from typing import Optional

from langchain import LlamaCpp
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

from decouple import config
from loguru import logger


class Summarizer:
    N_GPU_LAYERS = config("N_GPU_LAYERS", default=40, cast=int)
    N_BATCH = config("N_BATCH", default=512, cast=int)
    N_THREADS = config("N_THREADS", default=12, cast=int)
    N_CTX = config("N_CTX", default=16000, cast=int)
    DEFAULT_MODEL_DIR = "./model_dir"

    def __init__(self, model_file_name: str, model_dir: Optional[str] = None,
                 skip_inference: bool = False):
        if model_file_name is None:
            raise ValueError("model_file_name cannot be None")

        logger.info("===================Listing dir for model====================")
        print(os.listdir(model_dir))

        self._llm = LlamaCpp(
            model_path=os.path.join(Summarizer.DEFAULT_MODEL_DIR if model_dir is None else model_dir, model_file_name),
            n_threads=Summarizer.N_THREADS,
            n_parts=-1,
            n_gpu_layers=Summarizer.N_GPU_LAYERS,
            n_batch=Summarizer.N_BATCH,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            verbose=True,
            max_tokens=10000,
            n_ctx=Summarizer.N_CTX)
        self._text_splitter = CharacterTextSplitter()
        self._skip_inference = skip_inference

    def summarize(self, raw_text: str) -> str:
        if raw_text is None:
            raise ValueError("raw_text cannot be None")

        if self._skip_inference:
            return raw_text

        texts = self._text_splitter.split_text(raw_text)

        docs = [Document(page_content=t) for t in texts[:3]]
        chain = load_summarize_chain(self._llm, chain_type="refine")
        result = chain.run(docs)

        return result
