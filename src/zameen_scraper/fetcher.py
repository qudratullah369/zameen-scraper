import httpx


DEFAULT_TIMEOUT = 20.0


def fetch_html(url: str, timeout: float = DEFAULT_TIMEOUT) -> str:
    response = httpx.get(
        url,
        timeout=timeout,
        follow_redirects=True,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            )
        },
    )

    response.raise_for_status()
    return response.text
