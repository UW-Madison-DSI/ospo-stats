################################################################################
#                                                                              #
#                          fetch_dsi_repositories.py                           #
#                                                                              #
################################################################################
#                                                                              #
#        This is a utility for fetching repositories from the GitHub API       #
#        belonging to the University of Wisconsin Data Science Institute.      #
#                                                                              #
#        Author(s): Abe Megahed                                                #
#                                                                              #
#        This file is subject to the terms and conditions defined in           #
#        'LICENSE.txt', which is part of this source code distribution.        #
#                                                                              #
################################################################################
#  Copyright (C) 2024 Data Science Institute, Univeristy of Wisconsin-Madison  #
################################################################################

from models.repository import Repository 
import mysql.connector

#
# globals
#

query = 'org:UW-Madison-DSI';
table = 'dsi_repositories';

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
		database = "github"
	)
except:
	print("No database found.")
	exit()

# fetch and store repositories according to search query
#
Repository.find_all(db, table, query)