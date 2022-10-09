from rich.console import Console
from rich.prompt import Prompt
from rich.theme import Theme

from modules.helpers import clear, exit_, url_to_filename_list
from modules.install import *
from modules.mods import *
from modules.web_requests import *


def interface():
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
        console.print(
            "[green]W twojej lokalizacji został już znaleziony profil z zalecaną wersją forge. Oznacza to więc, że jest on już prawdopodobnie zainstalowany.[/green]")
    else:
        console.print(
            "[red]W twojej lokalizacji nie został znaleziony profil z zalecaną wersją forge. Oznacza to więc, że prawdopodobnie nie jest ona jeszcze zainstalowana.[/red]")

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

        console.print("Pobieranie forge...\n")
        download_forge(forge_download_url, console)
        console.print("Instalowanie forge...\n")
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
            local_mods = get_local_mods()
            clear()
        else:
            exit_()

    if mods_already_downloaded(remote_names, local_mods):
        console.print("[green]●[/green] Wszystkie mody są aktualne.")
    else:
        console.print(
            "[red]●[/red] Znaleziono brakujące mody. Rozpoczęcie pobierania.\n")
        missing_mods = get_missing_mods(remote_mod_urls, local_mods)

        download_mods(missing_mods, console)
        console.print("[green]●[/green] Pobrano brakujące mody.")

    input("\nNaciśnij enter, by zakończyć.")
    console.print("Dobranoc")
