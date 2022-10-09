import os

from modules.constants import FORGE_URL
from modules.helpers import url_to_filename
from modules.web_requests import get_response


def get_missing_mods(remote_mod_urls, local_modlist) -> list:
    mod_urls = []
    for mod_url in remote_mod_urls:
        if url_to_filename(mod_url) not in local_modlist:
            mod_urls.append(mod_url)
    return mod_urls


def forge_is_installed() -> bool:
    response = get_response(FORGE_URL)
    forge = url_to_filename(response.text).replace('-installer.jar', '')
    mc_version = forge.split('-')[1]
    forge_version = forge.split('-')[2]
    jar_name = mc_version + "-forge-" + forge_version + ".jar"
    if 'versions' in os.listdir("./"):
        for profile in os.listdir("./versions/"):
            if os.path.isdir("./versions/" + profile):
                if jar_name in os.listdir("./versions/" + profile):
                    return True
    return False


def mods_already_downloaded(remote_modlist, local_mods) -> list:
    for mod in remote_modlist:
        if mod not in local_mods:
            return False
    return True


def get_local_mods() -> list:
    local_mods = []
    for file in os.listdir("./mods/"):
        if file.endswith(".jar"):
            local_mods.append(file)
    return local_mods


def mod_folder_exists() -> bool:
    if not os.path.exists('mods'):
        return False
    return True


def create_mod_folder() -> None:
    os.makedirs('mods')


def get_incorrect_mods(local_mods, remote_mods) -> list:
    incorrect_mods = []
    for mod in local_mods:
        if mod not in remote_mods:
            incorrect_mods.append(mod)
    return incorrect_mods


def remove_mods(mod_names) -> None:
    for mod_name in mod_names:
        os.remove('./mods/' + mod_name)
