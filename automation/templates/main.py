from ..utils.logger import logger
from .bestiary import Bestiary
from .items import Items
from .powers import Powers


def yaml_to_other(
    input_files: list = [
        "04_Powers.yaml",
        "05_Vulnerabilities.yaml",
        "06_Bestiary.yaml",
        # "07_Items.yaml",
    ],
    writing: list = ["md", "csv", "png"],
    out_delim: str = "\t",  # or ','
):
    """Execute all write functions based on inputs at top of script

    Args:
        input_files (list, optional): Local relative paths.
            If len=2, also make combined csv
        writing (list, optional): List of output formats.
        out_delim (str, optional): CSV delimiter - `\t` or `,`
    """
    for file in input_files:
        logger.info(f"Started {file}")

        if "best" in file.lower() or "pc" in file.lower():
            my_class = Bestiary(file)
            if "png" in writing:
                for pc in my_class.categories.get(("PC",), []):
                    my_class.as_dict[pc].make_pc_img()
        elif "power" in file.lower() or "vuln" in file.lower():
            my_class = Powers(file)
        elif "item" in file.lower():
            my_class = Items(file)
        else:
            raise ValueError("Could not infer ingestion routine by file name.")

        if "md" in writing:
            my_class.write_md(output_fp=None, TOC=False)
        if "csv" in writing:
            my_class.write_csv(delimiter=out_delim)
    if "04_Powers.yaml" in input_files and "05_Vulnerabilities.yaml" in input_files:
        Powers(input_files=["04_Powers.yaml", "05_Vulnerabilities.yaml"]).write_csv()


if __name__ == "__main__":
    yaml_to_other()
