import asyncio

import aiohttp
import networkx as nx
from bs4 import BeautifulSoup
from loguru import logger


async def urls(url, session):
    try:
        r = await session.get(url)
        content_type = r.headers["content-type"]

        if "text/html" not in content_type:
            return

        text = await r.text()
        soup = BeautifulSoup(text, "html.parser")

        for link in soup.find_all("a"):
            yield link.get("href")

    except aiohttp.ServerConnectionError as e:
        logger.warning(f"{url}: {e}")

    except aiohttp.ClientOSError as e:
        logger.warning(e)


class URLGraph:
    def __init__(self):
        self.roots = []
        self.visited = {}
        self.graph = nx.Graph()

    def add(self, root):
        self.roots.append(root)
        self.add_node(root, root)

    def add_node(self, url, root):
        self.visited[url] = 1
        self.graph.add_node(url, group=root)

    async def search(self, url, session, root):
        async for child in urls(url, session):
            if child and child.startswith(root):  # disgusting shortcut
                self.graph.add_edge(url, child)

                if child not in self.visited:
                    self.add_node(child, root)
                    asyncio.create_task(self.search(child, session, root))
                else:
                    self.visited[child] += 1

    def build(self, time=60, workers=20):
        async def abuild():
            conn = aiohttp.TCPConnector(limit=workers)
            session = aiohttp.ClientSession(connector=conn)

            for root in self.roots:
                asyncio.create_task(self.search(root, session, root))

            await asyncio.sleep(time)
            await session.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(abuild())

    @property
    def weights(self):
        return self.visited
