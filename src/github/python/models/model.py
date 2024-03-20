################################################################################
#                                                                              #
#                                   model.py                                   #
#                                                                              #
################################################################################
#                                                                              #
#        This is an abstract base class for models that can be stored to       #
#        a database.                                                           #
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
import json
import numpy as np

class Model:

	#
	# attributes
	#

	attributes = []

	#
	# constructor
	#

	def __init__(self, attributes):

		"""
		Creates a new model with the specified attributes.

		Parameters:
			attributes (dict): The model's attributes
		"""

		# set attributes
		#
		self.attributes = attributes;

	#
	# querying methods
	#

	def has(self, attribute):

		"""
		Tests if this model has this attribute.

		Returns:
			boolean
		"""

		return attribute in self.attributes and self.attributes[attribute] != None and self.attributes[attribute] != ''

	#
	# getting methods
	#

	def get(self, attribute):

		"""
		Gets this model's attribute.

		Parameters:
			attribute (string): The attribute to get.
		Returns:
			object
		"""

		if (not self.has(attribute)):
			return
		return self.attributes[attribute]

	#
	# setting methods
	#

	def set(self, key, value):

		"""
		Sets one of this model's attributes.

		Parameters:
			key (string): The name of the attribute to set.
			value: The value of the attribute to set.
		Returns:
			Model
		"""

		self.attributes[key] = value
		return self

	def set_all(self, attributes):

		"""
		Sets all of this model's attributes.

		Parameters:
			attributes (dict): The attributes (keys and values) to set.
		Returns:
			Model
		"""

		self.attributes = attributes
		return self

	#
	# ajax methods
	#

	def fetch(self):

		"""
		Fetches this model from the server.

		Returns:
			Model
		"""

		request = requests.get(self.url())
		if (request.status_code == 200):
			self.attributes = json.loads(request.text)
		else:
			print("Error - could not fetch model from " + self.url())
		return self

	#
	# database methods
	#

	def exists(self, db, table):

		"""
		Tests whether this model exists in the database.

		Parameters:
			db (object) - The database to store the model in.
			table (string) - The name of the database table to store the model in.
		Returns:
			boolean
		"""

		return self.find(db, table) != None

	def find(self, db, table):

		"""
		Finds this model in the database.

		Parameters:
			db (object) - The database to store the model in.
			table (string) - The name of the database table to store the model in.
		Returns:
			Object
		"""

		cursor = db.cursor()
		query = 'SELECT * FROM ' + table + ' WHERE id = ' + str(self.get('id'))
		cursor.execute(query)
		return cursor.fetchall()

	def store(self, db, table):

		"""
		Stores this model in the database.

		Parameters:
			db (object) - The database to store the model in.
			table (string) - The name of the database table to store the model in.
		Returns:
			Object
		"""

		# check for data
		#
		if (self.attributes == None):
			print("Can not store uninitialized model.")
			return

		# delete previous row if already exists
		#
		if (self.exists(db, table)):
			self.delete(db, table)

		# add new row to database
		#
		cursor = db.cursor()
		attributes = self.to_array()

		# create list of keys
		#
		keys = list(attributes.keys())
		keys_str = ''
		count = 0
		for key in keys:
			keys_str += str(key)
			count += 1
			if (count < len(keys)):
				keys_str += ', '

		# create list of values
		#
		values = list(attributes.values())
		values_str = ''
		count = 0
		for value in values:
			values_str += ("'" + str(value).encode(encoding="ascii", errors="ignore").decode('ascii').replace("'", "`") + "'") if value != None else 'NULL'
			count += 1
			if (count < len(values)):
				values_str += ', '

		query = 'INSERT INTO ' + table + ' (' + keys_str + ') VALUES (' + values_str + ')'
		cursor.execute(query)
		db.commit()

	def delete(self, db, table):

		"""
		Deletes this model from the database.

		Parameters:
			db (object) - The database to store the model in.
			table (string) - The name of the database table to store the model in.
		Returns:
			Object
		"""

		cursor = db.cursor()
		query = 'DELETE FROM ' + table + ' WHERE id = ' + str(self.get('id'))
		cursor.execute(query)
		db.commit()
		return self

	#
	# output methods
	#

	def print(self):

		"""
		Prints this model's attributes

		Returns:
			None
		"""

		print(self.attributes)