#!./env/bin/python3
import inquirer
import os
import operations.scrape_posts as sp
import operations.upload_posts as up
from operations.read_config import read_config

def main() -> None:

    all_operations: list[str] = [
        "Scrape Posts",
        "Upload Posts",
    ]
    ops_questions = [
        inquirer.List("operation",
        message="Select operation", 
        choices=all_operations)
    ]
    ops_answer = inquirer.prompt(ops_questions)

    yaml_files = [file for file in os.listdir() if file.endswith('.yaml')]
    if len(yaml_files) == 0:
        raise FileNotFoundError("No config file found")
    elif len(yaml_files) > 1:
        # prompt for config file to use
        conf_questions = [
            inquirer.List("config_file",
            message="Select config file to use", 
            choices=yaml_files)
        ]
        conf_answer = inquirer.prompt(conf_questions)
        config_file_path = conf_answer["config_file"]
    else:
        config_file_path = yaml_files[0]

    if ops_answer["operation"] == "Scrape Posts":
        config: dict = read_config(config_file_path, ["authenticated_user", "download"])
        parameters = sp.get_parameters()
        sp.scrape_posts(config, parameters["username"], parameters["start"], parameters["count"])
    elif ops_answer["operation"] == "Upload Posts":
        config: dict = read_config(config_file_path, ["authenticated_user", "upload"])
        parameters = up.get_parameters()
        up.upload_posts(config, parameters["count"])
    

if __name__ == '__main__':
    main()