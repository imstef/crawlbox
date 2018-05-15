#!/usr/bin/env python3
import sys
from src.api import api

api.cbGreet()

# Basic top level param logic
if len(sys.argv[1:]) > 0 :
	arg1 = sys.argv[1:][0]
	topLevelCommands = ['--version', '--greeting', '--license', 'create']

	# Starting point of the program which loads different aspects of the functionality depending on the commands that are passed

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

	# Create a new repo
	if arg1 in topLevelCommands and arg1 == 'create' :
		
		# Name of the repo
		if (len(sys.argv[1:]) == 2) :
			name = sys.argv[1:][1]
			api.cbCreateProjectDir(name)
			print('Created dir in home folder with name: ' + name)
		elif (len(sys.argv[1:]) == 3) :
			name = sys.argv[1:][1]
			path = sys.argv[1:][2]
			print('Create dir with name ' + name +  ' in the following path: ' + path)
		else :
			print('Create a repo in the home folder with basic name')