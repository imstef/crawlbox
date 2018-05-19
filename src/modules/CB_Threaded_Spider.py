import threading
from queue import Queue
from src.api import CB_Api
from src.modules import CB_Spider

class CB_Threaded_Spider :
	queue = ''
	api = ''
	repoName = ''
	repoPath = ''
	spider = ''

	def __init__(self, repoName, repoPath) :
		CB_Threaded_Spider.queue = Queue()
		CB_Threaded_Spider.api = CB_Api.CB_Api()
		CB_Threaded_Spider.repoName = repoName
		CB_Threaded_Spider.repoPath = repoPath
		CB_Threaded_Spider.spider = CB_Spider.CB_Spider('healthfella', 'https://healthfella.com/', CB_Threaded_Spider.api.getDomainName('https://healthfella.com/'), repoPath, repoName, 2)

	# Create worker threads (will die when main exits)
	@staticmethod
	def createWorkers() :
		for _ in range(4):
			t = threading.Thread(target=CB_Threaded_Spider.work)
			t.daemon = True
			t.start()

	# Do the next job in the queue
	@staticmethod
	def work() :
		while True:
			url = CB_Threaded_Spider.queue.get()
			CB_Threaded_Spider.spider.crawl(threading.current_thread().name, url)
			CB_Threaded_Spider.queue.task_done()

	# Each queued link is a new job
	@staticmethod
	def createJobs(path) :
		for link in CB_Threaded_Spider.api.fileToSet(path + '/healthfella/queue.txt'):
			CB_Threaded_Spider.queue.put(link)
		CB_Threaded_Spider.queue.join()
		CB_Threaded_Spider.crawl(path)

	# Check if there are items in the queue, if so crawl them
	@staticmethod
	def crawl(path) :
		queuedLinks = CB_Threaded_Spider.api.fileToSet(path + '/healthfella/queue.txt')
		crawledLinks = CB_Threaded_Spider.api.fileToSet(path + '/healthfella/crawled.txt')
		if len(queuedLinks) > 0:
			#print(str(len(queuedLinks)) + ' links in the queue')
			CB_Threaded_Spider.createJobs(path)
		else :
			print('Domain fully crawled (' + str(len(crawledLinks)) + ' links found).')