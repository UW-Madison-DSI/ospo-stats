################################################################################
#                                                                              #
#                                  gitlab.py                                   #
#                                                                              #
################################################################################
#                                                                              #
#        This is an abstract base class for fetching GitLab models.            #
#                                                                              #
#        Author(s): Abe Megahed                                                #
#                                                                              #
#        This file is subject to the terms and conditions defined in           #
#        'LICENSE.txt', which is part of this source code distribution.        #
#                                                                              #
################################################################################
#  Copyright (C) 2024 Data Science Institute, Univeristy of Wisconsin-Madison  #
################################################################################

import requests

class GitLab:

	#
	# attributes
	#

	url = 'https://git.doit.wisc.edu/api/v4'
	token = '<YOUR PERSONAL ACCESS TOKEN>'

	#
	# querying methods
	#

	def get(self, url):

		"""
		Gets data from the GitHub API.

		Parameters:
			url (string) - The url to fetch.
		Returns:
			Request
		"""

		# initiate the get request
		#
		return requests.get(url, headers = {
			'Authorization': 'Bearer ' + self.token
		})
