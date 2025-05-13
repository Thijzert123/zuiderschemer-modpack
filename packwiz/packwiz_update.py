#!/usr/bin/python3

import functools
import sys
import os
import subprocess
import requests

PACKWIZ_SUFFIX = ".pw.toml" # files that are managed by packwiz

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    END = '\033[0m'

def get_mc_dirs():
    mc_dirs = [] # such as mc1.20.4 or mc1.21.1
    if sys.argv[1] == "all":
        for root, dirnames, filenames in os.walk("."):
            for dirname in dirnames:
                if dirname.startswith("mc"):
                    mc_dirs.append(dirname)
    else:
        for arg in sys.argv[1:]: # skip first entry
            mc_dirs.append("mc" + arg)
    return sorted(mc_dirs)

# remove and clean all mod/shaders/resources managed by packwiz
def remove_managed_files(mc_dirs, debug = False):
    for root, dirnames, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(PACKWIZ_SUFFIX):
                filepath = os.path.join(root, filename)
                mc_version = root.split("/")[1]
                if mc_version in mc_dirs:
                    if debug:
                        print("Removing " + filepath)
                    os.remove(filepath)

@functools.cache
def download_vanilla_tweaks_pack(url):
    return requests.get(url).content

def update_packwiz_instances(debug = False):
    if len(sys.argv) < 2:
        print("Please specify Minecraft version (e.g. 1.21.1) or update all instances with 'all'.")
        exit(1)

    packwiz_output_stream = subprocess.DEVNULL
    if debug:
        packwiz_output_stream = None

    mc_dirs = get_mc_dirs()
    pack_content = eval(open("pack_content.py").read())

    print("Removing files managed by this script...", end="")
    sys.stdout.flush()
    remove_managed_files(mc_dirs, debug)
    print(" done")

    packwiz_instances_refreshed = []

    for content_type in pack_content:
        for project in pack_content[content_type]:
            print()
            print(f"Adding {project["id"]}: ", end="")
            sys.stdout.flush()

            if "include" in project and "exclude" in project:
                print()
                print("Include and exclude specified at the same time. Remove one of these to add this project.")
                continue

            for mc_dir in mc_dirs:
                # Refresh packwiz
                if (mc_dir not in packwiz_instances_refreshed):
                    subprocess.run(["packwiz", "refresh"], cwd=mc_dir, stdout=packwiz_output_stream, stderr=packwiz_output_stream)
                    packwiz_instances_refreshed.append(mc_dir)

                mc_version = mc_dir.replace("mc", "")

                if ("include" in project and mc_version not in project["include"]) and ("exclude" in project and mc_version in project["exclude"]):
                    print(f"{Colors.RED}{mc_version}{Colors.END} ", end="")
                    continue

                command = ["packwiz", "modrinth", "install", "--yes", project["id"]]
                if "force-versions" in project and mc_version in project["force-versions"]:
                    command = ["packwiz", "modrinth", "install", "--yes", "--project-id", project["id"], "--version-id", project["force-versions"][mc_version]]

                returncode = subprocess.run(command, cwd=mc_dir, stdout=packwiz_output_stream, stderr=packwiz_output_stream).returncode
                if returncode == 0:
                    print(f"{Colors.GREEN}{mc_version}{Colors.END} ", end="")
                else:
                    print(f"{Colors.RED}{mc_version}{Colors.END} ", end="")
                sys.stdout.flush()

        print()

if __name__ == "__main__":
    update_packwiz_instances()
