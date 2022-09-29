import os
from sys import exit as sys_exit
from rich.progress import Progress
import rich.progress as prog
from rich.console import Console
from rich.theme import Theme
from rich.prompt import Prompt
from requests import get


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def url_to_filename(filename):
    return filename.rstrip().split('/')[-1].replace('%2B', '+')


def url_to_filename_list(url_list):
    filename_list = []
    for item in url_list:
        filename_list.append(url_to_filename(item))
    return filename_list


def error(error_message, is_critical=1):
    print(error_message)

    if is_critical:
        input('Naciśnij enter by zakończyć.')
        sys_exit()


def get_mods_to_download(remote_mod_urls, local_modlist):
    mod_urls = []
    for mod_url in remote_mod_urls:
        if url_to_filename(mod_url) not in local_modlist:
            mod_urls.append(mod_url)
    return mod_urls


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


def forge_is_installed():
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


def get_forge_download_url():
    response = get_response(FORGE_URL)
    forge_download_url = response.text
    return forge_download_url


def install_forge(forge_download_url):
    response = get(forge_download_url, stream=True)
    check_status_code(response.status_code)
    total_bytes = int(response.headers.get("content-length", 0))
    if total_bytes == 0:
        error("Error: No content-length header")

    block_size = 8192
    with Progress(prog.BarColumn(style="white", finished_style="green", complete_style="green"), prog.TaskProgressColumn(), "|", prog.DownloadColumn(), "|", prog.TransferSpeedColumn(), console=console) as progress_bar:
        download_task = progress_bar.add_task(
            description="Pobieranie...", total=total_bytes)

        name = url_to_filename(forge_download_url)
        with open("./" + name, "wb") as forge_file:
            for data in response.iter_content(block_size):
                progress_bar.update(download_task, advance=len(data))
                forge_file.write(data)

    console.print("Instalowanie forge...\n")

    os.system(f"java -jar {name}")
    os.remove(name)


def download_mods(modlist, local_mods):
    mod_count = len(modlist)
    mods_downloaded = 0
    for mod_url in modlist:
        mod_name = url_to_filename(mod_url)
        if mod_name in local_mods:
            continue
        mods_downloaded += 1
        print(
            f"Pobieranie: {mod_name} ({str(mods_downloaded)}/{str(mod_count)}):")
        response = get(mod_url.rstrip(), stream=True)
        check_status_code(response.status_code)
        total_bytes = int(response.headers.get("content-length", 0))
        if total_bytes == 0:
            error("Error: No content-length header")
        block_size = 8192
        with Progress(prog.BarColumn(style="white", finished_style="green", complete_style="green"), prog.TaskProgressColumn(), "|", prog.DownloadColumn(), "|", prog.TransferSpeedColumn(), console=console) as progress_bar:
            download_task = progress_bar.add_task(
                description="Pobieranie...", total=total_bytes)
            with open("./mods/" + mod_name, "wb") as mod_file:
                for data in response.iter_content(block_size):
                    progress_bar.update(download_task, advance=len(data))
                    mod_file.write(data)


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


def mods_already_downloaded(remote_modlist, local_mods):
    for mod in remote_modlist:
        if mod not in local_mods:
            return False
    return True


def get_local_mods():
    local_mods = []
    for file in os.listdir("./mods/"):
        if file.endswith(".jar"):
            local_mods.append(file)
    return local_mods


def mod_folder_exists():
    if not os.path.exists('mods'):
        return False
    return True


def create_mod_folder():
    os.makedirs('mods')


def get_incorrect_mods(local_mods, remote_mods):
    incorrect_mods = []
    for mod in local_mods:
        if mod not in remote_mods:
            incorrect_mods.append(mod)
    return incorrect_mods


def remove_mods(mod_names):
    for mod_name in mod_names:
        os.remove('./mods/' + mod_name)


console = Console(
    theme=Theme(
        {
            "progress.percentage": "white",
            "progress.download": "white",
            "progress.data.speed": "white",
            "progress.remaining": "white",
            "progress.filesize": "white",
            "status.spinner": "white",
            "prompt.choices": "white",
            "prompt.default": "white"}
    ),
    highlight=False)

FORGE_URL = "https://serwerwanilia.pl/info/forge.txt"
REMOTE_URL = "https://serwerwanilia.pl/info/mods.txt"
VERSION_URL = "https://serwerwanilia.pl/info/version.txt"
VERSION = "1.2.1"

clear()
console.rule("Instalator modów [magenta]Wanilia+[/magenta]", style="white")
console.print("Wersja " + VERSION, justify="center")
console.print(
    "\nTen program pobierze forge oraz mody i umieści je w folderze [underline]mods[/underline] w tej samej lokalizacji, w której się znajduje, dlatego powinien zostać umieszczony w lokalizacji instalacji Minecrafta (z reguły w folderze .minecraft). Po więcej informacji zajrzyj na Discord.",
    justify="center")
console.print("\nNaciśnij Enter, by kontynuować.", justify="center")
input()
clear()

with console.status("Sprawdzanie nowej wersji instalatora.", spinner="point"):
    update_possible = installer_update_possible()

if update_possible:
    console.print(
        "[red]Dostępna jest nowa wersja instalatora.\nWięcej informacji na naszym Discordzie.[/red]",
        justify="center")
    console.print("\nNaciśnij Enter, by kontynuować.", justify="center")
    input()
    clear()

with console.status("Sprawdzanie wersji Forge.", spinner="point"):
    forge_found = forge_is_installed()
    forge_version = get_forge_remote_version()

if forge_found:
    console.print("[green]W twojej lokalizacji został już znaleziony profil z zalecaną wersją forge. Oznacza to więc, że jest on już prawdopodobnie zainstalowany.[/green]")
else:
    console.print("[red]W twojej lokalizacji nie został znaleziony profil z zalecaną wersją forge. Oznacza to więc, że prawdopodobnie nie jest ona jeszcze zainstalowana.[/red]")

default_option = "N" if forge_found else "T"
user_choice = Prompt.ask(
    f"\nCzy chcesz pobrać i zainstalować forge? Zalecana wersja forge to [underline]{forge_version}[/underline]. \nWpisz \"[green]T[/green]\", by pobrać i zainstalować forge lub \"[red]N[/red]\" by kontynuować bez pobierania:",
    choices=[
        "T",
        "N"],
    default=default_option,
    console=console)

if user_choice == 'T':
    clear()
    with console.status("Szukanie wersji Forge.", spinner="point"):
        forge_download_url = get_forge_download_url()
    print("Pobieranie forge:")
    install_forge(forge_download_url)
    clear()
    console.print(
        "[green]●[/green] Instalacja forge zakończona.")

clear()

if not mod_folder_exists():
    create_mod_folder()

with console.status("Synchronizowanie listy modów", spinner="point"):
    remote_mod_urls = fetch_modlist()
    remote_names = url_to_filename_list(remote_mod_urls)
console.print("[green]●[/green] Lista modów zsynchronizowana.")

with console.status("Sprawdzanie zainstalowanych modów.", spinner="point"):
    local_mods = get_local_mods()
console.print("[green]●[/green] Sprawdzono zainstalowane mody.")

incorrect_mods = get_incorrect_mods(local_mods, remote_names)
if len(incorrect_mods) > 0:
    console.print("[red]●[/red] Wykryto niewłaściwe mody w folderze mods:")
    for mod in incorrect_mods:
        console.print("[red]- " + mod + "[/red]")
    user_choice = Prompt.ask(
        "Wpisz \"[green]T[/green]\" by je usunąć lub \"[red]N[/red]\" by zakończyć",
        choices=[
            "T",
            "N"],
        default="T",
        console=console)
    if user_choice == "T":
        remove_mods(incorrect_mods)
        get_local_mods()
        clear()
    else:
        sys_exit()

if mods_already_downloaded(remote_names, local_mods):
    console.print("[green]●[/green] Wszystkie mody są aktualne.")
else:
    console.print(
        "[red]●[/red] Znaleziono brakujące mody. Rozpoczęcie pobierania.\n")
    mods_required = get_mods_to_download(remote_mod_urls, local_mods)
    download_mods(mods_required, local_mods)
    console.print("[green]●[/green] Pobrano brakujące mody.")

input("\nNaciśnij enter, by zakończyć.")
