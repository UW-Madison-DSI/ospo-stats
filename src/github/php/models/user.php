<?php
/******************************************************************************\
|                                                                              |
|                                   user.php                                   |
|                                                                              |
|******************************************************************************|
|                                                                              |
|        This is a class for fetching and storing GitHub users.                |
|                                                                              |
|        Author(s): Abe Megahed                                                |
|                                                                              |
|        This file is subject to the terms and conditions defined in           |
|        'LICENSE.txt', which is part of this source code distribution.        |
|                                                                              |
|******************************************************************************|
|  Copyright (C) 2024 Data Science Institute, Univeristy of Wisconsin-Madison  |
\******************************************************************************/

include_once "models/github.php";
include_once "models/model.php";

class User extends Model {

	//
	// querying methods
	//

	/**
	 * Get this user's base url.
	 *
	 * @return string
	 */
	public static function baseUrl() {
		return 'https://api.github.com/search/users';
	}

	/**
	 * Get this user's url.
	 *
	 * @return string
	 */
	public function url() {
		return self::baseUrl() . '/' . $this->id;
	}

	/**
	 * Get this team's database table.
	 *
	 * @return string
	 */
	public function table() {
		return 'users';
	}

	//
	// fetching methods
	//

	public static function fetchAll($db, $query, $table = 'users') {
		$items = [];
		$url = User::baseUrl() . '?q=' . $query;
		$text = GitHub::fetch($url);
		$data = json_decode($text);
		
		if (!$data || !property_exists($data, 'items')) {
			echo "No data received.\n";
			print_r($text);
			return;
		}

		// iterate over pages
		//
		$total = $data->total_count;
		$count = 0;
		$page = 1;
		echo "Total count = " . $total . ".\n";
		while ($count < $total) {
			$text = GitHub::fetch($url . '&page=' . $page);
			$data = json_decode($text);
			$page++;
			$count += count($data->items);

			if (!$data || !property_exists($data, 'items')) {
				echo "Error - no data received.\n";
				print_r($text);
				continue;
			}

			// store
			//
			for ($i = 0; $i < count($data->items); $i++) {
				$item = $data->items[$i];
				$attributes = get_object_vars($item);
				$user = new User($attributes);
				echo "Saving " . $user->get('login') . ".\n";
				$user->store($db, $table);
			}

			// add to list
			//
			$items = array_merge($items, $data->items);

			// rate limiting - limit to 30 requests / minute
			//
			sleep(2);
		}

		return $items;
	}

	//
	// conversion methods
	//

	/**
	 * Convert this team to an array.
	 *
	 * @return array
	 */
	public function toArray() {
		return [
			'id' => $this->get('id'),

			// name attributes
			//
			'login' => $this->get('login'),

			// attributes
			//
			'avatar_url' => $this->get('avatar_url'),
			'html_url' => $this->get('html_url'),

			// metrics
			//
			'type' => $this->get('type'),
			'score' => $this->get('score')
		];
	}
}