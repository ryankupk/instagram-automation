#!./env/bin/python3
import inquirer
import operations.scrape_posts as sp
import operations.upload_posts as up
from operations.read_config import read_config

def main() -> None:

    all_operations: list[str] = [
        "Scrape Posts",
        "Upload Posts",
    ]
    questions = [
        inquirer.List("operation",
        message="Select operation", 
        choices=all_operations)
    ]
    answer = inquirer.prompt(questions)

    if answer["operation"] == "Scrape Posts":
        config: dict = read_config(["authenticated_user", "download"])
        parameters = sp.get_parameters()
        sp.scrape_posts(config, parameters["username"], parameters["start"], parameters["count"])
    elif answer["operation"] == "Upload Posts":
        config: dict = read_config(["authenticated_user", "upload"])
        parameters = up.get_parameters()
        up.upload_posts(config, parameters["count"])
    

if __name__ == '__main__':
    main()