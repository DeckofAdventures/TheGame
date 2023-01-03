# Welcome to Deck of Adventures, The Game

This repository establishes the version history of the Deck of Adventure tabletop
roleplaying game. A magical world awaits, where Players come first. In Deck of
Adventure, it’s your turn, your choice.

Deck of Adventures is a collaborative roleplaying system, built with an open source
ethos. Please visit our
[Development Guide](./docs/src/2_Development/) to learn more about this project. Or
visit our [Mechanics Guide](./docs/src/1_Mechanics/01_PlayerGuide_Full.md) to learn more
about how to play.

## Join our [Discord server!](https://discord.gg/dk6RfWgPHF)

*If the above link is expired, please
[submit an issue](https://github.com/DeckofAdventures/TheGame/issues/new?assignees=&labels=bug&template=bug_report.md&title=Expired%20Discord%20Link!).*

## Developers

### Markdown

While not strictly enforced, we ask that you observe
[Markdown Linting](https://github.com/DavidAnson/markdownlint). The following can be
added to a vscode settings file. The [Rewrap](https://github.com/stkb/Rewrap/) extension
supports wrapping to 88 characters.

```json
{
    "[markdown]" : {
        "editor.rulers": [88],
        "editor.formatOnPaste": true,
        "editor.formatOnSave": true,
        // https://github.com/stkb/Rewrap/
        // Toggle via command prompt per file
        // Default paragraph rewrap key: alt+q or option+q
        "rewrap.autoWrap.enabled": true,
        "rewrap.wrappingColumn": 88
    },
    // https://github.com/DavidAnson/markdownlint
    "editor.codeActionsOnSave": {
        "source.fixAll.markdownlint":true
    },
    "markdownlint.focusMode": 5, // ignore issues around the cursor
}
```

### Code

In addition to game documentation, this repository is home to automation tools that
help us rapidly iterate on designs while keeping user-friendly outputs.

In contributions, please conform to `black` formatting.
