import instagrapi
import inquirer
import os
import hashlib
from requests import post
from json import dumps
from copy import deepcopy
from dataclasses import dataclass

@dataclass
class Location:
    name: str
    latitude: float
    longitude: float

@dataclass
class Post:
    caption: str
    content_path: str
    upload_id: str
    user_tags: list[instagrapi.types.Usertag]
    location: Location
    extra_data: dict

def get_parameters():
    questions: list[inquirer.Text] = [
        inquirer.Text(name='count', message='Number of posts to post from the uploads directory (enter 0 to post all)'),
    ]
    answers: dict[str, str] = inquirer.prompt(questions)
    return answers

def get_idempotency_key(subdir_path: str) -> hash:
    file_hashes = []
    for file in os.listdir(subdir_path):
        if os.path.isfile(os.path.join(subdir_path, file)):
            with open(os.path.join(subdir_path, file), 'rb') as f:
                # append md5 hash of each file to a list
                file_hashes.append(hashlib.md5(f.read()).hexdigest())
    # create md5 hash of all file hashes
    return hashlib.md5(''.join(file_hashes).encode()).hexdigest()

def get_serializable_members(obj):
    serializable_members = []
    for attr_name in dir(obj):
        if not attr_name.startswith('_'):  # Skip private and magic methods
            attr = getattr(obj, attr_name)
            if not callable(attr):  # Skip callable attributes (methods)
                try:
                    dumps(attr)  # Try serializing the attribute
                    serializable_members.append(attr_name)
                except (TypeError, OverflowError):
                    pass  # Skip non-serializable attributes
    return serializable_members

def upload_posts(config, count):
    count = int(count)

    required_items = ["caption.txt", "image.jpg"]

    cl = instagrapi.Client()
    try:
        cl.login(config["authenticated_user"]["username"], config["authenticated_user"]["password"])
    except Exception as e:
        print(e)
        raise e
    
    posted_count = 0
    for root, dirs, _ in os.walk(config["upload"]["content_path"]):
        for subdir in dirs:
            if posted_count >= count > 0:
                break
            subdir_path = os.path.join(root, subdir)

            idempotency_key = get_idempotency_key(subdir_path)
            idempotency_key_file_path = os.path.join(config["upload"]["idempotency_key_path"], "idempotency_key.txt")
            if os.path.isfile(idempotency_key_file_path):
                with open(idempotency_key_file_path, "r") as f:
                    existing_idempotency_keys = f.read().splitlines()
                    if idempotency_key in existing_idempotency_keys:
                        print(f"Idempotency key {idempotency_key} already exists for directory {subdir}, skipping...")
                        continue
                        
            files = os.listdir(subdir_path)

            # this is very stupid!!!
            for required_item in required_items:
                if required_item not in files:
                    print(f"Required item {required_item} not found in directory {subdir}, skipping...")
                    continue
            
            try:
                media = cl.photo_upload(
                    path=os.path.join(subdir_path, "image.jpg"),
                    caption=open(os.path.join(subdir_path, "caption.txt")).read(),
                )
            except Exception as e:
                print(e)
                raise e

            with open(idempotency_key_file_path, "a") as f:
                f.write(f"{idempotency_key}\n")

            if "discord_webhook" in config:
                payload = {"content": get_serializable_members(media)}
                headers = {"Content-Type": "application/json"}
                res = post(config["discord_webhook"]["url"], data=dumps(payload), headers=headers)
                print(config["discord_webhook"]["url"])
                print(res.json())

            posted_count += 1
            print(f"Posted {posted_count} posts")
                    

def main(count: int):
    config = read_config(["authenticated_user", "upload"])
    upload_posts(config, count)

if __name__ == "__main__":
    from read_config import read_config
    import typer
    typer.run(main)

else:
    # running as module
    pass