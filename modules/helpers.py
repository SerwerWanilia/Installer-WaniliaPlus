import os
from sys import exit as sys_exit


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
        exit_()



def exit_():
    sys_exit()
