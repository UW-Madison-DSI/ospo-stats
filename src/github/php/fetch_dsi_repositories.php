<?php
/******************************************************************************\
|                                                                              |
|                          fetch_dsi_repositories.php                          |
|                                                                              |
|******************************************************************************|
|                                                                              |
|        This is a utility for fetching and storing GitHub repositories        |
|        belonging to the University of Wisconsin Data Science Institute.      |
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

//
// globals
//

$query = 'org:UW-Madison-DSI';
$table = 'dsi_repositories';

//
// main
//

$respositories = Repository::fetchAll($db, $table, $query);