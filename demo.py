import os
import sys
import asyncio
import requests
import datetime
from random import random
from jotting import note, read


@note.worthy
async def main(urls, notepad):
    notepad(info="triggering jobs")
    for u in urls:
        await get_url(u)


@note.worthy
async def get_url(url, notepad):
    loop = asyncio.get_event_loop()
    await asyncio.sleep(random())
    notepad(info="about to get the url")
    return requests.get(url)


with open(os.path.expanduser("~/Desktop/logbox.txt"), "w+") as f:
    with note.book(_writer=read.tree(file=f)):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(main([
            "https://google.com", "https://youtube.com", "https://facebook.com", "https://wikipedia.org"
        ]))
