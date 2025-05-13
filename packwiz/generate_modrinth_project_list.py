#!/usr/bin/python3

import requests
from functools import cache
from py_markdown_table.markdown_table import markdown_table # pip install py-markdown-table

BASE_MODRINTH_API_URL = "https://api.modrinth.com/v2"
BASE_MODRINTH_WEBSITE_URL = "https://modrinth.com"
CLIENT_PLUS_ID = "zuiderschemer"
OUTPUT_FILE = "modrinth_project_list.md"

CHECKMARK_ICON = "✅"
CROSSMARK_ICON = "❌"

@cache
def get_request_json(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data from {url} ({response.status_code})")

@cache
def get_project_game_versions(project_id):
    url = f"{BASE_MODRINTH_API_URL}/project/{project_id}"
    return get_request_json(url)["game_versions"]

@cache
def get_project_versions(project_id):
    url = f"{BASE_MODRINTH_API_URL}/project/{project_id}/version"
    return get_request_json(url)

@cache
def get_newest_version_for_each_game_version():
    project_game_versions = get_project_game_versions(CLIENT_PLUS_ID)
    project_versions = get_project_versions(CLIENT_PLUS_ID)
    processed_game_versions = {}
    for project_version in project_versions:
        version_game_versions = project_version["game_versions"]
        if not set(version_game_versions).issubset(processed_game_versions): # does version_game_versions contain elements of processed_game_versions?
            for version_game_version in version_game_versions:
                processed_game_versions[version_game_version] = project_version["id"]
        if sorted(project_game_versions) == sorted(list(processed_game_versions.keys())): # check if all game versions are processed
            break
    return processed_game_versions

@cache
def get_dependencies_for_version(version_id):
    url = f"{BASE_MODRINTH_API_URL}/version/{version_id}"
    return get_request_json(url)["dependencies"]

@cache
def get_project_name(project_id):
    url = f"{BASE_MODRINTH_API_URL}/project/{project_id}"
    return get_request_json(url)["title"]

@cache
def get_project_markdown_link(project_id):
    url = f"{BASE_MODRINTH_WEBSITE_URL}/project/{project_id}"
    markdown_link = f"[{get_project_name(project_id)}]({url})" # markdown format: [Link Name](https://link-url.com)
    return markdown_link

@cache
def get_project_dict():
    project_dict = {}
    newest_version_for_each_game_version = get_newest_version_for_each_game_version()
    for newest_versions_key in newest_version_for_each_game_version: # newest_versions_key is the game version (1.21.1)
        newest_version = newest_version_for_each_game_version[newest_versions_key]
        version_dependencies = get_dependencies_for_version(newest_version)
        for version_dependency in version_dependencies:
            version_dependency_project_id = version_dependency["project_id"]
            if version_dependency_project_id == None: # item is not on Modrinth (VanillaTweaks.zip), so skip it
                continue

            if not version_dependency["dependency_type"] == "embedded": # skip dependencies that are not embedded
                continue

            project_link = get_project_markdown_link(version_dependency_project_id)
            if version_dependency_project_id not in project_dict:
                project_dict[version_dependency_project_id] = {}
            project_dict[version_dependency_project_id]["Name"] = project_link
            project_dict[version_dependency_project_id][newest_versions_key] = CHECKMARK_ICON

    return project_dict

def add_crossmarks_to_project_dict(project_dict):
    newest_version_for_each_game_version = get_newest_version_for_each_game_version()
    for project_id in project_dict:
        for game_version in newest_version_for_each_game_version:
            if game_version not in project_dict[project_id]:
                project_dict[project_id][game_version] = CROSSMARK_ICON
    return project_dict

def project_dict_to_project_list(project_dict):
    project_list = []
    for i in project_dict:
        project_list.append(project_dict[i])
    return project_list

def sort_list_by_name(project_list):
    return sorted(project_list, key=lambda d: d["Name"])

def get_markdown_table_from_project_list(project_list):
    project_list = sort_list_by_name(project_list)
    return markdown_table(project_list).set_params(row_sep = "markdown", quote = False).get_markdown()


if __name__ == "__main__":
    project_dict = add_crossmarks_to_project_dict(get_project_dict())
    project_list = project_dict_to_project_list(project_dict)
    markdown_table = get_markdown_table_from_project_list(project_list)
    print(markdown_table)
    with open(OUTPUT_FILE, "w") as f:
        f.write(markdown_table)
    print(f"Wrote list to {OUTPUT_FILE}")
