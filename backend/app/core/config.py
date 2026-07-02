

def parse_cors_origins(origins: str) -> list[str] | str:
    """
    Parse a string of CORS origins into a list.

    Args:
        origins (str): A string of CORS origins, separated by commas.

    Returns:
        list: A list of CORS origins.
    """
    if origins.startswith("[") and origins.endswith("]"):
        return [origin.strip() for origin in origins[1:-1].split(",")]
    return [origin.strip() for origin in origins.split(",")]

