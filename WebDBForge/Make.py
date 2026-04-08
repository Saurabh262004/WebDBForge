import os
import time
import orjson
import bs4
from WebDBForge.Scrapers import Fetcher, ImageCollector
from WebDBForge.Nav import SoupNavigator
from WebDBForge.Node import NodeEvaluator
from tqdm import tqdm

def MakeDB(
		fetchManifest: dict[str, str],
		navsManifest: dict[str, str],
		nodeSRC: str = None,
		extraRef: dict = None,
		imageManifest: dict[str, str] = None,
		out: str = None,
		rawOut: str = None,
		logSRC: str = None,
		stall: float = 2.0
	) -> dict:
	'''
	Build a structured database by fetching HTML sources, processing them
	through navigation scripts, and evaluating nodes.

	Parameters
	----------
	fetchManifest : dict[str, str]
		Mapping of keys to URLs for plain HTML pages to fetch.

	navsManifest : dict[str, str]
		Mapping of keys to file paths of navigation scripts used to process
		the fetched HTML content.

	nodeSRC : str | None, optional
		File path to a node script that defines the structure of the final
		database. If None, node evaluation may be skipped or handled elsewhere.

	extraRef : dict | None, optional
		Additional reference data used during node evaluation.

	imageManifest : dict | None, optional
		Configuration for the image collection process. Must include:
			- "__dir__": Target directory for images.
			- "__type__": Either "ref" or "direct".

		If "__type__" == "ref":
			- Must include "__ref__": Key pointing to a location in the final
			  database that contains the actual manifest.

		If "__type__" == "direct":
			- Must include "__manifest__": The actual image manifest.

	out : str | None, optional
		File path to write the final database. If None, the database is not
		written to disk and is only returned.

	rawOut : str | None, optional
		File path to write the raw extracted data from navigation scripts before node evaluation.\
		If None, raw data is not written to disk.

	logSRC : str | None, optional
		File path for logging errors during navigation script evaluation.
		If provided, errors are written to this file. If None, no log file
		is created.

	stall : float, default=2.0
		Time in seconds to wait between consecutive fetch requests.

	Returns
	-------
	dict
		The constructed database object.
	'''

	with tqdm(total=100, desc='Making DB') as pbar:
		startTime = int(time.time() * 1000)

		# verify nav files

		for src in navsManifest.values():
			if not os.path.exists(src):
				raise FileNotFoundError(src)

		pbar.update(10)

		# load nav files

		navScripts = {}

		for key, value in navsManifest.items():
			with open(value, 'rb') as f:
				navBytes = f.read()

			nav = orjson.loads(navBytes)

			navScripts[key] = nav

		pbar.update(10)

		# fetch plain html pages

		session = Fetcher._get_session()

		fetchData = Fetcher.fetchTextBatch(fetchManifest, session, stall)

		pbar.update(10)

		# process plain html pages

		for key, value in fetchData.items():
			fetchData[key] = bs4.BeautifulSoup(value, 'html.parser')

		pbar.update(10)

		# extract data from processed html with nav scripts

		navData = {}

		for key, nav in navScripts.items():
			navData[key] = SoupNavigator.eval(nav, fetchData, logFile=logSRC)

		pbar.update(10)

		# write raw extracted data to disk before node evaluation

		if rawOut is not None:
			path = os.path.dirname(rawOut)

			if not os.path.exists(path):
				os.makedirs(path)

			with open(rawOut, 'wb') as f:
				f.write(orjson.dumps(navData, option=orjson.OPT_INDENT_2))

		pbar.update(10)

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

		pbar.update(10)

		# image collection process

		if imageManifest is not None:
			# get proper image manifest

			imgDir = imageManifest.get('__dir__', None)

			if imgDir is None:
				raise Exception('image manifest must contain __dir__ key')

			manifestType = imageManifest.get('__type__', None)

			if manifestType is None:
				raise Exception('image manifest must contain __type__ key')

			if manifestType == 'ref':
				imageManifest = db.get(imageManifest['__ref__'], None)
			elif manifestType == 'direct':
				imageManifest = imageManifest.get('__manifest__', None)

			if imageManifest is None:
				raise Exception('no valid image manifest found')

			# collect images

			ImageCollector.collectBatch(imageManifest, imgDir, session, stall)

		pbar.update(10)

		# finalize database / add metadata

		metadata = {}

		endTime = int(time.time() * 1000)

		metadata['lastUpdate'] = startTime
		metadata['creationTime'] = endTime - startTime

		if isinstance(db, dict):
			db['__metadata__'] = metadata
		elif isinstance(db, list):
			db.append({'__metadata__': metadata})

		pbar.update(10)

		# return / write database

		if out is not None:
			path = os.path.dirname(out)

			if not os.path.exists(path):
				os.makedirs(path)

			with open(out, 'wb') as f:
				f.write(orjson.dumps(db, option=orjson.OPT_INDENT_2))

		pbar.update(10)

		return db
