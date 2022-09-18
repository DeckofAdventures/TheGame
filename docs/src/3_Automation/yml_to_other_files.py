"""
Takes yml files as input, can generate a series of other files, including
    Markdown - includes table of contents and links
    CSV      - defaults to tab delimited
    dot      - flow char instruction format
    PNG/SVG  - for rendering flow charts
User should specify the variables below, before the first function
    input_file  - what to read
    writing     - list of outputs
    add loners  - include items in flow chart that have no prereqs/children
    out_delim   - csv delimiter
User should also install pydot to generate dot files
User should inspect output in subfolder before moving moving elsewhere
"""

input_files = ["04_Powers.yml", "05_Vulnerabilities.yml"]  # edit this, permits multiple
writing = ["md"]  # , "dot", "png", "csv", "svg"]  #         # list of options
add_dependencies = ["Skill"]  # "Skill", "Level", "Role"]  # # list of options
add_loners = False  #                                   # Include items without links?
out_delim = "\t"  #                                     # delimiter for csv

if any(x in writing for x in ["dot", "png", "svg"]):
    import pydot
from collections import OrderedDict
import csv, yaml, logging, os, pathlib
import logging

# logging
logging.basicConfig(
    level=os.environ.get(
        "LOG_LEVEL", "info"
    ).upper(),  # debug, info, warning, error, critical
    format="[%(asctime)s][%(funcName)-8s][%(levelname)-8s]: %(message)s",
    datefmt="%H:%M:%S",
)


def load_source(input_yml="04_Powers.yml"):
    """Load the yaml file"""
    with open(input_yml, encoding="utf8") as f:
        data = yaml.safe_load(f)
    return data


def write_csv(input_yml="04_Powers.yml", out_csv="temp.tsv", delimiter="\t"):
    """Write CSV from YAML, default is tab-delimited"""
    data = load_source(input_yml)
    rows = []
    with open(out_csv, "w", newline="") as f_output:
        csv_output = csv.DictWriter(
            f_output,
            fieldnames=["Name"] + list(data["Template"].keys()),
            delimiter=delimiter,
        )
        csv_output.writeheader()
        for k, v in data.items():
            if v and any(v.values()):
                v["Name"] = k
                rows.append(v)
        csv_output.writerows(rows)


def quote(s):
    """Return quoted string"""
    if not isinstance(s, str):
        s = str(s)
    return '"{}"'.format(s.replace('"', '\\"'))


def edge_str(a, b=None):
    """Generates a `->` b notation for dot edges"""
    comparators = ["<", ">", "≤", "≥"]
    label = ""
    if b is not None:
        if any(comp in b for comp in comparators):
            b, comparison = b.split(" ", 1)
            label = f' [label="{comparison}"]'
        return f"{quote(b)} -> {quote(a)}{label}"
    else:
        return f"{quote(a)}"


def get_edges(name, children=[]):
    """Generate full set of child->node given children"""
    edges = []
    edges.append(edge_str(name))
    for c in children:
        if isinstance(c, str):
            edges.append(edge_str(name, c))
        elif isinstance(c, dict):
            key = c.keys()[0]
            edges.append(edge_str(name, key))
            edges = edges + get_edges(key, c[key])
    return edges


def dot_template(input_yml, add_dependencies=add_dependencies, loners=[]):
    gen_powers = True if "powers" in input_yml.lower() else False

    dot_frontmatter = """digraph {concentrate=true; splines=curved; compound=true;\n"""
    dot_subgraph_role = (
        "\n/* Roles */\n"
        "\tCaster [shape=box style=filled];\n"
        "\tSupport [shape=box style=filled];\n"
        "\tMartial [shape=box style=filled];\n"
        "\tDefender [shape=box style=filled];\n"
    )
    dot_subgraph_skill = (
        "/* Skill */\n"
        '\tsubgraph cluster_stats { label="Stats/Attributes"\n'
        '\t\tsubgraph cluster_agility{label="Agility" {Finesse Stealth} };\n'
        '\t\tsubgraph cluster_Conviction{label="Conviction" {Bluffing Performance} };\n'
        '\t\tsubgraph cluster_Intuition{label="Intuition" {Detection Craft} };\n'
        '\t\tsubgraph cluster_Intelligence{label="Intelligence"'
        "{Knowledge Investigation} };\n"
        '\t\tsubgraph cluster_Strength{label="Strength"  {Athletics Brute} };\n'
        '\t\tsubgraph cluster_Vitality{label="Vitality" {Vitality [style = invis]} };'
        "\n\t}\n\n"
    )
    dot_subgraph_level = (
        "/* Level */\n"
        '\tsubgraph cluster_levels { label="Levels";\n'
        "\tLevel_1 [shape=box style=filled];\n"
        "\tLevel_2 [shape=box style=filled];\n"
        "\tLevel_3 [shape=box style=filled];\n"
        "\tLevel_4 [shape=box style=filled];}\n\n"
    )
    dot_subgraph_loners = (
        "/* Loners */\n" '\tsubgraph cluster_levels {label="No Prerequisites";\n\t%s}\n'
    )
    if gen_powers:
        if "Role" in add_dependencies:
            dot_frontmatter += dot_subgraph_role
        if "Skill" in add_dependencies:
            dot_frontmatter += dot_subgraph_skill
        if "Level" in add_dependencies:
            dot_frontmatter += dot_subgraph_level
    if add_loners:
        dot_frontmatter += dot_subgraph_loners % ";\n\t".join(loners)
    return dot_frontmatter + "\n/* Linked */\n\t" + "%s\n}"


def yaml_to_dot(
    input_yml="04_Powers.md", out_dot="temp.dot", add_dependencies=["Role"]
):
    edges = []
    loners = []
    prereq_strings = ["Prereq Power"]
    if add_dependencies:
        prereq_strings += [f"Prereq {dep}" for dep in add_dependencies]
    for node, vals in load_source(input_yml).items():
        if node != "Template" and vals:  # ignore first template row
            if "Prereq Level" in vals.keys():
                vals["Prereq Level"] = f"Level_{vals['Prereq Level']}"
            prereqs = {k: vals[k] for k in vals.keys() if k in prereq_strings}
            logging.debug(
                "Prereqs: ", {k: vals[k] for k in vals.keys() if k in prereq_strings}
            )
            children = []
            for sublist in prereqs.values():
                if not isinstance(sublist, list):
                    sublist = [sublist]
                children.extend(sublist)
            if children:
                edges += get_edges(node, children)
                try:
                    loners.remove(get_edges(node))
                except ValueError:
                    pass
            elif add_loners:
                loners += get_edges(node)
    dot_string = dot_template(input_yml, add_dependencies, loners) % ";\n\t".join(edges)
    return dot_string


def make_bullet(value, indents=0):
    """Return string with 4 spaces per indent, plus '- '"""
    spaces = indents * "    "
    return f"{spaces}- {value}\n"


def make_link(value, indents=0):
    """For md table of contents, add brackets, parens and remove spaces"""
    no_spaces = value.lower().replace(" ", "-")
    link = f"[{value}](#{no_spaces})"
    return make_bullet(link, indents)


def sort_dict(my_dict, my_list):
    """Sort dict by list of keys. Return OrderedDict"""
    index_map = {v: i for i, v in enumerate(my_list)}
    return OrderedDict(sorted(my_dict.items(), key=lambda pair: index_map[pair[0]]))


def sort_power(power_dict):
    """Given a power, return OrderedDict in markdown read order"""
    if "Prereq" in power_dict:
        power_dict["Prereq"] = sort_dict(
            power_dict["Prereq"], ["Role", "Level", "Skill", "Power"]
        )
    if "Save" in power_dict:
        power_dict["Save"] = sort_dict(
            power_dict["Save"], ["Trigger", "DR", "Type", "Fail", "Succeed"]
        )

    return sort_dict(
        power_dict,
        [
            "Type",
            "Category",
            "Subcategory",
            "XP",
            "PP",
            "Prereq",
            "To Hit",
            "Damage",
            "Range",
            "AOE",
            "Target",
            "Mechanic",
            "Save",
            "Description",
            "Tags",
        ],
    )


def list_to_or(entry):
    """Given string or list, return with joined OR"""
    entry = [entry] if not isinstance(entry, list) else entry
    entry = [str(i) for i in entry]
    return " or ".join(entry)


def save_check_to_txt(save: dict):
    """Given a Save dict, return a sentence"""
    trigger = save["Trigger"] + ", target(s) make a "
    if "DR" in save:
        trigger += "DR " + str(save["DR"]) + " "
    trigger += list_to_or(save["Type"]) + " Save"
    output = [trigger, "On fail, target(s) " + save["Fail"]]
    if "Succeed" in save:
        output.append("On success, target(s) " + save["Succeed"])
    return ". ".join(output)


def merge_mechanics(power):
    """Given power dict, merge all appropriate items into Mechanic"""
    if isinstance(power["Mechanic"], list):  # when mechanics are list, indent after 1st
        mech_bullets = power["Mechanic"][0] + "\n"
        for mech_bullet in power["Mechanic"][1:]:
            mech_bullets += make_bullet(mech_bullet)
        power["Mechanic"] = mech_bullets[:-1]  # remove last space
    if "PP" in power:
        mechanic = "For " + list_to_or(power["PP"]) + " PP, " + power["Mechanic"] + ". "
    else:
        mechanic = power["Mechanic"]
    if "Save" in power:
        mechanic += save_check_to_txt(power["Save"]) + ". "
    return "".join([power["Type"], ". ", mechanic])


def make_entries(input_items, input_yml="04_Powers.yml"):
    """Turn each input item into bulleted list with key prefix. Input list of Powers"""
    data = load_source(input_yml)
    entries = ""
    input_list = input_items if isinstance(input_items, list) else [input_items]
    for item in input_list:  # for power in input list
        power = data[item]
        if "PP" in power:
            pp_list = list_to_or(power["PP"])
            costs = (  # gave extra newline. don't know why. added [:-1]
                "Costs:\n"
                + make_bullet(f"XP: {power['XP']}", 1)
                + make_bullet(f"PP: {pp_list}", 1)
            )[:-1]
        else:
            costs = f"XP Cost: {power['XP']}"
        entries += (
            f"**{item}**\n\n"
            + make_bullet(f"Description: {power['Description']}", 0)
            + make_bullet(f"Mechanic: {merge_mechanics(power)}", 0)
            + make_bullet(costs, 0)
        )
        if "Prereq" in power:
            entries += make_bullet("Prereqs:", 0) + "".join(
                [  # joins all present prereqs
                    make_bullet(f"{k}: {list_to_or(v)}", 1)
                    for k, v in power["Prereq"].items()
                ]
            )
        if "Tags" in power:
            entries += make_bullet(f"Tags: {power['Tags']}")
        entries += "\n"
    return entries


def parse_categories(data):
    """Get set of Categories and Subcategories"""
    categories = dict()  # category: sub pairing
    cat_items = dict()  # concatenated string: [items]
    for k, v in data.items():  # get set of sub/categories for TOC later
        if v and v["Category"]:
            cat = v["Category"]
            sub = v["Subcategory"]
            concat_str = f"{cat}_{sub}"
            if cat not in categories:
                categories[cat] = set(["None"])
                cat_items[f"{cat}_None"] = []
            categories[cat].add(sub)
            if concat_str not in cat_items:
                cat_items[concat_str] = []
            cat_items[f"{cat}_{sub}"] += [k]
    return categories, cat_items


def yaml_to_md(input_yml="04_Powers.yml", out_md="temp.md"):
    """Generate markdown from yaml"""
    data = load_source(input_yml)
    categories, cat_items = parse_categories(data=data)
    file_title = pathlib.Path(input_yml).stem.split("_")[-1]

    with open(out_md, "w", newline="") as f:
        f.write(
            f"""# {file_title}\n
            <!-- DEVELOPERS: Please edit corresponding yaml in 3_Automation -->\n
            """
        )
        body = ""
        for cat, sublist in categories.items():  # for each sub/category, load entries
            body += f"## {cat}\n\n"
            if "None" in sublist:  # Move no subcategory first
                sublist.remove("None")
                sublist = ["None"] + list(sublist)
            for sub in sublist:
                if sub == "None":
                    body += make_entries(cat_items[f"{cat}_None"], input_yml=input_yml)
                elif sub and sub != "None":
                    body += f"### {sub}\n\n"
                    body += make_entries(cat_items[f"{cat}_{sub}"], input_yml=input_yml)

        # f.write(md_TOC(categories=categories)) # Commented out TOC
        f.write(body)


def validate_input(input_file="04_Powers.yml", out_delim="\t"):
    """Check input exists, return all possible versions"""
    assert pathlib.Path(input_file).exists(), f"Couldn't find {input_file}"
    try:
        _ = load_source(input_file)
    except:
        raise FileNotFoundError(f"Couldn't load {input_file}")
    stem = "./_Automated_output/" + os.path.splitext(os.path.basename(input_file))[0]

    x = "t" if out_delim == "\t" else "c"  # Write a 'tsv' if tab, else 'csv'

    return f"{stem}.{x}sv", f"{stem}.dot", f"{stem}.png", f"{stem}.svg", f"{stem}.md"


def main(writing=[], input_file="04_Powers.yml", out_delim="\t"):
    """Decide which generating"""
    logging.info("Strarted")

    # Check input file, string replace to get various extensions
    out_csv, out_dot, out_png, out_svg, out_md = validate_input(input_file, out_delim)

    if "csv" in writing:
        write_csv(input_yml=input_file, out_csv=out_csv, delimiter=out_delim)
        logging.info("Wrote csv")

    if not any(x in writing for x in ["png", "svg"]) and "dot" in writing:
        # if you want pic, make dot
        logging.warning("Adding 'dot' in order to generate picture")
        writing += ["dot"]

    if "dot" in writing:
        dot_string = yaml_to_dot(
            input_yml=input_file, out_dot=out_dot, add_dependencies=add_dependencies
        )
        with open(out_dot, "w", newline="") as f_output:
            f_output.write(dot_string)
        logging.info("Wrote dot")
        graphs = pydot.graph_from_dot_data(dot_string)
        graph = graphs[0]

        if "png" in writing:
            try:
                graph.write_png(out_png, prog="dot.exe")
            except FileNotFoundError:
                graph.write_png(out_png)
            logging.info("Wrote png")
        if "svg" in writing:
            graph.write_svg(out_svg)
            logging.info("Wrote svg")

    if "md" in writing:
        yaml_to_md(input_yml=input_file, out_md=out_md)
        logging.info("Wrote md")

    if not writing:  # if no extensions
        logging.warning("Did nothing")


if __name__ == "__main__":
    for input_file in input_files:
        main(writing, input_file, out_delim)
