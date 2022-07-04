import os
from glob import glob
from pathlib import Path
from pdf2image import convert_from_path  # install

pdf_path = Path(glob("./temp_CharSheet*pdf")[0])
out_path = Path("../1_Mechanics/PremadeCharacters/")

roles = ["Defender", "Caster", "Support", "Martial"]  # Roles in order
level_max = 3


def split_pdf(dry_run=True, roles=roles, level_max=level_max):
    """
    Splits PDF for premade characters into individual pngs
    Built to accomodate additional levels

    :param dry_run: If true (default), just prints filename to std out
    :param roles: roles in order as they appear in pdf
    :param level_max: maximum level in pdf for each role
    """
    role_idx = 0  # Initialize which role
    level = 0  # Initialize which level for role
    pages = convert_from_path(pdf_path, 500)
    for num, page in enumerate(pages):
        level = num % 3 + 1
        file_name = "Premade_" + roles[role_idx] + "_Level" + str(level) + ".png"
        print(file_name)
        if not dry_run:
            page.save(out_path / file_name, "PNG")
        if level == level_max:
            role_idx += 1


split_pdf()
