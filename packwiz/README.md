# Packwiz
`packwiz` is used to assemble the modpack. You can find the installation instructions [here](https://packwiz.infra.link/installation).

## Export modpack
In the folder of a Minecraft version, run:
```
packwiz modrinth export
```

## Updating or adding contents of this modpack to another packwiz instance
You can use `packwiz_update.py` to import all the mods, resource packs and shaders to another packwiz instance. Be sure to specify the game version, like `1.21.1` or `1.21.3`, or `all` to update all versions.
```
$ pwd # current working directory
/home/john/git/client-plus/packwiz
$ python3 packwiz_update.py 1.21.1
```

## Generating a project list
There are two different scripts for generating project lists: `generate_modrinth_project_list.py` and `generate_packwiz_project_list.py`. `generate_modrinth_project_list.py` uses the Modrinth API to provide an accurate project list for all projects already updoaded to Modrinth. This is the only list that should be uploaded to the README or Modrinth description. `generate_packwiz_project_list.py` uses the packwiz files to generate the project list with all updated mods. This list is almost never accurate to what users get when downloading from Modrinth, it only shows what mods are for what Minecraft versions if all packs were to be updated RIGHT NOW.

## Dependencies
`py-mardown-table` is used to generate a markdown list ([docs](https://pypi.org/project/py-markdown-table)). To download the dependencies, run `pip install py-markdown-table`.

### Usage
The usage is the same for both scripts: just run it without any command-line arguments and a markdown list will be printed to the terminal. Both scripts will also write the project list to a file.
