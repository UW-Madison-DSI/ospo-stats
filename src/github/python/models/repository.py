################################################################################
#                                                                              #
#                                repository.py                                 #
#                                                                              #
################################################################################
#                                                                              #
#        This is a class for fetching and storing GitHub repositories.         #
#                                                                              #
#        Author(s): Abe Megahed                                                #
#                                                                              #
#        This file is subject to the terms and conditions defined in           #
#        'LICENSE.txt', which is part of this source code distribution.        #
#                                                                              #
################################################################################
#  Copyright (C) 2024 Data Science Institute, Univeristy of Wisconsin-Madison  #
################################################################################

from models.github import GitHub
from models.model import Model
import json
import requests
import time
import datetime

class Repository(Model):

	#
	# attributes
	#

	base_url = GitHub.url + '/repositories'
	search_url = GitHub.url + '/search/repositories'

	#
	# querying methods
	#

	def url(self):

		"""
		Gets the url for this repository.

		Returns:
			string
		"""

		return self.base_url + '/' + str(self.get('id'))

	def content_url(self):

		"""
		Gets the url for this repository's content.

		Returns:
			string
		"""

		return GitHub.content_url + '/' + self.get('owner')['login'] + '/' + self.get('name')

	#
	# getting methods
	#

	def get_readme(self):

		"""
		Get the README.md information for this repository.

		Returns:
			string
		"""

		# try main branch
		#
		request = requests.get(self.content_url() + '/main/README.md')
		if (request.status_code == 200):
			return request.text

		# try master branch
		#
		request = requests.get(self.content_url() + '/master/README.md')
		if (request.status_code == 200):
			return request.text

		return None

	#
	# ajax methods
	#

	def fetch(self):

		"""
		Fetches this repository from the GitHub API.

		Returns:
			Repository
		"""

		# request attributes from API
		#
		request = GitHub().get(self.url())
		if (request.status_code == 200):

			# update attributes
			#
			self.set_all(json.loads(request.text))
		else:
			print("Error - could not fetch model from " + self.url())

		return self

	#
	# searching methods
	#

	@staticmethod
	def search(query, page = None):

		"""
		Search for repositories from the GitHub API.

		Returns:
			Repository
		"""

		# query GitHub API
		#
		url = Repository.search_url + '?q=' + query;
		if (page):
			url += '&page=' + str(page)
		response = GitHub().get(url)

		# parse response
		#
		if (response.status_code == 200):
			return json.loads(response.text)

	@staticmethod
	def find_all(db, table, query, year = None):

		"""
		Fetch and store repositories according to a search query.

		Parameters:
			db (object) - The database to store the repository info into.
			table (string) - The database table store the repository info into.
			query (string) - The query to use to find repositories to store.
		Returns:
			None
		"""

		data = Repository.search(query)
		
		# check if search returns any results
		#
		if (data == None or data['items'] == None):
			print("No data received.\n")
			print(text)
			return

		# check total number of items
		#
		total = data['total_count']
		print("Total count = " + str(total))

		# iterate over pages
		#
		page = 1
		count = 0
		while (count < total):

			# load data for page
			#
			data = Repository.search(query, page)

			# check if data exists for page
			#
			if (data == None or data['items'] == None):
				print("Error - no data received.\n")
				print(text)
				continue

			# store data from page
			#
			for i in range(0, len(data['items'])):
				repository = Repository(data['items'][i])
				if year is not None:
					repository.set('year', year)

				# delete repository if it already exists
				#
				if (repository.exists(db, table)):
					repository.delete(db, table)

				print("Saving " + repository.get('name'))
				repository.store(db, table)
				count += 1

			# advance to next page
			#
			page += 1

	@staticmethod
	def find_since(db, table, query, start_year):

		"""
		Fetch and store repositories from a particular year until the present.

		Parameters:
			db (object) - The database to store the repository info into.
			table (string) - The database table store the repository info into.
			query (string) - The query to use to find repositories to store.
			start_year (int) - The earliest year to search for.
		Returns:
			None
		"""

		year =  datetime.date.today().year

		# start at curent year and count down to start year
		#
		while (year > start_year):
			start_date = str(year) + '-01-01'
			end_date = str(year + 1) + '-01-01'
			date_query = query + '%20created:' + start_date + '..' + end_date

			# fetch items from date range
			#
			print("Fetching items from " + start_date + " to " + end_date)
			Repository.find_all(db, table, date_query, year)

			# rate limiting - limit to 30 requests / minute
			#
			time.sleep(2);

			# go to previous year
			#
			year -= 1

	#
	# conversion methods
	#

	def to_array(self):

		"""
		Get this repository's attributes as an array.

		Returns:
			array
		"""

		readme = self.get_readme()
		lowercase = readme.lower() if readme else None
		has_images = lowercase != None and ('.jpg' in lowercase or '.jpeg' in lowercase or '.png' in lowercase)
		has_icons = lowercase != None and '.svg' in lowercase

		return {
			'id': self.get('id'),

			# name attributes
			#
			'name': self.get('name'),
			'full_name': self.get('full_name'),

			# owner info
			#
			'owner_id': self.get('owner')['id'],

			# attributes
			#
			'html_url': self.get('html_url') if self.has('html_url') else None,
			'description': self.get('description')[:8192] if self.has('description') else None,
			'homepage': self.get('homepage') if self.has('homepage') else None,
			'language': self.get('language') if self.has('language') else None,

			# metrics
			#
			'stargazers_count': self.get('stargazers_count'),
			'watchers_count': self.get('watchers_count'),
			'forks_count': self.get('forks_count'),
			'open_issues_count': self.get('open_issues_count'),
			'score': self.get('score'),

			# license
			#
			'license_key': self.get('license')['key'] if self.has('license') else None,
			'license_name': self.get('license')['name'] if self.has('license') else None,
			'readme_size': len(readme) if readme else None,
			'readme_has_images': 1 if has_images else 0,
			'readme_has_icons': 1 if has_icons else 0,
			'year': self.get('year') if self.has('year') else None
		}