import time
import cloudscraper

class Fetcher:
	@staticmethod
	def _get_session(session: cloudscraper.CloudScraper = None) -> cloudscraper.CloudScraper:
		return session or cloudscraper.create_scraper()

	@staticmethod
	def fetchText(url: str, session: cloudscraper.CloudScraper = None) -> str:
		if session is None:
			session = Fetcher._get_session(session)

		headers = {
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
			"Accept-Language": "en-US,en;q=0.9",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Connection": "keep-alive",
		}

		response = session.get(url, headers=headers)

		response.raise_for_status()

		return response.text

	@staticmethod
	def fetchTextBatch(manifest: dict[str, str], session: cloudscraper.CloudScraper = None, stall: float = 2.0) -> dict[str, str]:
		if session is None:
			session = Fetcher._get_session(session)

		responses = {}

		for key, url in manifest.items():
			time.sleep(stall)
			responses[key] = Fetcher.fetchText(url, session)

		return responses

	@staticmethod
	def fetchContent(url: str, session: cloudscraper.CloudScraper = None) -> bytes:
		if session is None:
			session = Fetcher._get_session(session)

		headers = {
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
			"Accept-Language": "en-US,en;q=0.9",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Connection": "keep-alive",
		}

		response = session.get(url, headers=headers)

		response.raise_for_status()

		return response.content

	@staticmethod
	def fetchContentBatch(manifest: dict[str, str], session: cloudscraper.CloudScraper = None, stall: float = 2.0) -> dict[str, bytes]:
		if session is None:
			session = Fetcher._get_session(session)

		responses = {}

		for key, url in manifest.items():
			time.sleep(stall)
			responses[key] = Fetcher.fetchContent(url, session)

		return responses
