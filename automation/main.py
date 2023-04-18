from glob import glob
from pathlib import Path

from .pdf.split_premades import split_pdf  # requires pdf2image package
from .templates.main import yaml_to_other  # if writing dot, requires pydot package


def main():
    split_pdf(  # Reading PDFs is slow. Comment out if not using
        dry_run=True,
        roles=["Defender", "Caster", "Support", "Martial"],
        level_max=3,
        pdf_path=Path(glob("./automation/_input/*PremadeSheet*pdf")[0]),
        out_folder=Path("./docs/src/1_Mechanics/PremadeCharacters/"),
    )

    yaml_to_other(
        input_files=[
            "04_Powers.yaml",
            "05_Vulnerabilities.yaml",
            "06_Bestiary.yaml",
            "07_Items.yaml",
        ],
        writing=["md", "csv", "png"],
        out_delim="\t",  # or ',' # for csv
    )


if __name__ == "__main__":
    main()
