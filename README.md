# instagram-automation
Repository to hold scripts and services for automating tasks on instagram

## Usage

Create a python virtual environment
``` bash
virtualenv env
```
Activate the virtual environment
#### Linux
``` bash
source env/bin/activate
```
#### Powershell
``` PowerShell
env\Scripts\activate.ps1
```

Create the `config.yaml` file
``` yaml
authenticated_user: # necessary for all operations
    username: <instagram username or email address>
    password: <password>

download: # necessary for scraping posts
    path: /path/to/dir/

upload: # necessary for uploading posts
    path: /path/to/dir/
    idempotency_key_path: /path/to/dir/

discord_webhook: #optional
    url: <discord webhook url for notifications>

```

Run the script with a wizard to make selections:

``` bash
./ia.py
```

or run individual scripts with commandline arguments:
``` bash
python3 operations/scrape_posts.py <username> <starting post index> <number of posts to scrape>
```
