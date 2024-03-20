<?php
/******************************************************************************\
|                                                                              |
|                                  model.php                                   |
|                                                                              |
|******************************************************************************|
|                                                                              |
|        This is an abstract base class for models.                            |
|                                                                              |
|        Author(s): Abe Megahed                                                |
|                                                                              |
|        This file is subject to the terms and conditions defined in           |
|        'LICENSE.txt', which is part of this source code distribution.        |
|                                                                              |
|******************************************************************************|
|  Copyright (C) 2024 Data Science Institute, Univeristy of Wisconsin-Madison  |
\******************************************************************************/

abstract class Model {

	//
	// attributes
	//

	public $attributes = [];

	//
	// constructor
	//

	/**
	 * Create a new model.
	 *
	 * @param $attributes[]
	 * @return Model
	 */
	function __construct(array $attributes) {

		// set attributes
		//
		$this->attributes = $attributes;
	}

	//
	// querying methods
	//

	/**
	 * Test if this model has this attribute.
	 *
	 * @param string $attribute
	 * @return boolean
	 */
	public function has(string $attribute) {	
		return array_key_exists($attribute, $this->attributes) && $this->attributes[$attribute] != NULL;	
	}

	//
	// getting methods
	//

	/**
	 * Get this model's attribute.
	 *
	 * @param string $attribute
	 * @return object
	 */
	public function get(string $attribute) {	
		if (!$this->has($attribute)) {
			return;
		}
		return $this->attributes[$attribute];
	}

	//
	// setting methods
	//

	/**
	 * Set this model's attribute.
	 *
	 * @param string $key
	 * @param object $value
	 * @return NULL
	 */
	public function set(string $key, $value) {	
		$this->attributes[$key] = $value;
	}

	/**
	 * Set all of this model's attributes.
	 *
	 * @param object $attributes
	 * @return NULL
	 */
	public function setAll(string $attributes) {	
		$this->attributes = $attributes;
	}

	//
	// ajax methods
	//

	/**
	 * Fetch this model from the server.
	 *
	 * @return Model
	 */
	public function fetch() {
		$this->attributes = json_decode(file_get_contents($this->url()));
		return $this;
	}

	//
	// database saving methods
	//

	/**
	 * Store this model in the database.
	 *
	 * @param db - the database to store the model in.
	 * @param string $table - the database table to store the model in.
	 * @return bool - success
	 */
	public function store($db, string $table) {

		// check for data
		//
		if (!$this->attributes) {
			return;
		}

		// delete previous row if already exists
		//
		if (exists($db, $table, 'id', $this->get('id'))) {
			delete($db, $table, $this->get('id'));
		}

		// add new row to database
		//
		return insert($db, $table, $this->toArray());
	}

	//
	// output methods
	//

	/**
	 * Save this model to a file.
	 *
	 * @param string $filename - the name of the file to store the model in.
	 * @return bool - success
	 */
	public function saveAs($filename) {

		// check if we can save
		//
		if (!$this->attributes) {
			return;
		}

		// write model data
		//
		file_put_contents($filename, json_encode($this->attributes, JSON_PRETTY_PRINT));
	}

	/**
	 * Convert this model to JSON.
	 *
	 * @return bool - success
	 */
	public function toJson() {
		return json_encode($this->attributes);
	}
}