<?php
/******************************************************************************\
|                                                                              |
|                                repository.php                                |
|                                                                              |
|******************************************************************************|
|                                                                              |
|        This is a class for fetching and storing GitHub repositories.         |
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

class Repository extends Model {

	//
	// querying methods
	//

	/**
	 * Get this repository's base url.
	 *
	 * @return string
	 */
	public static function baseUrl() {
		return 'https://api.github.com/search/repositories';
	}

	/**
	 * Get this repository's url.
	 *
	 * @return string
	 */
	public function url() {
		return self::baseUrl() . '/' . $this->id;
	}

	/**
	 * Get the url to this repository's content.
	 *
	 * @return string
	 */
	public function contentUrl() {
		return 'https://raw.githubusercontent.com/' . $this->get('owner')->login . '/' . $this->get('name');
	}

	/**
	 * Get this team's database table.
	 *
	 * @return string
	 */
	public function table() {
		return 'repositories';
	}

	/**
	 * Limit the size of a string
	 *
	 * @return string
	 */
	public static function clampStr($str, $limit): ?string {
		if (!$str) {
			return $str;
		}
		return strlen($str) > $limit? substr($str, 0, $limit) : $str;
	}

	/**
	 * Get this repo's readme file
	 *
	 * @return string
	 */
	public function getReadMe(): ?string {

		// try main branch
		//
		$text = file_get_contents($this->contentUrl() . '/main/README.md');
		if ($text) {
			return $text;
		}

		// try master branch
		//
		$text = file_get_contents($this->contentUrl() . '/master/README.md');
		if ($text) {
			return $text;
		}

		return NULL;
	}

	//
	// fetching methods
	//

	public static function fetchAll($db, $table, $query, $year = NULL) {
		$items = [];
		$url = Repository::baseUrl() . '?q=' . $query;
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
				$repository = new Repository($attributes);
				if ($year) {
					$repository->set('year', $year);
				}
				echo "Saving " . $repository->get('name') . ".\n";
				$repository->store($db, $table);
			}

			// add to list
			//
			$items = array_merge($items, $data->items);

			// advance to next page
			//
			$page++;
			$count += count($data->items);

			// rate limiting - limit to 30 requests / minute
			//
			sleep(2);
		}

		return $items;
	}

	public static function fetchSince($db, string $table, string $query, int $startYear) {
		$items = [];
		$year = date("Y");
		while ($year > $startYear) {
			$startDate = $year . '-01-01';
			$endDate = ($year + 1) . '-01-01';
			$dateQuery = $query . '%20created:' . $startDate . '..' .$endDate;

			// fetch items from date range
			//
			echo "Fetching items from " . $startDate . " to " . $endDate . "\n";
			$yearItems = Repository::fetchAll($db, $table, $dateQuery, $year);

			// add to list
			//
			if ($yearItems) {
				$items = array_merge($items, $yearItems);
			}

			// rate limiting - limit to 30 requests / minute
			//
			sleep(2);

			// go to previous year
			//
			$year--;
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
		$readme = $this->getReadme();
		$lowercase = $readme? strtolower($readme) : null;

		return [
			'id' => $this->get('id'),

			// name attributes
			//
			'name' => $this->get('name'),
			'full_name' => $this->get('full_name'),

			// owner info
			//
			'owner_id' => $this->get('owner')->id,

			// attributes
			//
			'html_url' => $this->get('html_url'),
			'description' => self::clampStr($this->get('description'), 8192),
			'homepage' => $this->get('homepage'),
			'language' => $this->get('language'),

			// metrics
			//
			'stargazers_count' => $this->get('stargazers_count'),
			'watchers_count' => $this->get('watchers_count'),
			'forks_count' => $this->get('forks_count'),
			'open_issues_count' => $this->get('open_issues_count'),
			'score' => $this->get('score'),

			// license
			//
			'license_key' => $this->has('license')? $this->get('license')->key : null,
			'license_name' => $this->has('license')? $this->get('license')->name : null,
			'readme_size' => $readme? strlen($readme) : null,
			'readme_has_images' => $readme != null && (str_contains($lowercase, '.jpg') || str_contains($lowercase, '.jpeg') || str_contains($lowercase, '.png')) ? 1 : 0,
			'readme_has_icons' => $readme != null && str_contains($lowercase, '.svg') ? 1 : 0,
			'year' => $this->has('year')? $this->get('year') : null
		];
	}
}