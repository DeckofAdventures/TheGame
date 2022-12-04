from .yaml_spec import YamlSpec
from ..utils.logger import logger


class Powers(YamlSpec):
    """Set of DofA powers

    Attributes:
        content (dict): input powers converted to human-readable mechanics
        categories (set): set of tuples - set((categ, subcat, subsubcat),(categ2))
    """

    def __init__(self, input_files="04_Powers_SAMPLE.yaml", limit_types: list = None):
        """Initialize. Load file, establish attributes

        Args:
            input_files (str, optional): String to local file or list of strings.
                Defaults to "04_Powers_SAMPLE.yaml".
            limit_types (list, optional): Only output items of provided types.
                Defaults to None, which means all of the following:
                ["Major", "Minor", "Passive", "Adversary", "House", "Vulny"]

        Attributes:
            _data (dict): raw input data
            _categories (set): all power categories
            _template (dict): Template item from input data
            _content (dict): data restructured to sentences.
            _stem (str): Input file name no extension
            _name (str): Last string of stem when split by `_`
            _limit_types (list): See arg above
        """
        input_files = self.ensure_list(ambiguous_item=input_files)
        super().__init__(
            input_files=[
                file for file in input_files if "Power" in file or "Vuln" in file
            ]
        )
        self._limit_types = limit_types

    def sort_template(self, power_dict):
        """Given a power, return OrderedDict in markdown read order"""
        if "Prereq" in power_dict:
            power_dict["Prereq"] = self.sort_dict(
                power_dict["Prereq"], ["Role", "Level", "Skill", "Power"]
            )
        if "Save" in power_dict:
            power_dict["Save"] = self.sort_dict(
                power_dict["Save"], ["Trigger", "DR", "Type", "Fail", "Succeed"]
            )

        return self.sort_dict(
            power_dict,
            [
                "Type",
                "Category",
                "Description",
                "Mechanic",
                "XP",
                "PP",
                "Prereq",
                "Prereq_Role",
                "Prereq_Level",
                "Prereq_Skill",
                "Prereq_Power",
                "To Hit",
                "Damage",
                "Range",
                "AOE",
                "Target",
                "Save",
                "Tags",
            ],
        )

    def save_check_to_txt(self, save: dict) -> str:
        """Given a Save dict from a power, return a readable sentence

        Args:
            save (dict): subset of power dict, save with trigger, DR, type, etc

        Returns:
            save_string (str): readable sentence detailing all features of a save
        """
        sentence = save["Trigger"] + ", target(s) make a "
        sentence += "DR " + str(save["DR"]) + " " if "DR" in save else ""
        sentence += self.list_to_or(save["Type"]) + " Save"
        output = [sentence, "On fail, target(s) " + save["Fail"]]
        output.append(
            "On success, target(s) " + save["Succeed"]
        ) if "Succeed" in save else None
        return ". ".join(output)

    def merge_mechanics(self, power):
        """Given power dict, merge all appropriate items into Mechanic

        Args:
            power (dict): individual power

        Returns:
            power_merged (dict): power with all mechanic items combined.
        """
        if isinstance(power["Mechanic"], list):  # when mech are list, indent after 1st
            mech_bullets = power["Mechanic"][0] + "\n"
            for mech_bullet in power["Mechanic"][1:]:
                mech_bullets += self.make_bullet(mech_bullet)
            power["Mechanic"] = mech_bullets[:-1]  # remove last space
        mechanic = (
            ("For " + self.list_to_or(power["PP"]) + " PP, " + power["Mechanic"] + ". ")
            if "PP" in power
            else power["Mechanic"]
        )
        if "Save" in power:
            mechanic += self.save_check_to_txt(power["Save"]) + ". "
        power["Mechanic"] = "".join([power["Type"], ". ", mechanic])
        power["Category"] = self.ensure_list(power["Category"])
        power.pop("Save", None)
        return power

    @property
    def content(self) -> dict:
        """Return readable dict with Mechanics collapsed."""
        if not self._content:
            self._content = {
                power: {
                    **self.flatten_embedded(self.merge_mechanics(traits)),
                }
                for (power, traits) in self._raw_data.items()
            }
        return self.filter_dict_by_key(  # Filter by types specified when init class
            dict_content=self._content, key_filter="Type", key_options=self._limit_types
        )

    @property
    def categories(self):
        """Return set of tuples: (categories, subcategories)"""
        if not self._categories:
            for v in self._raw_data.values():  # get set of sub/categories for TOC later
                self._categories.add(tuple(self.ensure_list(v["Category"])))
        return sorted(self._categories)

    def by_category(self, category: list = None):
        """Returns readable dict of powers limited by category, if present

        Args:
            category (list, optional): Ordered list/set of [category, subcategory].
                Defaults to None, meaning no filtering or ordering.

        Returns:
            dict: Subset of readable dict
        """
        return self.filter_dict_by_key(
            dict_content=self.content, key_filter="Category", key_options=category
        )
