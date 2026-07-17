# Internals

## Data model

`NavigableDict` stores data as dictionary keys while mirroring keys as
attributes for dot navigation.

## Lazy directive resolution

When reading a value by key or attribute, navdict checks whether the stored
value is a directive string and resolves it only on access.

## Memoization

Resolved directive values are memoized per key so repeated access does not
recompute by default.

## Resource location

For file-based directives, navdict resolves paths using source file context
first, then `NAVDICT_DEFAULT_RESOURCE_LOCATION`, then current working
directory.

## Alias hook

When normal lookup fails, an optional alias hook can map an alias to a real
key and retry lookup.
