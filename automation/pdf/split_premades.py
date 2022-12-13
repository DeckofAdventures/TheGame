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
):
    """Splits PDF for premades into individual pngs: Premade_{Role}_Level{#}.png

    Args:
        dry_run (bool, optional): If true (default), just logs filename as info.
        roles (list, optional): Roles in order as they appear in pdf.
            Defaults to ["Defender", "Caster", "Support", "Martial"].
        level_max (int, optional): Max levels being split in file. Defaults to 3.
        pdf_path (Path, optional): Input pdf path.
            Defaults to Path(glob("../_input/temp_CharSheet*pdf")[0]).
        out_folder (Path, optional): Output png folder.
            Defaults to Path("../docs/src/1_Mechanics/PremadeCharacters/").
    """
    role_idx = 0  # Initialize which role
    level = 0  # Initialize which level for role
    pages = convert_from_path(pdf_path, 500)
    for num, page in enumerate(pages):
        level = num % 3 + 1
        file_name = "Premade_" + roles[role_idx] + "_Level" + str(level) + ".png"
        logger.info(file_name)
        if not dry_run:
            page.save(out_folder / file_name, "PNG")
        if level == level_max:
            role_idx += 1


if __name__ == "__main__":
    split_pdf()
