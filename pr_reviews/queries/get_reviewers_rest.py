import os
import aiohttp
import asyncio

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# get proxy settings from environment variables
HTTPS_PROXY = os.getenv("HTTPS_PROXY")
# check for lowercase https_proxy
if not HTTPS_PROXY:
    HTTPS_PROXY = os.getenv("https_proxy")


async def fetch(session, url):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    if HTTPS_PROXY:
        async with session.get(url, headers=headers, proxy=HTTPS_PROXY) as response:
            return await response.json()
    else:
        async with session.get(url, headers=headers) as response:
            return await response.json()


async def fetch_batch(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)


def get_reviewers_for_pull_request(
    owner: str, repo: str, pull_number: int
) -> list[dict]:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
    urls = [url]
    reviewers = asyncio.run(fetch_batch(urls))
    result = [item["user"] for sublist in reviewers for item in sublist]
    return result


def get_reviewers_for_pull_requests(
    owner: str, repo: str, pull_numbers: list[int]
) -> list[dict]:
    urls = [
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        for pull_number in pull_numbers
    ]
    reviewers = asyncio.run(fetch_batch(urls))
    result = [item["user"] for sublist in reviewers for item in sublist]
    return result
