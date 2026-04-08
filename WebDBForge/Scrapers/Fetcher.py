import time
import cloudscraper

# standard headers for all requests to mimic a real browser
HEADERS = {
	"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
	"Accept-Language": "en-US,en;q=0.9",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	"Connection": "keep-alive",
}

class Fetcher:
	# get a cloudscraper session
	@staticmethod
	def _get_session(session: cloudscraper.CloudScraper = None) -> cloudscraper.CloudScraper:
		return session or cloudscraper.create_scraper()

	# fetch plain text from url
	@staticmethod
	def fetchText(url: str, session: cloudscraper.CloudScraper = None) -> str:
		session = Fetcher._get_session(session)

		response = session.get(url, headers=HEADERS)

		response.raise_for_status()

		return response.text

	# fetch plain text from multiple urls
	@staticmethod
	def fetchTextBatch(manifest: dict[str, str], session: cloudscraper.CloudScraper = None, stall: float = 2.0) -> dict[str, str]:
		session = Fetcher._get_session(session)

		responses = {}

		for key, url in manifest.items():
			time.sleep(stall)
			responses[key] = Fetcher.fetchText(url, session)

		return responses

	# fetch raw content from url
	@staticmethod
	def fetchContent(url: str, session: cloudscraper.CloudScraper = None) -> bytes:
		session = Fetcher._get_session(session)

		response = session.get(url, headers=HEADERS)

		response.raise_for_status()

		return response.content

	# fetch raw content from multiple urls
	@staticmethod
	def fetchContentBatch(manifest: dict[str, str], session: cloudscraper.CloudScraper = None, stall: float = 2.0) -> dict[str, bytes]:
		session = Fetcher._get_session(session)

		responses = {}

		for key, url in manifest.items():
			time.sleep(stall)
			responses[key] = Fetcher.fetchContent(url, session)

		return responses
