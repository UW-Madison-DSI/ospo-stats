<?php
/******************************************************************************\
|                                                                              |
|                                  github.php                                  |
|                                                                              |
|******************************************************************************|
|                                                                              |
|        This is an abstract base class for fetching GitHub models.            |
|                                                                              |
|        Author(s): Abe Megahed                                                |
|                                                                              |
|        This file is subject to the terms and conditions defined in           |
|        'LICENSE.txt', which is part of this source code distribution.        |
|                                                                              |
|******************************************************************************|
|  Copyright (C) 2024 Data Science Institute, Univeristy of Wisconsin-Madison  |
\******************************************************************************/

abstract class GitHub {

	//
	// attributes
	//

	public static $token = "<YOUR PERSONAL ACCESS TOKEN>";

	//
	// querying methods
	//

	public static function fetch($url) {

		// setup the request, you can also use CURLOPT_URL
		//
		$ch = curl_init($url);

		// returns the data/output as a string instead of raw data
		//
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

		// set headers
		//
		curl_setopt($ch, CURLOPT_HTTPHEADER, array(
			'Accept: application/vnd.github+json',
			'Authorization: Bearer ' . self::$token,
			'X-GitHub-Api-Version: 2022-11-28',
			'User-Agent: curl/7.54.1'
		));

		// get stringified data/output. See CURLOPT_RETURNTRANSFER
		//
		$data = curl_exec($ch);

		// get info about the request
		//
		$info = curl_getinfo($ch);

		// close curl resource to free up system resources
		//
		curl_close($ch);

		return $data;
	}
}