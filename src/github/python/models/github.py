################################################################################
#                                                                              #
#                                  github.py                                   #
#                                                                              #
################################################################################
#                                                                              #
#        This is an abstract base class for fetching GitHub models.            #
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

class GitHub:

	#
	# attributes
	#

	url = 'https://api.github.com'
	content_url = 'https://raw.githubusercontent.com'
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
			'Accept': 'application/vnd.github+json',
			'Authorization': 'Bearer ' + self.token,
			'X-GitHub-Api-Version': '2022-11-28',
			'User-Agent': 'curl/7.54.1'
		})
