import os

# Setup a folder for a specific site
def cbCreateProjectDir(directory, path = 'rel') :
	if not os.path.exists(directory) :
		if path == 'rel':
			print('Creating project dir ' + directory)
			os.makedirs(directory)
		else :
			print('Creating custom path project dir ' + directory)
			os.makedirs(path + '/' + directory)
	else :
		print('Repository already exists')

def cbCreateDataFiles(projectName, baseURL) :
	queue = projectName + '/queue.txt'
	crawled = projectName + '/crawled.txt'

	if not os.path.isFile(queue) :
		cbWriteFile(queue, baseURL)

	if not os.path.isFile(crawled) :
		cbWwriteFile(crawled, '')

# Create a new file
def cbWriteFile(path, data) :
	file = open(path, 'w')
	file.write(data)
	file.close()

def cbGreet() :
	print('Welcome to crawlbox!')