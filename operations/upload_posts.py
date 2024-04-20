import instagrapi
import inquirer
import os
import hashlib
import requests
import json
from dataclasses import dataclass

@dataclass
class Location:
    name: str = None
    latitude: float = None
    longitude: float = None

class Post:
    caption: str
    content_path: str
    upload_id: str = None
    user_tags: list[instagrapi.types.Usertag] = []
    location: Location = None
    extra_data: dict = {}
    
    def __init__(self, fields: list[str], path: str):
        post_extensions = ('jpg', 'jpeg')
        for field in fields:
            if field.endswith(post_extensions):
                setattr(self, 'content_path', field)
                self.content_path = field
            elif field.split('.')[0] == 'caption':
                self.caption = open(f"{path}/{field}").read()
            elif field.split('.')[0] == 'upload_id':
                self.upload_id = open(f"{path}/{field}").read()
            elif field.split('.')[0] == 'user_tags':
                user_tags = []
                with open(f"{path}/{field}", 'r') as f:
                    for tag_params in f.read().splitlines():
                        for tag_param in tag_params.split(','):
                            user_tag = instagrapi.types.Usertag(tag_param[0], tag_param[1], tag_param[2])
                            user_tags.append(user_tag)
                self.user_tags = user_tags
            elif field.split('.')[0] == 'location':
                with open(f"{path}/{field}", 'r') as f:
                    location_params = f.read().splitlines()
                self.location = Location(location_params[0], location_params[1], location_params[2])
            elif field.split('.')[0] == 'extra_data':
                with open(f"{path}/{field}", 'r') as f:
                    extra_data = json.load(f)
                self.extra_data = extra_data


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
                    json.dumps(attr)  # Try serializing the attribute
                    serializable_members.append(attr_name)
                except (TypeError, OverflowError):
                    pass  # Skip non-serializable attributes
    return serializable_members

def upload_posts(config, count):
    count = int(count)

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
            try:
                post = Post(files, subdir_path)
            except Exception as e:
                print(e)
                raise e

            try:
                media = cl.photo_upload(
                    path=os.path.join(subdir_path, post.content_path),
                    caption=post.caption,
                    # TODO: make the following work
                    # upload_id=post.upload_id,
                    # usertags=post.user_tags,
                    # location=post.location,
                    # extra_data=post.extra_data,
                )
            except Exception as e:
                print(e)
                raise e

            with open(idempotency_key_file_path, "a") as f:
                f.write(f"{idempotency_key}\n")

            if "discord_webhook" in config:
                payload = json.dumps({"content": {key:value for key, value in post.__dict__.items() if not key.startswith('__') and not callable(key)}})
                headers = {"Content-Type": "application/json"}
                # TODO: make the following work
                response = requests.post(config["discord_webhook"]["url"], data=payload, headers=headers)
                print(response.json())

            posted_count += 1
            print(f"Posted {posted_count} posts")
                    

def main(config_file_path: str, count: int):
    config = read_config(config_file_path, ["authenticated_user", "upload"])
    upload_posts(config, count)

if __name__ == "__main__":
    from read_config import read_config
    import typer
    typer.run(main)

else:
    # running as module
    pass