import os
from urllib.parse import urlparse
from src.modules import CB_Worker
import threading
import shutil

class CB_Api :
		
	# Make a dictionary of name=value pairs from the hidden config file
	def getUserSettings(self) :
		userSettings = {}

		with open('/var/www/crawlbox/.cboxrc') as f :
			for line in f :
				name, var = line.partition('=')[::2]
				userSettings[name.strip()] = var.strip('\n\t') # strip new lines and tabs from the file

		return userSettings

	# Setup a folder for a specific site
	def createRepo(self, name = '', path = '', numThreads = 0) :
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
				file = open('/var/www/crawlbox/.cboxrc', 'w')
				file.write('repoPath=' + path + '\n' + 'repoName=' + name + '\n' + 'numThreads=' + str(numThreads))
				file.close()
				os.makedirs(path + '/' + name)
		else :
			print('Repository already exists')

	def createDataFiles(self, projectName, baseURL, path) :
		# Get user settings so we know where to create the files
		if os.path.isfile('/var/www/crawlbox/.cboxrc') :
			queueDataPath = path + '/queue.txt'
			crawlDataPath = path + '/crawled.txt'
			scriptsDataPath = path + '/scripts.txt'
			metaDataPath = path + '/meta.txt'
			stylesDataPath = path + '/styles.txt'

			if not os.path.isfile(queueDataPath) :
				self.writeFile(queueDataPath, baseURL)
				print('Queue data file created...')
			else :
				print('File already exists')

			if not os.path.isfile(scriptsDataPath) :
				self.writeFile(scriptsDataPath, '')
				print('Scripts data file created...')
			else :
				print('File already exists')

			if not os.path.isfile(metaDataPath) :
				self.writeFile(metaDataPath, '')
				print('Meta data file created...')
			else :
				print('File already exists')

			if not os.path.isfile(stylesDataPath) :
				self.writeFile(stylesDataPath, '')
				print('Meta data file created...')
			else :
				print('File already exists')

			if not os.path.isfile(crawlDataPath) :
				self.writeFile(crawlDataPath, '')
				print('Crawl data file created...')
			else :
				print('File already exists')
		else :
			print("\033[93m Config file not found.\033[0m")


	def createProject(self, projectName, baseURL, repoPath, repoName, configFile, active=False) :
		projectPath = repoPath + repoName + '/' + projectName

		if not os.path.exists(projectPath) :
			os.makedirs(projectPath)
			print('New project named' + projectName + ' created under the ' + repoName + ' repository, at the following location: ' + repoPath + repoName)
			self.createDataFiles(projectName, baseURL, projectPath)

			if active :
				# Chech to see if there is an active project
				userSettings = self.getUserSettings()
				#prj = userSettings['activeProject']
				if 'activeProject' in userSettings and userSettings['activeProject'] != 'none' :
					self.setActiveProject(configFile, projectName, baseURL)
					print('Active project changed to: ' + projectName)
				else :
					# Append an active project to the config file
					# Save custom path in a static .txt file
					file = open('/var/www/crawlbox/.cboxrc', 'w')
					file.write('repoPath=' + repoPath + '\n' + 'repoName=' + repoName + '\n' + 'numThreads=' + userSettings['numThreads'] + '\n' + 'activeProject="' + projectName + '"\n' + 'activeURL="' + baseURL + '"')
					file.close()
					print('Active project set to: ' + projectName)
		else :
			print('\033[91m Project already exists. \033[0m')

	# Create a new file
	def writeFile(self, path, data) :
		file = open(path, 'w+')
		file.write(data)
		file.close()

	def setActiveProject(self, path, projectName, projectURL) :
		userSettings = self.getUserSettings()
		
		with open(path, 'r') as file :
			fileData = file.read()

		# Update active project
		newdata = fileData.replace(userSettings['activeProject'], '"' + projectName + '"')

		with open(path, 'w') as file :
			file.write(newdata)

		# Update active project url
		with open(path, 'r') as file :
			fileData = file.read()

		# Replace
		newdata = fileData.replace(userSettings['activeURL'], '"' + projectURL + '"')

		with open(path, 'w') as file :
			file.write(newdata)

	def getActiveProject() :
		userSettings = self.getUserSettings()
		return userSettings['activeProject']

	def greet() :
		print('Welcome to crawlbox!')

	# Add data to an existing file
	def appendToFile(self, path, data) :
		with open(path, 'a') as file :
			file.write(data + '\n')

	# Delete the contents of a file
	def deleteFileContents(self, path) :
		open(path, 'w').close()

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

	# Flush project and set files to initial state
	def flushDataFiles(self, repoPath, repoName, projectName, projectURL) :
		projectPath = repoPath + repoName + '/' + projectName
		self.deleteFileContents(projectPath + '/queue.txt')
		self.deleteFileContents(projectPath + '/crawled.txt')
		self.deleteFileContents(projectPath + '/scripts.txt')
		self.deleteFileContents(projectPath + '/meta.txt')
		self.deleteFileContents(projectPath + '/styles.txt')

		# Reset to initial state
		self.appendToFile(projectPath + '/queue.txt', projectURL)
		print('Flushing ' + projectName + ', at: ' + projectPath)

	def removeProject(self, repoPath, repoName, projectName) :
		userSettings = self.getUserSettings()
		path = repoPath + repoName + '/' + projectName

		# Check if it is the active project, recreate the config file
		if userSettings['activeProject'] == projectName :
			print('Removing the active project. Update config file')
			# Save custom path in a static .txt file
			file = open('/var/www/crawlbox/.cboxrc', 'w')
			file.write('repoPath=' + repoPath + '\n' + 'repoName=' + repoName + '\n' + 'numThreads=' + userSettings['numThreads'] + '\n' + 'activeProject=none' + '\n' + 'activeURL=none')
			file.close()

		if os.path.exists(path) :
			shutil.rmtree(path)
			print(projectName + ' permanently removed.')

	def removeRepo(self, repoPath, repoName, configFile) :
		print('Removing the active repository')
		path = repoPath + repoName

		if os.path.exists(path) :
			shutil.rmtree(path)
			print(repoName + ' permanently removed.')

		# Remove config file
		self.deleteFileContents(configFile)
		print('Removed repo config')
	def regenConfigFile(self) :
		print('Regen config')

	def getUserConfig(self) :
		userSettings = self.getUserSettings()
		print(userSettings)