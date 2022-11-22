from utils.logger import logger
from .powers import Powers


class Markdown(Powers):
    """Generate markdown for set of powers

    Args:
        Powers (powers object): Powers class with relevant attributes

    Attributes:
        category_heirarchy (list): list of tuples.
            [(item, indentation, (categ, subcat, subsub, etc.))]
    """

    def __init__(self, input_files="04_Powers_SAMPLE.yaml"):
        """Initialize powers class

        Args:
            input_files (str, optional): String to local file or list of strings.
                Defaults to "04_Powers_SAMPLE.yaml".

        Arrtibutes:
            _category_hierarchy (list): list of tuples
                e.g., [(item, indent, (categ, subcat, subsub, etc.))]
        """
        super().__init__(input_files=input_files)
        self._category_hierarchy = None

    def make_link(self, value: str, indents: int = 0) -> str:
        """Make relative within-doc bulleted link for TOC. [name](#no-spaces)

        Args:
            value (str): heading name
            indents (int): indent level for heading

        Returns:
            link (str): markdown formatted indented bullet with relative path for
                table of contents. E.g., `    - [Heading name](#heading-name)`
        """
        no_spaces = value.lower().replace(" ", "-")
        link = f"[{value}](#{no_spaces})"
        return self.make_bullet(link, indents)

    def make_header(self, value: str, level: (int) = 0):
        """Return string with level+1 * `#`

        Args:
            value (str): heading content
            level (int): heading level. e.g., `# Zero`, `## One`
        """
        prefix = level * "#"
        return f"\n#{prefix} {value}\n"

    @property
    def category_hierarchy(self):
        """Return list of tuples: [(item, indent, (categ, subcat, subsub, etc.))]"""
        if not self._category_hierarchy:
            categories, indents, category_set, prev_category_tuple = [], [], [], tuple()
            for category_tuple in self.categories:
                for idx, category in enumerate(
                    category_tuple
                ):  # indent level, category
                    prev_category = (  # previous category at same heading level
                        prev_category_tuple[idx]
                        if idx < len(prev_category_tuple)
                        else None
                    )
                    if category != prev_category:  # if new, add
                        categories.append(category)
                        indents.append(idx)
                        # subset of tuple relevant to heading level
                        category_set.append(category_tuple[0 : idx + 1])
                prev_category_tuple = category_tuple
            self._category_hierarchy = list(zip(categories, indents, category_set))
        return self._category_hierarchy

    def md_TOC(self) -> str:
        """Generate markdown Table of Contents with category_heirarchy"""
        TOC = "<!-- MarkdownTOC add_links=True -->\n"
        for (category, indent, _) in self.category_hierarchy:
            TOC += self.make_link(category, indent)
        return TOC + "<!-- /MarkdownTOC -->\n"

    def make_entries(self, category_set: set) -> str:
        """All entries into bulleted lists with key prefixes.

        Args:
            category_set (set): unique set of categories (categ, subcateg)"""
        entries = ""
        for power_name, power in self.by_category(category_set).items():
            power = self.sort_power(power)
            power = {k: power[k] for k in power if k not in ["Category", "Type"]}
            entries += f"\n**{power_name}**\n\n"
            for k, v in power.items():
                entries += self.make_bullet(f"{k}: {self.list_to_or(v)}")
            entries += "\n"
        return entries

    def write(self, output_fp: str = None, TOC: bool = False):
        """Write markdown

        Args:
            output_fp (str, optional): relative path for writing output file. Default
                None meaning save to ../docs/src/1_Mechanics/ path with same file name
            TOC (bool, optional): Write table of contents. Default False
        """
        if not output_fp:
            output_fp = "../docs/src/1_Mechanics/" + self._stem + ".md"
        output = "<!-- DEVELOPERS: Please edit corresponding yaml -->\n\n"
        if TOC:
            output += self.md_TOC()
        for (category, indent, category_set) in self.category_hierarchy:
            output += self.make_header(category, indent)
            output += self.make_entries(category_set)
        with open(output_fp, "w", newline="") as f:
            f.write(output)
        logger.info("Wrote md")
