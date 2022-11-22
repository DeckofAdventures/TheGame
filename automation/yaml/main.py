from utils.logger import logger
from .powers import Powers
from .markdown import Markdown
from .csv import Csv
from .dot import Dot


def yml_to_other(
    input_files: list = [
        "04_Powers.yaml",
        "05_Vulnerabilities.yaml",
        "06_Bestiary.yaml",
    ],
    writing: list = ["md", "dot", "png", "csv", "svg"],
    dependencies: list = ["Skill"],  # "Skill", "Level", "Role"],
    add_loners: bool = False,
    out_delim: str = "\t",  # or ','
):
    """Execute all write functions based on inputs at top of script

    Args:
        input_files (list, optional): Local relative paths.
            If len=2, also make combined csv
        writing (list, optional): List of output formats.
        dependencies (list, optional): Which dependencies to incldue in dot.
        add_loners (bool, optional): Include loners in dot.
        out_delim (str, optional): CSV delimiter - `\t` or `,`
    """
    for f in input_files:
        logger.info(f"Started {f}")
        if "md" in writing:
            Markdown(f).write()
        if "csv" in writing:
            Csv(f).write(delimiter=out_delim)
        if any(img_out in writing for img_out in ["dot", "png", "svg"]):
            dot = Dot(f, dependencies=dependencies, add_loners=add_loners)
            if "dot" in writing:
                dot.write()
            dot.to_pic(out_format=[i for i in writing if i in ["png", "svg"]])
    if len(input_files) == 2:
        Csv(["04_Powers.yaml", "05_Vulnerabilities.yaml"]).write(
            output_fp="../docs/src/1_Mechanics/04_Powers_Combined.tsv"
        )


if __name__ == "__main__":
    yml_to_other()
