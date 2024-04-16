import yaml

def read_config(requirements: list[str]) -> dict[str, str]:
    config = yaml.safe_load(open("config.yaml"))
    # validations
    for requirement in requirements:
        if requirement not in config:
            raise Exception(f"Required parameter `{requirement}` not found in config.yaml")
    
    return config