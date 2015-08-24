__author__ = "Winter"

from time import sleep
from evergreen import configuration
import os
import subprocess

CONFIG_FILE_NAME = 'settings.ini'

def main():
    print('Starting ArmA dedicated server')
    config_file = "settings.ini"
    # init a configuration instance
    evergreen = configuration(CONFIG_FILE_NAME)
    settings_instance = evergreen.open_instance()
    # check if config options are all present
    settings_required = [
        ['directories', 'game_dir'],
        ['directories', 'repo_dir'],
        ['paths', 'server_config'],
        ['settings', 'profile_name'],
        ['settings', 'arma_exe'],
        ['settings', 'arma_server_exe'],
        ['settings', 'arma_server_pass'],
        ['settings', 'misc_client_params'],
        ['settings', 'repo_ignore_list'],
        ['settings', 'start_delay']
    ]
    for section, option in settings_required:
        evergreen.check_value(settings_instance, section, option)
    # set global variables
    game_directory = evergreen.return_value(settings_instance, 'directories', 'game_dir')
    mod_repository_directory = evergreen.return_value(settings_instance, 'directories', 'repo_dir')
    server_config_path = evergreen.return_value(settings_instance, 'paths', 'server_config')
    profile_name = evergreen.return_value(settings_instance, 'settings', 'profile_name')
    executable_name = evergreen.return_value(settings_instance, 'settings', 'arma_exe')
    server_executable_name = evergreen.return_value(settings_instance, 'settings', 'arma_server_exe')
    server_password = evergreen.return_value(settings_instance, 'settings', 'arma_server_pass')
    misc_client_params = evergreen.return_value(settings_instance, 'settings', 'misc_client_params')
    server_start_delay = evergreen.return_value(settings_instance, 'settings', 'start_delay')
    repo_ignore_list = evergreen.return_value(settings_instance, 'settings', 'repo_ignore_list')
    # produce a list of mods to run from the repository
    repo_contents = os.listdir(mod_repository_directory)
    if len(repo_contents) > 0:
        addon_params_string = ''
        addon_separator = ';'
        repo_ignore_list = repo_ignore_list.split(' ')
        print_list('Files being ignored in the repository: ', repo_ignore_list)
        repo_contents = [file for file in repo_contents if file not in repo_ignore_list]  # filter out unwanted files
        print('Building a list of addons to launch with arma')
        for addon in repo_contents:
            print('\tAdding: {} to the list of addons'.format(addon))
            addon_directory = os.path.join(mod_repository_directory, addon)
            addon_params_string += (addon_directory + addon_separator)
    else:
        print('There are no mods present inside the repository!')
        return -1
    executable_path = os.path.join(game_directory, executable_name)
    mods_used_parameter = '-mod=' + addon_params_string
    world_param = '-world=empty'
    profile_param = '-name=' + profile_name
    client_params = misc_client_params.split(' ')
    client_start_arguments = [executable_path, profile_param, mods_used_parameter, world_param]
    client_start_arguments.extend(client_params)
    server_executable_path = os.path.join(game_directory, server_executable_name)
    config_param = '-config=' + server_config_path
    server_start_arguments = [server_executable_path, config_param, mods_used_parameter]
    print_list('Starting ArmA dedicated server using the following parameters:', server_start_arguments)
    try:
        process = subprocess.Popen(server_start_arguments)
    except subprocess.CalledProcessError as error:
        print("ArmA 3 Server didn't manage to start!")
        output = process.communicate()[0]
        print(process.returncode)
        return -1
    else:
        print("ArmA 3 Dedicated Server successfully started")
        pause('Waiting for the server to start ', int(server_start_delay))
        client_start_arguments.extend(['-connect=127.0.0.1', '-password=' + server_password])  # make client connect to the dedicated server
    try:
        process = subprocess.Popen(client_start_arguments)
    except subprocess.CalledProcessError as error:
        print("ArmA 3 didn't manage to start!")
        output = process.communicate()[0]
        print(process.returncode)
        return -1
    else:
        print("ArmA 3 successfully started")

def print_list(prompt='', list=[]):
    print(prompt)
    for element in list:
        print('\t{}'.format(element))

def pause(prompt='', time=10):
    count = time
    while count > 0:
        print('{}: {}'.format(count, prompt), end='\r')
        sleep(1)
        count -=1

if __name__ == "__main__":
    main()