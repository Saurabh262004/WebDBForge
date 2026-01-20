import os
import time
import orjson
import bs4
from WebDBForge.Scrapers import Fetcher
from WebDBForge.Nav import SoupNavigator
from WebDBForge.Node import NodeEvaluator

def MakeDB(fetchManifest: dict[str, str], navsManifest: dict[str, str], nodeSRC: str = None, out: str = None, logSRC: str = None) -> dict | None:
	startTime = int(time.time() * 1000)

	for src in navsManifest.values():
		if not os.path.exists(src):
			return False

	navScripts = {}

	for key, value in navsManifest.items():
		navFile = open(value, 'rb')
		navBytes = navFile.read()
		navFile.close()

		nav = orjson.loads(navBytes)

		navScripts[key] = nav

	fetchData = Fetcher.fetchTextBatch(fetchManifest)

	for key, value in fetchData.items():
		fetchData[key] = bs4.BeautifulSoup(value, 'html.parser')

	navData = {}

	for key, nav in navScripts.items():
		navData[key] = SoupNavigator.eval(nav, fetchData, logFile=logSRC)

	if nodeSRC is not None and os.path.exists(nodeSRC):
		nodeFile = open(nodeSRC, 'rb')
		nodeBytes = nodeFile.read()
		nodeFile.close()

		node = orjson.loads(nodeBytes)

		db = NodeEvaluator.eval(node, navData)
	else:
		db = navData

	metadata = {}

	endTime = int(time.time() * 1000)

	metadata['lastUpdate'] = startTime
	metadata['creationTime'] = endTime - startTime

	db['__metadata__'] = metadata

	if out is not None:
		if not os.path.exists(out):
			pass

		outFile = open(out, 'wb')
		outFile.write(orjson.dumps(db, option=orjson.OPT_INDENT_2))
		outFile.close()

	return db
