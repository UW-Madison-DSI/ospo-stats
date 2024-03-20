################################################################################
#                                                                              #
#                                   user.py                                    #
#                                                                              #
################################################################################
#                                                                              #
#        This is a class for fetching and storing GitHub users.                #
#                                                                              #
#        Author(s): Abe Megahed                                                #
#                                                                              #
#        This file is subject to the terms and conditions defined in           #
#        'LICENSE.txt', which is part of this source code distribution.        #
#                                                                              #
################################################################################
#  Copyright (C) 2024 Data Science Institute, Univeristy of Wisconsin-Madison  #
################################################################################

from models.model import Model
from models.github import GitHub

class User(Model):

	#
	# attributes
	#

	base_url = GitHub.url + '/users'
	search_url = GitHub.url + '/search/users'

	#
	# querying methods
	#

	def url() {

		"""
		Gets the url for this user.

		Returns:
			string
		"""

		return self.base_url + '/' + this.get('id');

	#
	# conversion methods
	#

	def to_array():

		"""
		Get this users's attributes as an array.

		Returns:
			array
		"""

		return [
			'id': this.get('id'),

			# name attributes
			#
			'login': this.get('login'),

			# attributes
			#
			'avatar_url': this.get('avatar_url'),
			'html_url': this.get('html_url'),

			# metrics
			#
			'type': this.get('type'),
			'score': this.get('score')
		]