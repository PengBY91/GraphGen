from typing import List

import gradio as gr

from graphgen.bases.base_storage import BaseGraphStorage
from graphgen.bases.datatypes import Chunk
from graphgen.models import OpenAIClient


async def build_mm_kg(
    llm_client: OpenAIClient,
    kg_instance: BaseGraphStorage,
    chunks: List[Chunk],
    progress_bar: gr.Progress = None,
):
    """
    Build multi-modal KG and merge into kg_instance
    :param llm_client: Synthesizer LLM model to extract entities and relationships
    :param kg_instance
    :param chunks
    :param progress_bar: Gradio progress bar to show the progress of the extraction
    :return:
    """

    raise NotImplementedError("Multi-modal KG building is not implemented yet.")
