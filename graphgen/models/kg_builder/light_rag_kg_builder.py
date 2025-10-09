import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

from graphgen.bases import BaseGraphStorage, BaseKGBuilder, BaseLLMClient, Chunk
from graphgen.templates import KG_EXTRACTION_PROMPT
from graphgen.utils import (
    detect_if_chinese,
    handle_single_entity_extraction,
    handle_single_relationship_extraction,
    logger,
    pack_history_conversations,
    split_string_by_multi_markers,
)


@dataclass
class LightRAGKGBuilder(BaseKGBuilder):
    llm_client: BaseLLMClient = None
    max_loop: int = 3

    async def extract(
        self, chunk: Chunk
    ) -> Tuple[Dict[str, List[dict]], Dict[Tuple[str, str], List[dict]]]:
        """
        Extract entities and relationships from a single chunk using the LLM client.
        :param chunk
        :return: (nodes_data, edges_data)
        """
        chunk_id = chunk.id
        content = chunk.content

        # step 1: language_detection
        language = "Chinese" if detect_if_chinese(content) else "English"
        KG_EXTRACTION_PROMPT["FORMAT"]["language"] = language

        hint_prompt = KG_EXTRACTION_PROMPT[language]["TEMPLATE"].format(
            **KG_EXTRACTION_PROMPT["FORMAT"], input_text=content
        )

        # step 2: initial glean
        final_result = await self.llm_client.generate_answer(hint_prompt)
        logger.debug("First extraction result: %s", final_result)

        # step3: iterative refinement
        history = pack_history_conversations(hint_prompt, final_result)
        for loop_idx in range(self.max_loop):
            if_loop_result = await self.llm_client.generate_answer(
                text=KG_EXTRACTION_PROMPT[language]["IF_LOOP"], history=history
            )
            if_loop_result = if_loop_result.strip().strip('"').strip("'").lower()
            if if_loop_result != "yes":
                break

            glean_result = await self.llm_client.generate_answer(
                text=KG_EXTRACTION_PROMPT[language]["CONTINUE"], history=history
            )
            logger.debug("Loop %s glean: %s", loop_idx + 1, glean_result)

            history += pack_history_conversations(
                KG_EXTRACTION_PROMPT[language]["CONTINUE"], glean_result
            )
            final_result += glean_result

        # step 4: parse the final result
        records = split_string_by_multi_markers(
            final_result,
            [
                KG_EXTRACTION_PROMPT["FORMAT"]["record_delimiter"],
                KG_EXTRACTION_PROMPT["FORMAT"]["completion_delimiter"],
            ],
        )

        nodes = defaultdict(list)
        edges = defaultdict(list)

        for record in records:
            match = re.search(r"\((.*)\)", record)
            if not match:
                continue
            inner = match.group(1)

            attributes = split_string_by_multi_markers(
                inner, [KG_EXTRACTION_PROMPT["FORMAT"]["tuple_delimiter"]]
            )

            entity = await handle_single_entity_extraction(attributes, chunk_id)
            if entity is not None:
                nodes[entity["entity_name"]].append(entity)
                continue

            relation = await handle_single_relationship_extraction(attributes, chunk_id)
            if relation is not None:
                key = (relation["src_id"], relation["tgt_id"])
                edges[key].append(relation)

        return dict(nodes), dict(edges)

    async def merge_nodes(
        self,
        entity_name: str,
        node_data: Dict[str, List[dict]],
        kg_instance: BaseGraphStorage,
    ) -> BaseGraphStorage:
        pass

    async def merge_edges(
        self,
        edges_data: Dict[Tuple[str, str], List[dict]],
        kg_instance: BaseGraphStorage,
    ) -> BaseGraphStorage:
        pass

    # async def process_single_node(entity_name: str, node_data: list[dict]):
    #     entity_types = []
    #     source_ids = []
    #     descriptions = []
    #
    #     node = await kg_instance.get_node(entity_name)
    #     if node is not None:
    #         entity_types.append(node["entity_type"])
    #         source_ids.extend(
    #             split_string_by_multi_markers(node["source_id"], ["<SEP>"])
    #         )
    #         descriptions.append(node["description"])
    #
    #     # 统计当前节点数据和已有节点数据的entity_type出现次数，取出现次数最多的entity_type
    #     entity_type = sorted(
    #         Counter([dp["entity_type"] for dp in node_data] + entity_types).items(),
    #         key=lambda x: x[1],
    #         reverse=True,
    #     )[0][0]
    #
    #     description = "<SEP>".join(
    #         sorted(set([dp["description"] for dp in node_data] + descriptions))
    #     )
    #     description = await _handle_kg_summary(
    #         entity_name, description, llm_client, tokenizer_instance
    #     )
    #
    #     source_id = "<SEP>".join(
    #         set([dp["source_id"] for dp in node_data] + source_ids)
    #     )
    #
    #     node_data = {
    #         "entity_type": entity_type,
    #         "description": description,
    #         "source_id": source_id,
    #     }
    #     await kg_instance.upsert_node(entity_name, node_data=node_data)
    #     node_data["entity_name"] = entity_name
    #     return node_data
