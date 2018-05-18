#!/usr/bin/env python3
import sys
import os.path
import threading
from queue import Queue
from src.api import Api
from src.modules import LinkFinder
from src.modules import Spider
from src.api import TermColor

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
	#linkFinder = LinkFinder.LinkFinder()
	api = Api.Api()
	termc = TermColor.TermColor()
	#print(api.getDomainName('https://test.healthfella.co.uk/index.php'))
	#linkFinder.feed('<a href="ddsadsadsa">Test<div><div><div></a>')

	# Get user session vars
	userSettings = api.getUserSettings()

	#print(userSettings)
	REPO_PATH = userSettings['repoPath']
	REPO_NAME = userSettings['repoName']
	NUMBER_OF_THREADS = 4

	print (termc.HEADER + 'some text' + termc.ENDC)

# Basic top level param logic
if len(sys.argv[1:]) > 0 :
	arg1 = sys.argv[1:][0]
	topLevelCommands = ['--version', '--greeting', '--license', 'init', 'create', 'crawl']

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
		# The thread queue
		threadQueue = Queue()
		spider = Spider.Spider('healthfella', 'https://healthfella.com/', api.getDomainName('https://healthfella.com/'), REPO_PATH, REPO_NAME)