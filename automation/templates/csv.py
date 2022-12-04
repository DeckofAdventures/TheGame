import csv

from ..utils.logger import logger
from .powers import Powers


class Csv(Powers):
    """Generate csv for set of powers

    Attributes:
        _fields (list): column headers
    """

    def __init__(self, input_files: list = "04_Powers_SAMPLE.yaml"):
        """Initialize CSV class

        Args:
            input_files (list, optional): List of strings, or just one string. R. Defaults to "04_Powers_SAMPLE.yaml".
        """
        super().__init__(input_files=input_files)
        self._fields = None

    @property
    def fields(self) -> list:
        """Column names for csv. Excludes 'save', hardcoded

        Returns:
            fields (list): list of column headers for CSV"""
        if not self._fields:
            all_fields = self.sort_template(
                self._template
            )  # get field list from template
            all_fields.pop("Save", None)  # remove Save for CSV
            # Flatten embedded fields
            self._fields = ["Name"] + list(self.flatten_embedded(all_fields).keys())
        return self._fields

    def write(self, output_fp: str = None, delimiter: str = "\t", ext: str = None):
        """Write CSV from YAML, default is tab-delimited

        Args:
            output_fp (str): relative filepath. Default none, which means local
                _output subfolder
            delimeter (str): column delimiter. `\t` for tab or `,` for comma. If other,
                must provide extension in ext
            ext (str): file extension if other than `.csv`, `.tsv`. Must include period
        """
        suffix_dict = {"\t": ".tsv", ",": ".csv"}
        if ext and ext not in [".tsv", ".csv", "tsv", "csv"]:
            suffix_dict.update({delimiter: ext})
        if not output_fp:
            output_fp = (
                self.filepath_default_output + self._stem + suffix_dict[delimiter]
            )
        rows = []
        with open(output_fp, "w", newline="") as f_output:
            csv_output = csv.DictWriter(
                f_output,
                fieldnames=self.fields,
                delimiter=delimiter,
            )
            csv_output.writeheader()
            for k, v in self.content.items():
                if v and any(v.values()):
                    v["Name"] = k
                    rows.append(v)
            csv_output.writerows(rows)
        logger.info("Wrote csv")
