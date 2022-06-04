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
writing = ["md", "dot", "png", "csv", "svg"]  #         # list of options
add_dependencies = []  # , "Skill", "Level", "Role"]  # # list of options
add_loners = False  #                                   # Include items without links?
out_delim = "\t"  #                                     # delimiter for csv

if any(x in writing for x in ["dot", "png", "svg"]):
    import pydot
import csv, yaml, logging, os, pathlib


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
    comparator = ["<", ">", "≤", "≥"]
    label = ""
    if b is not None:
        if any(comp in b for comp in comparator):
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
    """Return string with 3 spaces per indent, plus '- '"""
    spaces = indents * "   "
    return f"{spaces}- {value}\n"


def make_link(value, indents=0):
    """For md table of contents, add brackets, parens and remove spaces"""
    no_spaces = value.replace(" ", "-")
    link = f"[{value}](#{no_spaces})"
    return make_bullet(link, indents)


def make_entries(input_items, input_yml="04_Powers.yml"):
    """Turn each input item into bulleted list with key prefix"""
    data = load_source(input_yml)
    entries = ""
    for item in input_items:
        entries += make_bullet(f"Name: {item}")
        for k, v in data[item].items():
            indent = 1
            if isinstance(v, list):
                if k == "Mechanic":  # when mechanics are list, want indenting after 1st
                    mech_bullets = f"{v[0]}\n"
                    for mech_bullet in v[1:]:
                        mech_bullets += make_bullet(mech_bullet, 2)
                    v = mech_bullets[:-1]  # remove last space
                else:
                    v = [str(item) for item in v]
                    v = " or ".join(v)
            if "Cost" in k:  # additional indenting for cost items
                indent = 2
            if v == "None":  # Explicit YAML None is empty in md
                v = " "
            if not "egory" in k:  # drop sub/category items
                entries += make_bullet(f"{k}: {v}", indent)
        entries += "\n"
    return entries


def yaml_to_md(input_yml="04_Powers.yml", out_md="temp.md"):
    """Generate markdown from yaml"""
    data = load_source(input_yml)
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

    file_title = pathlib.Path(input_yml).stem.split("_")[-1]

    with open(out_md, "w", newline="") as f:
        f.write(
            f"# {file_title}\n\n<!-- DEVELOPERS: Please edit corresponding yaml in "
            + "3_Automation -->\n\n<!-- MarkdownTOC -->\n"
        )  # md Title
        TOC = ""  # Table of contents
        for k, v in categories.items():
            TOC += make_link(k)
            for sub in v:
                if sub and sub != "None":
                    TOC += make_link(sub, 1)  # indent subcategories
        TOC += "<!-- /MarkdownTOC -->\n\n"
        body = ""
        for cat, sublist in categories.items():  # for each sub/category, load entries
            body += f"## {cat}\n\n"
            if "None" in sublist:
                sublist.remove("None")
                sublist = ["None"] + list(sublist)
            for sub in sublist:
                if sub == "None":
                    body += make_entries(cat_items[f"{cat}_None"], input_yml=input_yml)
                elif sub and sub != "None":
                    body += f"### {sub}\n\n"
                    body += make_entries(cat_items[f"{cat}_{sub}"], input_yml=input_yml)

        f.write(TOC + body)


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
    # logging
    logging.basicConfig(
        level=os.environ.get(
            "LOG_LEVEL", "info"
        ).upper(),  # debug, info, warning, error, critical
        format="[%(asctime)s][%(funcName)-8s][%(levelname)-8s]: %(message)s",
        datefmt="%H:%M:%S",
    )
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
            graph.write_png(out_png, prog="dot.exe")
            logging.info("Wrote png")
        if "svg" in writing:
            graph.write_svg(out_svg)
            logging.info("Wrote svg")

    if "md" in writing:
        yaml_to_md(input_yml=input_file, out_md=out_md)
        logging.info("Wrote md")

    if not writing:  # if no extensions
        logging.warning("Did nothing")


try:
    input_file
except NameError:
    input_file = "04_Powers.yml"

for input_file in input_files:
    main(writing, input_file, out_delim)
