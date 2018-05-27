from urllib.request import Request, urlopen
from src.modules import CB_Parser
from queue import Queue
from src.api import CB_Api
from src.api import CB_TermColor
import time
import sys

class CB_Worker :
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
	emails = set()
	scriptsSet = set()
	metaSet = set()
	stylesSet = set()
	jobType = ''

	def __init__(self, jobType, projectName, baseURL, domainName, repoPath, repoName, reportType) :
		CB_Worker.projectName = projectName
		CB_Worker.baseURL = baseURL
		CB_Worker.domainName = domainName
		CB_Worker.reportType = reportType
		CB_Worker.jobType = jobType
		CB_Worker.queueFile = repoPath + repoName + '/' + projectName + '/queue.txt'
		CB_Worker.crawledFile =  repoPath + repoName + '/' + projectName + '/crawled.txt'
		CB_Worker.scriptsFile = repoPath + repoName + '/' + projectName + '/scripts.txt'
		CB_Worker.metaFile = repoPath + repoName + '/' + projectName + '/meta.txt'
		CB_Worker.stylesFile = repoPath + repoName + '/' + projectName + '/styles.txt'
		CB_Worker.boot()
		CB_Worker.termColor = CB_TermColor.CB_TermColor()
		#print('Spider object created!')

	@staticmethod
	def boot() :
		# Get all the data from the files and convert them to a set we can use
		api = CB_Api.CB_Api()
		CB_Worker.queueSet = api.fileToSet(CB_Worker.queueFile)
		CB_Worker.crawledSet = api.fileToSet(CB_Worker.crawledFile)
		CB_Worker.scriptsSet = api.fileToSet(CB_Worker.scriptsFile)
		CB_Worker.metaSet = api.fileToSet(CB_Worker.metaFile)
		CB_Worker.stylesSet = api.fileToSet(CB_Worker.stylesFile)

	@staticmethod
	def crawl(threadName, pageURL) :
		# Check if you already crawled the page
		if pageURL not in CB_Worker.crawledSet :
			processStart = time.time()
			if CB_Worker.reportType == 0 :
				sys.stdout.write(CB_Worker.termColor.HEADER + "Overall Progress " + CB_Worker.termColor.ENDC + "(Queue/Crawled): %d / %d \r" % (int(len(CB_Worker.queueSet)), int(len(CB_Worker.crawledSet))))
				sys.stdout.flush()
			elif CB_Worker.reportType == 1 :
				sys.stdout.write(CB_Worker.termColor.HEADER + "Overall Progress " + CB_Worker.termColor.ENDC + "(Queue/Crawled): %d / %d / %s  \r" % (int(len(CB_Worker.queueSet)), int(len(CB_Worker.crawledSet)), threadName))
				sys.stdout.flush()
			elif CB_Worker.reportType == 2 :
				print(threadName + ' is crawling ' + pageURL)
				# crawlStatus = 'Queue: ' + str(len(CB_Worker.queueSet)) + ', Crawled :' + str(len(CB_Worker.crawledSet))
				# print(crawlStatus)
			
			CB_Worker.addLinksToQueue(CB_Worker.seek(pageURL))
			
			# Remove from the waiting list and put it in crawled file
			if not len(CB_Worker.queueSet) == 1 :
				CB_Worker.queueSet.remove(pageURL)
				CB_Worker.crawledSet.add(pageURL)

				# Update the acual files that hold the data so all threads have the most updated info
				CB_Worker.updateDataFiles()
				processEnd = time.time()

				if CB_Worker.reportType == 2 :
					print(CB_Worker.termColor.HEADER +'[URL] ' + CB_Worker.termColor.ENDC + pageURL + CB_Worker.termColor.OKGREEN + ' crawled (' + str(round(processEnd - processStart, 2)) + ' seconds).' + CB_Worker.termColor.ENDC)
					#print(CB_Worker.emails)
			else :
				CB_Worker.queueSet.remove(pageURL)
				CB_Worker.crawledSet.add(pageURL)
				processEnd = time.time()
				# Update the acual files that hold the data so all threads have the most updated info
				CB_Worker.updateDataFiles()

				if CB_Worker.reportType == 2 :
					print(CB_Worker.termColor.HEADER +'[URL] ' + CB_Worker.termColor.ENDC + pageURL + CB_Worker.termColor.OKGREEN + ' crawled (' + str(round(processEnd - processStart, 2)) + ' seconds).' + CB_Worker.termColor.ENDC)
					print('Links (queued/crawled): ' + str(len(CB_Worker.queueSet)) + ' / ' + str(len(CB_Worker.crawledSet)))
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
				#if CB_Worker.reportType == 2 :
					#print('Carwling ' + pageURL)

				htmlBytes = res.read()
				htmlString = htmlBytes.decode('utf-8')

			finder = CB_Parser.CB_Parser(CB_Worker.jobType, CB_Worker.baseURL, pageURL)
			finder.feed(htmlString)
		except Exception as e :
			print(str(e))
			# There were no links so return an empty set
			return set()

		if CB_Worker.jobType != 'r' :
			#CB_Worker.emails = finder.getPageEmails()
			CB_Worker.scriptsSet = finder.getPageScripts()
			CB_Worker.metaSet = finder.getPageMeta()
			CB_Worker.stylesSet = finder.getPageStylesheets()
			CB_Worker.emails = finder.getPageEmails()

			print('Scripts: ' + str(len(CB_Worker.scriptsSet)))
			print('Meta: ' + str(len(CB_Worker.metaSet)))
			print('Styles: ' + str(len(CB_Worker.stylesSet)))
			print('Emails: ' + str(len(CB_Worker.emails)))
			print(CB_Worker.emails)
			#print(CB_Worker.metaSet)
			#print(CB_Worker.stylesSet)

		return finder.getPageLinks()

	# Add collected links to the queue
	@staticmethod
	def addLinksToQueue(links) :
		api = CB_Api.CB_Api()
		for url in links :
			# If a link is in the queue or already crawled skip it
			if (url in CB_Worker.queueSet) or (url in CB_Worker.crawledSet) :
				continue
			# Make sure to only crawl links within the domain
			if CB_Worker.domainName != api.getDomainName(url):
				continue

			# all looks good, add the links to the queue set
			CB_Worker.queueSet.add(url)

	@staticmethod
	def updateDataFiles() :
		api = CB_Api.CB_Api()
		api.setToFile(CB_Worker.queueSet, CB_Worker.queueFile)
		api.setToFile(CB_Worker.crawledSet, CB_Worker.crawledFile)
		api.setToFile(CB_Worker.scriptsSet, CB_Worker.scriptsFile)
		api.setToFile(CB_Worker.metaSet, CB_Worker.metaFile)
		api.setToFile(CB_Worker.stylesSet, CB_Worker.stylesFile)