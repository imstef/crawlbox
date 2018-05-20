import threading
from queue import Queue
from src.api import CB_Api
from src.modules import CB_Worker

class CB_ThreadedWorker :
	queue = ''
	api = ''
	repoName = ''
	repoPath = ''
	projectName = ''
	baseURL = ''
	domainName = ''
	spider = ''

	def __init__(self, jobType, projectName, baseURL, domainName, repoPath, repoName, reportType) :
		CB_ThreadedWorker.queue = Queue()
		CB_ThreadedWorker.api = CB_Api.CB_Api()
		CB_ThreadedWorker.repoName = repoName
		CB_ThreadedWorker.repoPath = repoPath
		CB_ThreadedWorker.baseURL = baseURL
		CB_ThreadedWorker.projectName = projectName
		CB_ThreadedWorker.spider = CB_Worker.CB_Worker(jobType, projectName, baseURL, CB_ThreadedWorker.api.getDomainName(baseURL), repoPath, repoName, reportType)

	# Create worker threads (will die when main exits)
	@staticmethod
	def createWorkers() :
		for _ in range(4):
			t = threading.Thread(target=CB_ThreadedWorker.work)
			t.daemon = True
			t.start()

	# Do the next job in the queue
	@staticmethod
	def work() :
		while True:
			url = CB_ThreadedWorker.queue.get()
			CB_ThreadedWorker.spider.crawl(threading.current_thread().name, url)
			CB_ThreadedWorker.queue.task_done()

	# Each queued link is a new job
	@staticmethod
	def createJobs(path) :
		for link in CB_ThreadedWorker.api.fileToSet(path + '/' + CB_ThreadedWorker.projectName + '/queue.txt'):
			CB_ThreadedWorker.queue.put(link)
		CB_ThreadedWorker.queue.join()
		CB_ThreadedWorker.crawl(path)

	# Check if there are items in the queue, if so crawl them
	@staticmethod
	def crawl(path) :
		queuedLinks = CB_ThreadedWorker.api.fileToSet(path + '/' + CB_ThreadedWorker.projectName + '/queue.txt')
		crawledLinks = CB_ThreadedWorker.api.fileToSet(path + '/' + CB_ThreadedWorker.projectName + '/crawled.txt')
		if len(queuedLinks) > 0:
			#print(str(len(queuedLinks)) + ' links in the queue')
			CB_ThreadedWorker.createJobs(path)
		else :
			print('Crawling for domain finished. Total links crawled: ' + str(len(crawledLinks)))