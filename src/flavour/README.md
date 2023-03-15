# Flavour Text

This folder contains the individual set files which hold the flavour text printed on that set's cards. When adding new flavour text to these files, please ensure to complete the following steps:

* Extract the flavour text and place it a file named `set-name.md`. If you have the [flesh-and-blood-cards](https://github.com/the-fab-cube/flesh-and-blood-cards) repo cloned, you can use the [`get_flavour.py`](get_flavour.py) file to automatically create this file.
* Add links to the first mention of each unique hero, character or location.
* Add any mentions of new characters, heroes or locations to the [data files](../data).
* Add the flavour text file to the [SUMMARY.md](../SUMMARY.md) file.

The file structure should look like this:

```
## Set Name
#### Card Name - (XXX000)
Flavour text
```

Where `(XXX000)` is the card's unique set identifier.
