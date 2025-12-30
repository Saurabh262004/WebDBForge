import os
import requests
from WebDBForge.Sanitizer import Sanitizer
from WebDBForge.Scrapers.Fetcher import Fetcher

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
  def saveBatch(data: dict[str, bytes], dir: str) -> None:
    if not os.path.exists(dir):
      os.makedirs(dir)

    for name, content in data.items():

      osProofName = Sanitizer.OSProofName(name)

      if osProofName is False:
        raise Exception(f'filename {name} is not OS proof')

      with open(os.path.join(dir, osProofName), 'wb') as f:
        f.write(content)

  @staticmethod
  def collectImage(url: str, dir: str, name: str, session: requests.Session = None) -> None:
    data = Fetcher.fetchContent(url, session)

    ImageCollector.saveImage(data, dir, name)

  @staticmethod
  def collectBatch(manifest: dict[str, str], dir: str, session: requests.Session = None, stall: float = 2.0) -> None:
    contents = Fetcher.fetchContentBatch(manifest, session, stall)

    ImageCollector.saveBatch(contents, dir)
