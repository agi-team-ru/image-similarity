import logging
from typing import Callable, List, Optional, Tuple
from similarities import ClipSimilarity
from PIL.Image import Image

model: Optional[ClipSimilarity] = None

logger = logging.getLogger(__name__)


def find_similar(
    target: Image, get_corpus_images: Callable[[], List[Image]]
) -> List[Tuple[int, float]]:
    global model
    if model == None:
        logger.info("Corpus initialization: started")
        model = ClipSimilarity(
            model_name_or_path="OFA-Sys/chinese-clip-vit-base-patch16"
        )
        model.add_corpus(get_corpus_images())
        logger.info("Corpus initialization: finished")
    res = model.most_similar(target)

    if not res:
        return []

    return [(item["corpus_id"], item["score"]) for item in res[0]]
