import os
import requests
from WebDBForge.Sanitizer import Sanitizer
from WebDBForge.Scrapers.Fetcher import Fetcher

class ImageCollector:
	# save a single image (raw content) to dir with name
	@staticmethod
	def saveImage(data: bytes, dir: str, name: str) -> None:
		if not os.path.exists(dir):
			os.makedirs(dir)

		osProofName = Sanitizer.OSProofName(name)

		if not osProofName:
			raise Exception(f'filename "{name}" is not OS proof')

		with open(os.path.join(dir, osProofName), 'wb') as f:
			f.write(data)

	# save multiple images (raw content) to dir with names
	@staticmethod
	def saveBatch(data: dict[str, bytes], dir: str) -> None:
		if not os.path.exists(dir):
			os.makedirs(dir)

		for name, content in data.items():

			osProofName = Sanitizer.OSProofName(name)

			if not osProofName:
				raise Exception(f'filename "{name}" is not OS proof')

			with open(os.path.join(dir, osProofName), 'wb') as f:
				f.write(content)

	# collect a single image (raw content) from url and save to dir with name
	@staticmethod
	def collectImage(url: str, dir: str, name: str, session: requests.Session = None) -> None:
		data = Fetcher.fetchContent(url, session)

		ImageCollector.saveImage(data, dir, name)

	# collect multiple images (raw content) from urls and save to dir with names
	@staticmethod
	def collectBatch(manifest: dict[str, str], dir: str, session: requests.Session = None, stall: float = 2.0) -> None:
		contents = Fetcher.fetchContentBatch(manifest, session, stall)

		ImageCollector.saveBatch(contents, dir)
