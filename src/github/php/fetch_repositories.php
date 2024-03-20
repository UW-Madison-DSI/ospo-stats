<?php
/******************************************************************************\
|                                                                              |
|                            fetch_repositories.php                            |
|                                                                              |
|******************************************************************************|
|                                                                              |
|        This is a utility for fetching repositories from the GitHub API       |
|        according to a search query.                                          |
|                                                                              |
|        Author(s): Abe Megahed                                                |
|                                                                              |
|        This file is subject to the terms and conditions defined in           |
|        'LICENSE.txt', which is part of this source code distribution.        |
|                                                                              |
|******************************************************************************|
|  Copyright (C) 2024 Data Science Institute, Univeristy of Wisconsin-Madison  |
\******************************************************************************/

include "models/repository.php";
include 'utilities/database.php';

$query = 'Wisconsin';
$table = 'wisconsin_repositories';

//
// main
//

$respositories = Repository::fetchSince($db, $table, $query, 2000);