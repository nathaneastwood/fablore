<a name="readme-top"></a>

# Data

This folder contains the data of the characters and locations of Rathe.

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>

## Characters

The characters file highlights the character's "type" (e.g. NPC or Hero); species; status (e.g. whether they are alive or dead); and the sections of the Main Story they are mentioned in.

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>

## Locations

The locations file highlights the location's region; any special notes; and any sections of the Main Story they are mentioned in.

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>

## Editing the Data

Any edits to the data should be made in the `.csv` file as opposed to the `.md` file. Instructions on how to create the `.md` file can be found [here](#creating-the-md-files).

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>

## Creating the .md Files

You can use the Python code found in `create_md.py`. To use this file, you will need to

```bash
pip install numpy
pip install pandas
pip install py-markdown-table
```

Then you can run the file from the command line to create both `.md` files.

```bash
python3 src/data/create_md.py
```

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>
