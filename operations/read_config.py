import yaml

def read_config(config_file_path: str = None, requirements: list[str] = ["authenticated_user"]) -> dict[str, str]:
    config = yaml.safe_load(open(config_file_path))
    # validations
    for requirement in requirements:
        if requirement not in config:
            raise Exception(f"Required parameter `{requirement}` not found in config.yaml")
    
    return config