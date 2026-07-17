# Developer Guide

This guide covers navdict internals, extension points, and development setup.

## In this section

- [Directive Plugins](directive-plugins.md): plugin contract and registration
- [Internals](internals.md): lazy resolution, memoization, and lookup behavior
- [Contributing](contributing.md): local setup and quality checks

## Source layout

Core code lives under `src/navdict/`:

- `navdict.py`: core `NavigableDict` implementation and built-in directive handling
- `directive.py`: directive parsing and plugin registry
- `directives.py`: built-in plugin implementations
