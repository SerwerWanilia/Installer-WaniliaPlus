import os

import rich.progress as prog
from requests import get
from rich.progress import Progress

from modules.helpers import error, url_to_filename
from modules.web_requests import check_status_code


def download_forge(forge_download_url, console):
    response = get(forge_download_url, stream=True)
    check_status_code(response.status_code)
    total_bytes = int(response.headers.get("content-length", 0))
    if total_bytes == 0:
        error("Błąd: Brak nagłówka content-length")

    block_size = 8192
    with Progress(prog.BarColumn(style="white", finished_style="green", complete_style="green"),
                  prog.TaskProgressColumn(), "|", prog.DownloadColumn(), "|", prog.TransferSpeedColumn(),
                  console=console) as progress_bar:
        download_task = progress_bar.add_task(
            description="Pobieranie...", total=total_bytes)

        name = url_to_filename(forge_download_url)
        with open("./" + name, "wb") as forge_file:
            for data in response.iter_content(block_size):
                progress_bar.update(download_task, advance=len(data))
                forge_file.write(data)


def install_forge(forge_download_url):
    name = url_to_filename(forge_download_url)
    if not os.path.isfile(name):
        error("Błąd: Forge nie został pobrany poprawnie.")
    os.system(f"java -jar {name}")
    os.remove(name)


def download_mods(modlist, console):
    mod_count = len(modlist)
    mods_downloaded = 0
    for mod_url in modlist:
        mod_name = url_to_filename(mod_url)
        mods_downloaded += 1
        print(
            f"Pobieranie: {mod_name} ({str(mods_downloaded)}/{str(mod_count)}):")
        response = get(mod_url.rstrip(), stream=True)
        check_status_code(response.status_code)
        total_bytes = int(response.headers.get("content-length", 0))
        if total_bytes == 0:
            error("Error: No content-length header")
        block_size = 8192
        with Progress(prog.BarColumn(style="white", finished_style="green", complete_style="green"),
                      prog.TaskProgressColumn(), "|", prog.DownloadColumn(), "|", prog.TransferSpeedColumn(),
                      console=console) as progress_bar:
            download_task = progress_bar.add_task(
                description="Pobieranie...", total=total_bytes)
            with open("./mods/" + mod_name, "wb") as mod_file:
                for data in response.iter_content(block_size):
                    progress_bar.update(download_task, advance=len(data))
                    mod_file.write(data)
