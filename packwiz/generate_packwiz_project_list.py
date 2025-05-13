#!/usr/bin/python3

#
# min. python version: 3.11
#

import os
import tomllib # python >= 3.11
from py_markdown_table.markdown_table import markdown_table # pip install py-markdown-table


PROJECT_LIST_FILENAME = "packwiz_project_list.md"
ROOT_DIR = "."
MC_PREFIX = "mc"
PACKWIZ_SUFFIX = ".pw.toml"
SUPPORTED_MC_VERSIONS = ["1.21.5"]

checkmark_icon = "✅"
x_icon = "❌"
project_dict = {}
project_list = []

def update_toml_data(root, category, mc_version):
    for root, dirs, files in os.walk(root):
        for filename in files:
            if filename.endswith(PACKWIZ_SUFFIX):
                filepath = os.path.join(root, filename)
                with open(filepath, "rb") as filecontent:
                    toml_data = tomllib.load(filecontent)
                    project_name = toml_data["name"]
                    project_id = toml_data["update"]["modrinth"]["mod-id"]
                    project_url = "https://modrinth.com/project/" + project_id
                    project_name_formatted = "[" + project_name + "](" + project_url + ")"

                    if project_name not in project_dict:
                        project_dict[project_name] = {}
                    
                    project_dict[project_name]["Name"] = project_name_formatted

                    for supported_mc_version in SUPPORTED_MC_VERSIONS:
                        if mc_version == supported_mc_version:
                            project_dict[project_name][mc_version] = checkmark_icon

                        if not supported_mc_version in project_dict[project_name]:
                            project_dict[project_name][supported_mc_version] = x_icon

def convert_dict_to_list():
    global project_list
    for i in project_dict:
        project_list.append(project_dict[i])
    
    project_list = sorted(project_list, key=lambda d: d["Name"])

def generate_project_list():
    for currentdir, rootdirs, rootfiles in os.walk("."):
        for rootdir in rootdirs:
            if rootdir.startswith(MC_PREFIX):
                mc_version = rootdir.removeprefix(MC_PREFIX).strip()
            
                for minecraftroot, minecraftdirs, minecraftfiles in os.walk(os.path.join(currentdir, rootdir)):
                    for minecraftdir in minecraftdirs:
                        if minecraftdir in ["mods", "resourcepacks", "shaderpacks"]:
                            toml_root = os.path.join(minecraftroot, minecraftdir)
                            update_toml_data(toml_root, minecraftdir, mc_version)

    convert_dict_to_list()
    return markdown_table(project_list).set_params(row_sep = "markdown", quote = False).get_markdown()

if __name__ == "__main__":
    project_list = generate_project_list()
    with open(PROJECT_LIST_FILENAME, "w") as project_list_file:
        project_list_file.write(project_list)
        
    print("Wrote project list to " + PROJECT_LIST_FILENAME)
