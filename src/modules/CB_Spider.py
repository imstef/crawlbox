from urllib.request import Request, urlopen
from src.modules import LinkFinder
from queue import Queue
from src.api import CB_Api
from src.api import TermColor
import sys

class CB_Spider :
	# A class var is shared among all instances of the class
	projectName = ''
	baseURL = ''
	domainName = ''
	queueFile = ''
	crawledFile = ''
	queueSet = set()
	reportType = 0
	crawledSet = set()
	termColor = ''

	def __init__(self, projectName, baseURL, domainName, repoPath, repoName, reportType) :
		CB_Spider.projectName = projectName
		CB_Spider.baseURL = baseURL
		CB_Spider.domainName = domainName
		CB_Spider.reportType = reportType
		CB_Spider.queueFile = repoPath + repoName + '/' + CB_Spider.projectName + '/queue.txt'
		CB_Spider.crawledFile =  repoPath + repoName + '/' + CB_Spider.projectName + '/crawled.txt'
		CB_Spider.boot()
		CB_Spider.termColor = TermColor.TermColor()
		#print('Spider object created!')

	@staticmethod
	def boot() :
		# Get all the data from the files and convert them to a set we can use
		api = CB_Api.CB_Api()
		CB_Spider.queueSet = api.fileToSet(CB_Spider.queueFile)
		CB_Spider.crawledSet = api.fileToSet(CB_Spider.crawledFile)

	@staticmethod
	def crawl(threadName, pageURL) :
		# Check if you already crawled the page
		if pageURL not in CB_Spider.crawledSet :
			if CB_Spider.reportType == 0 :
				sys.stdout.write(CB_Spider.termColor.HEADER + "Overall Progress " + CB_Spider.termColor.ENDC + "(Queue/Crawled): %d / %d \r" % (int(len(CB_Spider.queueSet)), int(len(CB_Spider.crawledSet))))
				sys.stdout.flush()
			elif CB_Spider.reportType == 1 :
				sys.stdout.write(CB_Spider.termColor.HEADER + "Overall Progress " + CB_Spider.termColor.ENDC + "(Queue/Crawled): %d / %d / %s  \r" % (int(len(CB_Spider.queueSet)), int(len(CB_Spider.crawledSet)), threadName))
				sys.stdout.flush()
			elif CB_Spider.reportType == 2 :
				print(threadName + ' is crawling ' + pageURL)
				# crawlStatus = 'Queue: ' + str(len(CB_Spider.queueSet)) + ', Crawled :' + str(len(CB_Spider.crawledSet))
				# print(crawlStatus)
			
			CB_Spider.addLinksToQueue(CB_Spider.seek(pageURL))

			# Remove from the waiting list and put it in crawled file
			if not len(CB_Spider.queueSet) == 1 :
				CB_Spider.queueSet.remove(pageURL)
				CB_Spider.crawledSet.add(pageURL)

				if CB_Spider.reportType == 2 :
					print(pageURL + ' crawled')

				# Update the acual files that hold the data so all threads have the most updated info
				CB_Spider.updateDataFiles()
			else :
				CB_Spider.queueSet.remove(pageURL)
				CB_Spider.crawledSet.add(pageURL)

				if CB_Spider.reportType == 2 :
					print(pageURL + ' crawled')

				# Update the acual files that hold the data so all threads have the most updated info
				CB_Spider.updateDataFiles()

				if CB_Spider.reportType == 2 :
					print('Crawling for domain finished. Total links crawled: ' + str(len(CB_Spider.crawledSet)))
		else :
			print('Page url already crawled!')

	@staticmethod
	def seek(pageURL) :
		htmlString = ''

		# Connect to the page and try to get the DOM from the URL in bytes
		try :
			# Workaround for 403 forbidden error when servers try to block spiders and crawlers
			req = Request(pageURL, headers={'User-Agent': 'Mozilla/5.0'})
			res = urlopen(req)

			# Make sure we're connecting to a web page
			if 'text/html' in res.getheader('Content-Type') :
				if CB_Spider.reportType == 2 :
					print('Carwling ' + pageURL)

				htmlBytes = res.read()
				htmlString = htmlBytes.decode('utf-8')

			finder = LinkFinder.LinkFinder(CB_Spider.baseURL, pageURL)
			finder.feed(htmlString)
		except Exception as e :
			print(str(e))
			# There were no links so return an empty set
			return set()

		return finder.getPageLinks()

	# Add collected links to the queue
	@staticmethod
	def addLinksToQueue(links) :
		api = CB_Api.CB_Api()
		for url in links :
			# If a link is in the queue or already crawled skip it
			if (url in CB_Spider.queueSet) or (url in CB_Spider.crawledSet) :
				continue
			# Make sure to only crawl links within the domain
			if CB_Spider.domainName != api.getDomainName(url):
				continue

			# all looks good, add the links to the queue set
			CB_Spider.queueSet.add(url)

	@staticmethod
	def updateDataFiles() :
		api = CB_Api.CB_Api()
		api.setToFile(CB_Spider.queueSet, CB_Spider.queueFile)
		api.setToFile(CB_Spider.crawledSet, CB_Spider.crawledFile)