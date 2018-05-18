from urllib.request import Request, urlopen
from src.modules import LinkFinder
from src.api import Api

class Spider :

	# A class var is shared among all instances of the class
	projectName = ''
	baseURL = ''
	domainName = ''
	queueFile = ''
	crawledFile = ''
	queueSet = set()
	crawledSet = set()

	def __init__(self, projectName, baseURL, domainName, repoPath, repoName) :
		Spider.projectName = projectName
		Spider.baseURL = baseURL
		Spider.domainName = domainName
		Spider.queueFile = repoPath + repoName + '/' + Spider.projectName + '/queue.txt'
		Spider.crawledFile =  repoPath + repoName + '/' + Spider.projectName + '/crawled.txt'
		self.boot()
		self.crawl('Spider 1', Spider.baseURL)

	@staticmethod
	def boot() :
		# Get all the data from the files and convert them to a set we can use
		api = Api.Api()
		Spider.queueSet = api.fileToSet(Spider.queueFile)
		Spider.crawlSet = api.fileToSet(Spider.crawledFile)

	@staticmethod
	def crawl(threadName, pageURL) :
		# Check if you already crawled the page
		if pageURL not in Spider.crawledSet :
			print(threadName + ' is crawling ' + pageURL)
			print('Queue: ' + str(len(Spider.queueSet)) + ', Crawled :' + str(len(Spider.crawledSet)))
			Spider.addLinksToQueue(Spider.seek(pageURL))

			# Remove from the waiting list and put it in crawled file
			Spider.queueSet.remove(pageURL)
			Spider.crawledSet.add(pageURL)
			print(pageURL + ' moved from queue to crawled')

			# Update the acual files that hold the data so all threads have the most updated info
			Spider.updateDataFiles()
			print('Data files updated')
		else :
			print('Crawling for domain finished')

	@staticmethod
	def seek(pageURL) :
		DOMString = ''

		# Connect to the page and try to get the DOM from the URL in bytes
		try :
			# Workaround for 403 forbidden error when servers try to block spiders and crawlers
			req = Request(pageURL, headers={'User-Agent': 'Mozilla/5.0'})
			res = urlopen(req)

			# Make sure we're connecting to a web page
			if 'text/html' in res.getheader('Content-Type') :
				print('read response from remote link and process data')
				DOMBytes = res.read()
				DOMString = DOMBytes.decode('utf-8')

			finder = LinkFinder.LinkFinder(Spider.baseURL, pageURL)
			finder.feed(DOMString)
		except Exception as e :
			print(str(e))
			# There were no links so return an empty set
			return set()

		return finder.getPageLinks()

	# Add collected links to the queue
	@staticmethod
	def addLinksToQueue(links) :
		api = CrawlboxApi.CrawlboxApi()
		for url in links :
			# If a link is in the queue or already crawled skip it
			if (url in Spider.queueSet) or (url in Spider.crawlSet) :
				continue
			# Make sure to only crawl links within the domain
			if Spider.domainName != api.getDomainName(url):
				continue
			# all looks good, add the links to the queue set
			print(url + ' ' + "\033[92m" + "added!" + "\033[0m")
			Spider.queueSet.add(url)

	@staticmethod
	def updateDataFiles() :
		api = CrawlboxApi.CrawlboxApi()
		api.setToFile(Spider.queueSet, Spider.queueFile)
		api.setToFile(Spider.crawledSet, Spider.crawledFile)