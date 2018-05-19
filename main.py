#!/usr/bin/env python3
import sys
import os
import os.path
from src.api import CB_Api
from src.modules import LinkFinder
from src.modules import CB_Spider
from src.api import TermColor
from src.modules import CB_Threaded_Spider

# Global vars
global REPO_PATH
global REPO_NAME
global PROJECT_PATH
global ACTIVE_PROJECT
global CONFIG_FILE_NAME
global INSTALLATION_STATUS
global NUMBER_OF_THREADS

CONFIG_FILE_NAME = '/var/www/crawlbox/.cboxlocal'

# Check if all config files are here
if not os.path.isfile(CONFIG_FILE_NAME) :
	print('Config file not found, cannot load user settings. Please cbox init a new working directory.')
	sys.exit()
else :
	# Instantiate base module objects so we can accses methods
	api = CB_Api.CB_Api()
	termc = TermColor.TermColor()

	# Get user session vars
	userSettings = api.getUserSettings()

	#print(userSettings)
	REPO_PATH = userSettings['repoPath']
	REPO_NAME = userSettings['repoName']
	NUMBER_OF_THREADS = 4
	ACTIVE_PROJECT = 'healthfella'

	#print (termc.HEADER + 'some text' + termc.ENDC)
	#print(str(len(api.fileToSet(REPO_PATH + REPO_NAME + '/' + 'healthfella/crawled.txt'))))

# Basic top level param logic
if len(sys.argv[1:]) > 0 :
	arg1 = sys.argv[1:][0]
	topLevelCommands = ['--version', '--greeting', '--license', 'init', 'create', 'crawl', 'flush', 'list']

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
		# Name of the project
		if (len(sys.argv[1:]) == 3) :
			name = sys.argv[1:][1]
			url = sys.argv[1:][2]
			api.createProject(name, url, REPO_PATH, REPO_NAME)
		else :
			print('\033[91m Invalid arguments supplied. Type "cbox --help create" for more info \033[0m')

	# Start a crawl process
	if arg1 in topLevelCommands and arg1 == 'crawl' :
		localParams = ['-r']

		if (len(sys.argv[1:]) == 1) :
			# The first spider
			print('regular search')
			spider = CB_Spider.CB_Spider('healthfella', 'https://healthfella.com/', api.getDomainName('https://healthfella.com/'), REPO_PATH, REPO_NAME, 0)
			spider.crawl('Spider 1', spider.baseURL)

		elif (len(sys.argv[1:]) == 2) :
			arg2 = sys.argv[1:][1]

			if arg2 in localParams :
				print('Initiating recursive search...')
				path = REPO_PATH + REPO_NAME
				threadedSpider = CB_Threaded_Spider.CB_Threaded_Spider(REPO_NAME, REPO_PATH)
				threadedSpider.createWorkers()
				threadedSpider.crawl(path)
			else :
				print('Invalid args supplied.')

	if arg1 in topLevelCommands and arg1 == 'flush' :
		if (len(sys.argv[1:]) == 2) :
			arg2 = sys.argv[1:][1]
			api.flushDataFiles(REPO_PATH, REPO_NAME, arg2)
		else :
			print('Invalid args')

	if arg1 in topLevelCommands and arg1 == 'list' :
		names = os.listdir(REPO_PATH + REPO_NAME)
		for i in names :
			if (i == ACTIVE_PROJECT) :
				print(i + '*')
			else :
				print(i)