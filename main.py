#!/usr/bin/env python3
import sys
import os
import os.path
from src.api import CB_Api
from src.modules import CB_Worker
from src.api import CB_TermColor
from src.modules import CB_ThreadedWorker

# Global vars
global REPO_PATH
global REPO_NAME
global PROJECT_PATH
global ACTIVE_PROJECT
global ACTIVE_PROJECT_URL
global CONFIG_FILE_PATH
global INSTALLATION_STATUS
global NUMBER_OF_THREADS

CONFIG_FILE_PATH = '/var/www/crawlbox/.cboxrc'

# Instantiate base module objects so we can accses methods
api = CB_Api.CB_Api()
termc = CB_TermColor.CB_TermColor()

# Check if all config files are here
if not os.path.isfile(CONFIG_FILE_PATH) :
	print('Config file not found, cannot load user settings. Please cbox init a new working directory.')
	#sys.exit()
else :
	# Get user session vars
	userSettings = api.getUserSettings()

	if 'numThreads' in userSettings :
		NUMBER_OF_THREADS = userSettings['numThreads']
	else :
		NUMBER_OF_THREADS = 2

	#print(userSettings)
	if 'repoPath' in userSettings :
		REPO_PATH = userSettings['repoPath']
	else :
		REPO_PATH = ''

	if 'repoName' in userSettings :
		REPO_NAME = userSettings['repoName']
	else :
		REPO_NAME = ''
	
	if 'activeProject' in userSettings :
		ACTIVE_PROJECT = userSettings['activeProject']
	else :
		ACTIVE_PROJECT = ''
	if 'activeURL' in userSettings :
		ACTIVE_PROJECT_URL = userSettings['activeURL']
	else :
		ACTIVE_PROJECT_URL = ''

	#print (termc.HEADER + 'some text' + termc.ENDC)
	#print(str(len(api.fileToSet(REPO_PATH + REPO_NAME + '/' + 'healthfella/crawled.txt'))))
	print(termc.WARNING + 'Crawlbox 0.1' + termc.ENDC)

# Basic top level param logic
if len(sys.argv[1:]) > 0 :
	args = sys.argv[1:]
	arg1 = sys.argv[1:][0]
	topLevelCommands = ['--version', '--greeting', '--license', '--config', 'init', 'create', 'scrape', 'flush', 'list', 'set', 'status', 'remove', 'report']

	# Starting point of the program which loads different aspects of the functionality depending on the commands that are passed
	if not arg1 in topLevelCommands :
		print('\033[91m Invalid arguments supplied. Type "cbox --help" for more info \033[0m')
		sys.exit()

	# The version arg
	if arg1 in topLevelCommands and arg1 == '--version' :
		print('0.0.1')

	# The license arg
	if arg1 in topLevelCommands and arg1 == '--license' :
		localParams = ['short']

		if len(sys.argv[1:]) == 2 :
			arg2 = sys.argv[1:][1]

			if arg2 in localParams and arg2 == 'short' :
				print('License: GNU General Public License Version 2 (GPL v2)')
		else :
			# Only 1 param passed
			print('License: GNU General Public License Version 2 (GPL v2) (License URL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)')

	# The greeting arg
	if arg1 in topLevelCommands and arg1 == '--greeting' :
		print('Welcome to crawlbox!')

	if arg1 in topLevelCommands and arg1 == '--config' :
		api.getUserConfig()

	# Init a new repo
	if arg1 in topLevelCommands and arg1 == 'init' :
		# Name of the repo
		if (len(sys.argv[1:]) == 2) :
			name = sys.argv[1:][1]
			api.createRepo(name)
		elif (len(sys.argv[1:]) == 3) :
			name = sys.argv[1:][1]
			path = sys.argv[1:][2]
			api.createRepo(name, path)
		else :
			api.createRepo()

	# Create a new project
	if arg1 in topLevelCommands and arg1 == 'create' :
		localParams = ['-a']
		# Name of the project
		if (len(sys.argv[1:]) == 3) :
			name = sys.argv[1:][1]
			url = sys.argv[1:][2]
			api.createProject(name, url, REPO_PATH, REPO_NAME, CONFIG_FILE_PATH)
		elif len(args) == 4:
			if args[3] in localParams and args[3] == '-a' :
				name = args[1]
				url = args[2]
				api.createProject(name, url, REPO_PATH, REPO_NAME, CONFIG_FILE_PATH, True)
		else :
			print('\033[91m Invalid arguments supplied. Type "cbox --help create" for more info \033[0m')

	# Start a crawl process
	if arg1 in topLevelCommands and arg1 == 'scrape' :
		localParams = ['-r', '--force']

		if (len(args) == 1) :
			# Crawl for the active project
			spider = CB_Worker.CB_Worker('', ACTIVE_PROJECT, ACTIVE_PROJECT_URL, api.getDomainName(ACTIVE_PROJECT_URL), REPO_PATH, REPO_NAME, 2)
			spider.crawl('Spider 1', spider.baseURL)
		elif len(args) == 2 :
			# Crawl recursively for the active project
			arg2 = args[1]
			path = REPO_PATH + REPO_NAME
			if arg2 in localParams and arg2 == '-r' :
				#print('Initiating recursive search...')
				threadedSpider = CB_ThreadedWorker.CB_ThreadedWorker('r', NUMBER_OF_THREADS, ACTIVE_PROJECT, ACTIVE_PROJECT_URL, api.getDomainName(ACTIVE_PROJECT_URL), REPO_PATH, REPO_NAME, 2)
				threadedSpider.createWorkers()
				threadedSpider.crawl(path)
			elif arg2 in localParams and arg2 == '--force' :
				api.flushDataFiles(REPO_PATH, REPO_NAME, ACTIVE_PROJECT, ACTIVE_PROJECT_URL)
				spider = CB_Worker.CB_Worker('', ACTIVE_PROJECT, ACTIVE_PROJECT_URL, api.getDomainName(ACTIVE_PROJECT_URL), REPO_PATH, REPO_NAME, 2)
				spider.crawl('Spider 1', spider.baseURL)
			else :
				print(termc.FAIL + 'Invalid arguments supplied. Please check "cbox --help scrape" for further instructions.' + termc.ENDC)
		elif len(args) == 4 :
			projectName = args[1]
			projectURL = args[2]
			arg3 = args[3]
			if arg3 in localParams and arg3 == '-r' :
				print('Recursive custom search')

	if arg1 in topLevelCommands and arg1 == 'flush' :
		if len(args) == 1 :
			path = REPO_PATH + REPO_NAME + '/' + ACTIVE_PROJECT
			if os.path.exists(path) :
				api.flushDataFiles(REPO_PATH, REPO_NAME, ACTIVE_PROJECT, ACTIVE_PROJECT_URL)
		
		elif len(args) == 2 :
			path = REPO_PATH + REPO_NAME + '/' + args[1]
			queue = api.fileToSet(path + '/queue.txt')
			crawled = api.fileToSet(path + '/crawled.txt')
			if os.path.exists(path) :
				# Get the URL from queue.txt
				if len(queue) == 1 :
					with open(path + '/queue.txt', 'r') as file :
						baseURL = [line.rstrip() for line in file]
				else :
					with open(path + '/crawled.txt', 'r') as file :
						baseURL = [line.rstrip() for line in file]

				#print(baseURL)
				api.flushDataFiles(REPO_PATH, REPO_NAME, args[1], baseURL[0])
		else :
			print('Invalid args')

	if arg1 in topLevelCommands and arg1 == 'list' :
		names = os.listdir(REPO_PATH + REPO_NAME)
		for i in names :
			if i == ACTIVE_PROJECT :
				print(i + termc.HEADER + '*' + termc.ENDC)
			else :
				print(i)

	if arg1 in topLevelCommands and arg1 == 'set' :
		localParams = ['active', 'threads']
		if args[1] in localParams and args[1] == 'active' :
			path = REPO_PATH + REPO_NAME + '/' + args[2]
			if os.path.exists(path) :
				# Get the URL from queue.txt
				with open(path + '/queue.txt', 'r') as file :
					baseURL = file.read()

				if not userSettings['activeProject'] == args[2] :
					api.setActiveProject(CONFIG_FILE_PATH, args[2], baseURL)
					print('Actie project set to ' + termc.OKBLUE + args[2] + termc.ENDC)
				else :
					print(termc.FAIL + args[2] + ' already active.' + termc.ENDC)
			else :
				print('Invalid project name!')
		elif args[1] in localParams and args[1] == 'threads' :
				with open(CONFIG_FILE_PATH, 'r') as file :
					fileData = file.read()

				# Update active project
				newdata = fileData.replace(userSettings['numThreads'], args[2])

				with open(CONFIG_FILE_PATH, 'w') as file :
					file.write(newdata)

				print(termc.OKGREEN + 'Config file updated.' + termc.ENDC)

	if arg1 in topLevelCommands and arg1 == 'status' :
		if not ACTIVE_PROJECT or not ACTIVE_PROJECT_URL :
			print('No active project set.')
		else :
			print('Active project: ' + termc.OKBLUE + userSettings['activeProject'] + termc.ENDC + ' (' + userSettings['repoName'] + ', ' + userSettings['activeURL'] + ')')

	if arg1 in topLevelCommands and arg1 == 'report' :
		if len(args) == 1 :
			path = REPO_PATH + REPO_NAME + '/' + ACTIVE_PROJECT
			queue = api.fileToSet(path + '/queue.txt')
			crawled = api.fileToSet(path + '/crawled.txt')
			scripts = api.fileToSet(path + '/scripts.txt')
			meta = api.fileToSet(path + '/meta.txt')
			styles = api.fileToSet(path + '/styles.txt')

			print('Showing stats for ' + ACTIVE_PROJECT + ' (' + ACTIVE_PROJECT_URL + ')')
			print('Links Crawled: ' + str(len(crawled)) + ' | Links Queued: ' + str(len(queue)))
			print('Scripts found: ' + str(len(scripts)))
			print('Meta info found: ' + str(len(meta)))
			print('Styles found: ' + str(len(styles)))

		elif len(args) == 2 :
			path = REPO_PATH + REPO_NAME + '/' + args[1]
			queue = api.fileToSet(path + '/queue.txt')
			crawled = api.fileToSet(path + '/crawled.txt')
			scripts = api.fileToSet(path + '/scripts.txt')
			meta = api.fileToSet(path + '/meta.txt')
			styles = api.fileToSet(path + '/styles.txt')

			if len(queue) == 1 :
				# Get the URL from queue.txt
				with open(path + '/queue.txt', 'r') as file :
					baseURL = [line.rstrip() for line in file]
			else :
				# Get the URL from queue.txt
				with open(path + '/crawled.txt', 'r') as file :
					baseURL = [line.rstrip() for line in file]

			print('Showing stats for ' + args[1] + ' (' + baseURL[0] + ')')
			print('Links Crawled: ' + str(len(crawled)) + ' | Links Queued: ' + str(len(queue)))
			print('Scripts found: ' + str(len(scripts)))
			print('Meta info found: ' + str(len(meta)))
			print('Styles found: ' + str(len(styles)))

	if arg1 in topLevelCommands and arg1 == 'remove' :
		if len(args) == 1 :
			api.removeProject(REPO_PATH, REPO_NAME, ACTIVE_PROJECT)
		elif len(args) == 2 :
			api.removeProject(REPO_PATH, REPO_NAME, args[1])