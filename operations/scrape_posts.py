import instagrapi
import inquirer

def get_parameters():
    questions: list[inquirer.Text] = [
        inquirer.Text(name='username', message='Enter username'),
        inquirer.Text(name='start', message='First post to scrape from (enter 0 to start from the topmost post)'),
        inquirer.Text(name='count', message='Number of posts to scrape after starting post (enter 0 to scrape all)'),
    ]
    answers: dict[str, str] = inquirer.prompt(questions)
    return answers
    

def scrape_posts(config: dict, username: str, start: str, count: str):
    count = int(count)
    start = int(start)

    cl = instagrapi.Client()
    try:
        cl.login(config["authenticated_user"]["username"], config["authenticated_user"]["password"])
    except Exception as e:
        print(e)
        raise e
    
    try:
        user_id = cl.user_id_from_username(username)
    except Exception as e:
        print(e)
        raise e

    medias = cl.user_medias(user_id, count + start if count > 0 else 9999)
    for media in medias[int(start) : int(start) + int(count)]:
        if media.media_type == 1:
            # photo
            cl.photo_download(media.pk, config["download"]["path"])
        elif media.media_type == 8:
            # album
            cl.album_download(media.pk, config["download"]["path"])
        elif media.media_type == 2 and media.product_type =='clips':
            cl.clip_download(media.pk, config["download"]["path"])
        elif media.media_type == 2 and media.product_type == 'feed':
            cl.video_download(media.pk, config["download"]["path"])
        else:
            pass

def main(config_file_path: str, username: str, start: int, count: int) -> None:
    config = read_config(config_file_path, ["authenticated_user", "download"])
    scrape_posts(config, username, start, count)
        
if __name__ == '__main__':
    from read_config import read_config
    import typer
    typer.run(main)


else:
    # running as module
    pass