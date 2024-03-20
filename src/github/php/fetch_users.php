<?php
/******************************************************************************\
|                                                                              |
|                               fetch_users.php                                |
|                                                                              |
|******************************************************************************|
|                                                                              |
|        This is a utility for fetching users from the GitHub API              |
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

include "models/user.php";
include 'utilities/database.php';

// $query = 'wisc.edu';
$query = 'Wisconsin';
$table = 'wisconsin_users';

//
// main
//

$users = User::fetchAll($db, $query, $table);