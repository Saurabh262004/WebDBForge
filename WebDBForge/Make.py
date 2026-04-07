import os
import time
import orjson
import bs4
from WebDBForge.Scrapers import Fetcher
from WebDBForge.Nav import SoupNavigator
from WebDBForge.Node import NodeEvaluator

def MakeDB(fetchManifest: dict[str, str], navsManifest: dict[str, str], nodeSRC: str = None, extraRef: dict = None, out: str = None, logSRC: str = None) -> dict | None:
	startTime = int(time.time() * 1000)

	# verify nav files

	for src in navsManifest.values():
		if not os.path.exists(src):
			raise FileNotFoundError(src)

	# load nav files

	navScripts = {}

	for key, value in navsManifest.items():
		with open(value, 'rb') as f:
			navBytes = f.read()

		nav = orjson.loads(navBytes)

		navScripts[key] = nav

	# fetch plain html pages

	session = Fetcher._get_session() # can be used for image collection later

	fetchData = Fetcher.fetchTextBatch(fetchManifest, session)

	# process plain html pages

	for key, value in fetchData.items():
		fetchData[key] = bs4.BeautifulSoup(value, 'html.parser')

	# extract data from processed html with nav scripts

	navData = {}

	for key, nav in navScripts.items():
		navData[key] = SoupNavigator.eval(nav, fetchData, logFile=logSRC)

	# add extra reference data

	if extraRef is not None:
		navData.update(extraRef)

	# process extracted data with nodes

	if nodeSRC is not None and os.path.exists(nodeSRC):
		with open(nodeSRC, 'rb') as f:
			nodeBytes = f.read()

		node = orjson.loads(nodeBytes)

		db = NodeEvaluator.eval(node, navData)
	else:
		db = navData

	# finalize database

	metadata = {}

	endTime = int(time.time() * 1000)

	metadata['lastUpdate'] = startTime
	metadata['creationTime'] = endTime - startTime

	if isinstance(db, dict):
		db['__metadata__'] = metadata
	elif isinstance(db, list):
		db.append({'__metadata__': metadata})

	# return / write database

	if out is not None:
		if not os.path.exists(out):
			pass

		with open(out, 'wb') as f:
			f.write(orjson.dumps(db, option=orjson.OPT_INDENT_2))

	return db
