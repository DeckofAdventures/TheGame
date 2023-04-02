from ..utils import logger
from .split_premades import split_pdf

__all__ = ["split_pdf"]

logger.warning(
    "This mechanism is depreciated with the addition of Bestiary write_md method and "
    + "will be removed in a future version."
)
