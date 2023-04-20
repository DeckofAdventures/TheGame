from automation.templates.main import yaml_to_other


def main():
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
