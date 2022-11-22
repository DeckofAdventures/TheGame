from glob import glob
from pathlib import Path

from pdf.split_premades import split_pdf  # requires pdf2image package
from templates.main import yml_to_other  # if dot, requires pydot package

split_pdf(  # This function is slow. Comment out if not using
    dry_run=True,
    roles=["Defender", "Caster", "Support", "Martial"],
    level_max=3,
    pdf_path=Path(glob("./_input/*PremadeSheet*pdf")[0]),
    out_folder=Path("../docs/src/1_Mechanics/PremadeCharacters/"),
)

yml_to_other(
    input_files=["04_Powers.yaml", "05_Vulnerabilities.yaml", "06_Bestiary.yaml"],
    writing=["md", "dot", "png", "csv", "svg"],
    dependencies=["Skill"],  # "Skill", "Level", "Role"],
    add_loners=False,
    out_delim="\t",  # or ','
)
