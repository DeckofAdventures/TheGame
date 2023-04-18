from pathlib import Path

# TODO: Validate mechanic composition


def test_md_exists(yaml_data, write_mds):
    _ = write_mds

    for yaml_path in yaml_data:
        assert Path(yaml_path.replace("yaml", "md")).exists()


def test_csv_exists(yaml_data, write_csvs):
    _ = write_csvs

    for yaml_path in yaml_data:
        assert Path(yaml_path.replace("yaml", "tsv")).exists()


def test_split_pdf(split_pdf):
    file_paths = split_pdf
    assert file_paths[-1].name == "Premade_Martial_Level3.png"
