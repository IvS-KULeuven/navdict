# navdict

<div class="nd-hero">
    <img
        class="nd-hero__logo nd-hero__logo--light"
        src="images/navdict-lockup-light-bg.svg"
        alt="navdict"
    >
    <img
        class="nd-hero__logo nd-hero__logo--dark"
        src="images/navdict-lockup-dark-bg.svg"
        alt="navdict"
    >
</div>

`navdict` (also available as `NavigableDict` and `NavDict`) is a Python
dictionary subclass that lets you access nested configuration and data using
both dictionary-style access and dot notation.

It is built for configuration-heavy projects where readability and flexibility
matter.

## Why navdict?

You can use `navdict` as a plain dictionary:

```python
setup["gse"]["hexapod"]["ID"]
```

Or navigate the same structure with dot notation:

```python
setup.gse.hexapod.ID
```

In addition, navdict supports directive-based values such as `yaml//...`,
`csv//...`, and `class//...` that are resolved lazily when accessed.
These directives are pluggable so you can add your own directives for your project.
More on directives in [User Guide: Directives](user-guide/directives.md).

## Core concepts

- Nested dictionaries are wrapped as navdict objects.
- Keys are available as both dictionary keys and attributes.
- Directive strings are interpreted on read and memoized.
- Relative resource paths can be resolved from the source file location.

## Example

```python
from navdict import NavDict

setup = NavDict(
    {
        "gse": {
            "hexapod": {
                "ID": 42,
                "calibration": [0, 1, 2, 3, 4, 5],
            }
        }
    }
)

assert setup["gse"]["hexapod"]["ID"] == 42
assert setup.gse.hexapod.ID == 42
```

## Next steps

- Start with [Getting Started](getting-started.md)
- Learn directive behavior in [User Guide: Directives](user-guide/directives.md)
- See alias support in [User Guide: Aliases](user-guide/aliases.md)
- Extend navdict with [Developer Guide: Directive Plugins](developer-guide/directive-plugins.md)
