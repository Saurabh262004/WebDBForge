import time
import requests

class Fetcher:
  @staticmethod
  def fetchText(url: str, session: requests.Session = None) -> str:
    if session is None:
      session = requests.Session()

    response = session.get(url)

    response.raise_for_status()

    return response.text

  @staticmethod
  def fetchTextBatch(urls: list[str], session: requests.Session = None, stall: float = 2.0) -> list[str]:
    if session is None:
      session = requests.Session()

    responses = []

    for url in urls:
      time.sleep(stall)
      responses.append(Fetcher.fetchText(url, session))

    return responses

  @staticmethod
  def fetchContent(url: str, session: requests.Session = None) -> bytes:
    if session is None:
      session = requests.Session()

    response = session.get(url)

    response.raise_for_status()

    return response.content

  @staticmethod
  def fetchContentBatch(urls: list[str], session: requests.Session = None, stall: float = 2.0) -> list[bytes]:
    if session is None:
      session = requests.Session()

    responses = []

    for url in urls:
      time.sleep(stall)
      responses.append(Fetcher.fetchContent(url, session))

    return responses
