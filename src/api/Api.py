import os
from urllib.parse import urlparse

class Api :

	# Make a dictionary of name=value pairs from the hidden config file
	def getUserSettings(self) :
		userSettings = {}

		with open('/var/www/crawlbox/.cboxlocal') as myfile :
			for line in myfile :
				name, var = line.partition('=')[::2]
				userSettings[name.strip()] = var.strip('\n\t') # strip new lines and tabs from the file

		return userSettings

	# Setup a folder for a specific site
	def createRepo(self, name = '', path = '') :
		if not os.path.exists(path + '/' + name) :
			# Default no args
			if name == '' and path == '' :
				os.makedirs('~/crawlbox')
				print('Initialized empty repo with the name "crawlbox" in your home directory')

			# No path with a name arg	
			if path == '' and name != '' :
				print('Creating project dir ' + name)
				os.makedirs(name)
			else :
				# Name and path args
				print('Creating custom path project dir ' + name)

				# Save custom path in a static .txt file
				file = open('.cboxlocal', 'w')
				file.write('repoPath=' + path + '\n' + 'repoName=' + name)
				file.close()
				os.makedirs(path + '/' + name)
		else :
			print('Repository already exists')

	def createDataFiles(self, projectName, baseURL, path) :
		# Get user settings so we know where to create the files
		if os.path.isfile('/var/www/crawlbox/.cboxlocal') :
			queueDataPath = path + '/queue.txt'
			crawlDataPath = path + '/crawled.txt'

			if not os.path.isfile(queueDataPath) :
				self.writeFile(queueDataPath, baseURL)
				print('Queue data file created...')
			else :
				print('File already exists')

			if not os.path.isfile(crawlDataPath) :
				self.writeFile(crawlDataPath, '')
				print('Crawl data file created...')
			else :
				print('File already exists')
		else :
			print("\033[93m Config file not found.\033[0m")


	def createProject(self, projectName, baseURL, repoPath, repoName) :
		projectPath = repoPath + repoName + '/' + projectName

		if not os.path.exists(projectPath) :
			os.makedirs(projectPath)
			print('New project named' + projectName + ' created under the ' + repoName + ' repository, at the following location: ' + repoPath + repoName)
			self.createDataFiles(projectName, baseURL, projectPath)
		else :
			print('\033[91m Project already exists. \033[0m')

	# Create a new file
	def writeFile(self, path, data) :
		file = open(path, 'w+')
		file.write(data)
		file.close()

	def greet() :
		print('Welcome to crawlbox!')

	# Add data to an existing file
	def appendToFile(self, path, data) :
		with open(path, 'a') as file :
			file.write(data + '\n')

	# Delete the contents of a file
	def deleteFileContents(self, path) :
		with open(path, 'w'):
			pass # do nothing

	# Read a file and convert each line to set items
	def fileToSet(self, fileName) :
		results = set()

		with open(fileName, 'rt') as file :
			for row in file :
				results.add(row.replace('\n', ''))

		return results

	# Iterate through a set, and convert it to a line in a file
	def setToFile(self, links, fileName) :
		self.deleteFileContents(fileName)

		for link in sorted(links) :
			self.appendToFile(fileName, link)

	# Get sub domain name if exists
	def getSubDomainName(self, url) :
		try :
			return urlparse(url).netloc
		except:
			return ''

	# Get domain name
	def getDomainName(self, url) :
		try :
			res = self.getSubDomainName(url).split('.')

			if 'co.uk' not in url :
				return res[-2] + '.' + res[-1]
			else :
				return res[-3] + '.' + res[-2] + '.' + res[-1]
		except:
			return ''
