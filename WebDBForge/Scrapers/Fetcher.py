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
	def fetchTextBatch(manifest: dict[str, str], session: requests.Session = None, stall: float = 2.0) -> dict[str, str]:
		if session is None:
			session = requests.Session()

		responses = {}

		for key, url in manifest.items():
			time.sleep(stall)
			responses[key] = Fetcher.fetchText(url, session)

		return responses

	@staticmethod
	def fetchContent(url: str, session: requests.Session = None) -> bytes:
		if session is None:
			session = requests.Session()

		response = session.get(url)

		response.raise_for_status()

		return response.content

	@staticmethod
	def fetchContentBatch(manifest: dict[str, str], session: requests.Session = None, stall: float = 2.0) -> dict[str, bytes]:
		if session is None:
			session = requests.Session()

		responses = {}

		for key, url in manifest.items():
			time.sleep(stall)
			responses[key] = Fetcher.fetchContent(url, session)

		return responses
