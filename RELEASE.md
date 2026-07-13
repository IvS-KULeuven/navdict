# Release a new version


- make sure you have run the formatter:`uv run ruff format`
- run the full test suite again: `uv run pytest tests`
- update the version number in the `pyproject.toml` file
- update `CHANGELOG.md` with the changes for this release, moving the `[Unreleased]` entries under
  a new `## [<version>] - <date>` heading
- push everything to GitHub and merge into `main`
- make a new release on GitHub

- remove previous builds: `rm -r dist`
- build the package: `uv build`
- publish the package to PyPI: `uv publish --token $UV_PUBLISH_TOKEN`
- update the documentation and check with `uv run mkdocs serve`
- Publish the updated documentation: `uv run mkdocs gh-deploy -r upstream -m "documentation update on .."`
