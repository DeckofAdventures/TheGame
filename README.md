# Welcome to Deck of Adventures, The Game

This repository establishes the version history of the Deck of Adventures tabletop
roleplaying game. A magical world awaits, where Players come first. In Deck of
Adventures, it’s your turn, your choice.

Deck of Adventures is a collaborative roleplaying system, built with an open source
ethos. To explore the project, please visit our
[website](https://deckofadventures.github.io/TheGame/), which includes both our
[Development Guide](https://deckofadventures.github.io/TheGame/1.0/2_Development/02_Design_Document/)
and [Mechanics Guide](https://deckofadventures.github.io/TheGame/1.0/1_Mechanics/01_PlayerGuide_Full/).

## Join our [Discord server!](https://discord.gg/dk6RfWgPHF)

*If the above link is expired, please
[submit an issue](https://github.com/DeckofAdventures/TheGame/issues/new?assignees=&labels=bug&template=bug_report.md&title=Expired%20Discord%20Link!).*

## Developers

### Getting Started

1. **Issues**. Proposing changes is as easy as [opening an issue](https://github.com/DeckofAdventures/TheGame/issues/new/choose).
2. **Edits**. The development team would welcome a PR that made direct edits to existing
   docs. Be aware that many lists (e.g., Powers, Bestiary, etc.) are managed as `yaml`
   files that can be edited directly and then transformed before or after a PR.
3. **Running Code**. The `environment.yaml` file specifies a
   [Conda](https://docs.conda.io/en/latest/) environment that will allow you to run all
   code and generate documentation. `mkdocs` will allow you to see what the docs site
   looks like before committing by visiting `localhost:8000`

```console
conda env create -f environment.yaml # Generate conda environment
conda activate dofa # Activate the environment
python automation/main.py # Generate md docs
bash docs/docs.sh serve # Generate md docs and deploy site
```

`pre-commit` is used to run a series of checks before accepting a commit, as outlined in
the `.pre-commit-config.yaml`. To turn on this feature within your activated conda
environment, simply run `pre-commit install`.

N.B.: The markdown lint pre-commit check requires ruby. Feel free to disable this item
if you are not familiar with ruby. If used, the following file may be a useful addition
to your markdown lint config: `~/.config/mdl/line_length_88.rb`

```ruby
all
exclude_rule 'MD034'
rule 'MD013', :line_length => 88, :tables => false
rule 'MD007', :indent => 2
```

### VS Code Extensions

The following VS Code extensions have been used to support development...

1. Markdown Lint: Establishes uniformity across docs
    - [Extension](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)
    - [GitHub](https://github.com/DavidAnson/markdownlint).
    - Config: `.markdownlint.yaml`
2. Rewrap: Supports hard wrapping docs to 88 characters, which makes facilitates PR
    review. The default keyboard shortcut is `alt+q` or `option+q`.
    - [Extension](https://marketplace.visualstudio.com/items?itemName=stkb.rewrap)
    - [GitHub](https://github.com/stkb/Rewrap/)
3. CSpell: Allows custom dictionaries on spell-check.
    - [Extension](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)
    - [GitHub](https://github.com/streetsidesoftware/vscode-spell-checker)
    - Config: `.cspell.json`
4. Black Formatter: Supports code uniformity.
    - [Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
    - [GitHub](https://github.com/microsoft/vscode-black-formatter)

The following items may also be helpful in a `.vscode/settings.json` file

```json
{
    "[markdown]" : {
        "editor.rulers": [88],
        "editor.formatOnPaste": true,
        "editor.formatOnSave": false,
        "rewrap.autoWrap.enabled": true,
        "rewrap.wrappingColumn": 88
    },
    "editor.codeActionsOnSave": {
        "source.fixAll.markdownlint":true
    },
    "python.analysis.autoImportCompletions": false,
    "python.formatting.provider": "black",
    "python.defaultInterpreterPath": "/YOUR/LOCAL/PATH",
    "python.formatting.blackArgs": [
        "--line-length=88",
        "--exclude='.env'"
    ],
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.python"
    },
    "notebook.formatOnSave.enabled":true,
}
```

### Code

In addition to game documentation, this repository is home to automation tools that
help us rapidly iterate on designs while keeping user-friendly outputs.

In contributions, please conform to `black` formatting.
