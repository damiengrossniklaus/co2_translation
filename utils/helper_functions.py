def read_markdown(markdown_path: str) -> str:
    """
    Reads markdown file and returns text as str.
    """
    text = ""
    with open(markdown_path, 'r') as f:
        for line in f.readlines():
            text += line

    return text
