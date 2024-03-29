################################################################################
#                                                                              #
#                               fetch_project.py                               #
#                                                                              #
################################################################################
#                                                                              #
#        This is a utility for fetching projects from the GitLab API           #
#                                                                              #
#        Author(s): Abe Megahed                                                #
#                                                                              #
#        This file is subject to the terms and conditions defined in           #
#        'LICENSE.txt', which is part of this source code distribution.        #
#                                                                              #
################################################################################
#  Copyright (C) 2024 Data Science Institute, Univeristy of Wisconsin-Madison  #
################################################################################

from models.project import Project 
import mysql.connector

#
# globals
#

table = 'projects';

#
# main
#

# connect to database
#
try:
	db = mysql.connector.connect(
		host = "localhost",
		user = "root",
		password = "root",
		database = "gitlab"
	)
except:
	print("No database found.")
	exit()

# fetch and store project
#
Project.fetch_by_id(db, table, 13771)