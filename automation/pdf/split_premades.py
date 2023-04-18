from glob import glob
from pathlib import Path

from pdf2image import convert_from_path  # install

from ..utils.logger import logger


def split_pdf(
    dry_run: bool = True,
    roles: list = ["Defender", "Caster", "Support", "Martial"],
    level_max: int = 3,
    pdf_path: Path = Path(glob("./automation/_input/*PremadeSheet*pdf")[0]),
    out_folder: Path = Path("../docs/src/1_Mechanics/PremadeCharacters/"),
    return_paths: bool = False,
):
    """Splits PDF for premades into individual png files: Premade_{Role}_Level{#}.png

    Args:
        dry_run (bool, optional): If true (default), just logs filename as info.
        roles (list, optional): Roles in order as they appear in pdf.
            Defaults to ["Defender", "Caster", "Support", "Martial"].
        level_max (int, optional): Max levels being split in file. Defaults to 3.
        pdf_path (Path, optional): Input pdf path.
            Defaults to Path(glob("../_input/temp_CharSheet*pdf")[0]).
        out_folder (Path, optional): Output png folder.
            Defaults to Path("../docs/src/1_Mechanics/PremadeCharacters/").
        return_paths (bool): If True, function returns list of output Patlib objects.
            Defaults False.
    """
    role_idx = 0  # Initialize which role
    level = 0  # Initialize which level for role
    pages = convert_from_path(pdf_path, 500)
    output_paths = []
    for num, page in enumerate(pages):
        level = num % 3 + 1
        file_name = "Premade_" + roles[role_idx] + "_Level" + str(level) + ".png"

        logger.info(file_name)

        fp = out_folder / file_name
        output_paths.append(fp)

        if not dry_run:
            page.save(fp, "PNG")
        if level == level_max:
            role_idx += 1

    if return_paths:
        return output_paths
