# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues at [`matx104/AETHERIX`](https://github.com/matx104/AETHERIX/issues). Use the `gh` CLI.

## Conventions

- **Create**: `gh issue create --title "..." --body "..."`.
- **Read**: `gh issue view <number> --comments`.
- **Comment**: `gh issue comment <number> --body "..."`.
- **Labels**: `gh issue edit <number> --add-label "..."`.
- **Close**: `gh issue close <number> --comment "..."`.

## Research-context note

When an issue is about a simulation result or routing benchmark, attach the run config (seed, scenario, RL hyperparameters) in the body. Reproducibility matters for a research artifact.
