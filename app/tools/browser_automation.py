from langchain.tools import tool 

import subprocess

@tool
def open_website(url: str) -> str:
    """Open a website URL in the default macOS browser."""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        subprocess.run(["open", url], check=True)
        return f"Opened {url}"

    except subprocess.CalledProcessError as e:
        return f"Failed to open {url}: {e}"