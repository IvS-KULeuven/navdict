# User Guide

This guide focuses on using navdict effectively in applications and
configuration workflows.

## In this section

- [Directives](directives.md): how to use directive values in YAML and dicts
- [Aliases](aliases.md): expose alternative names for keys and attributes
- [Recipes](recipes.md): practical usage patterns

## Typical workflow

1. Load data from Python dicts or YAML files.
2. Optionally add a label to control the rich tree root title when printing.
3. Navigate nested values using either key access or dot notation.
4. Use directives for file loading, class instantiation, and environment-based configuration.
5. Use aliases when multiple names should resolve to the same key.

For label usage, see [Getting Started](../getting-started.md).

Important caveat: dot navigation requires string keys at a given dictionary
level. If a level contains a non-string key, attribute access is disabled for
that whole level.
