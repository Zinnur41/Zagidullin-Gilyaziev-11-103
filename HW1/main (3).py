import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os


async def download_page(session, url, file_number, semaphore):
    async with semaphore:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    os.makedirs("pages", exist_ok=True)
                    filename = os.path.join("pages", f"{file_number}.txt")
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    return file_number, url
                else:
                    return None
        except Exception as e:
            print(f"Error downloading {url}: {e}")


async def main():
    category_url = "https://ru.wikipedia.org/wiki/Категория:Художники_XX_века"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(category_url) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
            mw_pages = soup.find("div", id="mw-pages")
            article_urls = []
            for item in mw_pages.find_all("li"):
                a_tag = item.find("a")
                if a_tag and "href" in a_tag.attrs and a_tag["href"].startswith("/wiki/"):
                    full_url = "https://ru.wikipedia.org" + a_tag["href"]
                    article_urls.append(full_url)

    urls_to_download = article_urls[1:101]

    semaphore = asyncio.Semaphore(5)
    async with aiohttp.ClientSession() as session:
        tasks = [
            download_page(session, url, i, semaphore)
            for i, url in enumerate(urls_to_download, 1)
        ]
        results = await asyncio.gather(*tasks)
        downloaded_pages = [r for r in results if r is not None]

    with open("index.txt", "w", encoding="utf-8") as f:
        for file_number, url in downloaded_pages:
            f.write(f"{file_number} {url}\n")


if __name__ == "__main__":
    asyncio.run(main())
