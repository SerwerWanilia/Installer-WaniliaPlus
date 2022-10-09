from requests import get

from modules.constants import *
from modules.helpers import error, url_to_filename


def get_forge_download_url():
    response = get_response(FORGE_URL)
    forge_download_url = response.text
    return forge_download_url


def fetch_modlist():
    response = get_response(REMOTE_URL)
    modlist = response.text.split("\n")
    modlist = list(filter(None, modlist))
    return modlist


def get_response(url):
    response = get(url)
    check_status_code(response.status_code)
    return response


def check_status_code(status_code):
    if status_code != 200:
        error('Błąd: Wystąpił problem z synchronizacją danych z sieci. Sprawdź połączenie z internetem.')


def installer_update_possible():
    response = get_response(VERSION_URL)
    remote_version = response.text.rstrip()

    if remote_version != VERSION:
        return True
    else:
        return False


def get_forge_remote_version():
    response = get_response(FORGE_URL)
    forge = url_to_filename(response.text).replace('-installer.jar', '')
    forge_version = forge.split('-')[2]
    return forge_version
