import os
import requests
from WebDBForge.Sanitizer import Sanitizer
from WebDBForge.Fetcher import Fetcher

class ImageCollector:
  @staticmethod
  def saveImage(data: bytes, dir: str, name: str) -> None:
    if not os.path.exists(dir):
      os.makedirs(dir)

    osProofName = Sanitizer.OSProofName(name)

    if osProofName is False:
      raise Exception(f'filename {name} is not OS proof')

    with open(os.path.join(dir, osProofName), 'wb') as f:
      f.write(data)

  @staticmethod
  def saveBatch(contents: list[bytes], dir: str, names: list[str]) -> None:
    if not os.path.exists(dir):
      os.makedirs(dir)

    for i in range(len(contents)):

      osProofName = Sanitizer.OSProofName(names[i])

      if osProofName is False:
        raise Exception(f'filename {names[i]} is not OS proof')

      with open(os.path.join(dir, osProofName), 'wb') as f:
        f.write(contents[i])

  @staticmethod
  def collectImage(url: str, dir: str, name: str, session: requests.Session = None) -> None:
    data = Fetcher.fetchContent(url, session)
    ImageCollector.saveImage(data, dir, name)

  @staticmethod
  def collectBatch(manifest: dict[str], dir: str, session: requests.Session = None, stall: float = 2.0) -> None:
    names = list(manifest.keys())
    urls = list(manifest.values())

    contents = Fetcher.fetchContentBatch(urls, session, stall)

    ImageCollector.saveBatch(contents, dir, names)
