<?php

include 'lib/mysql.php';

define('DATABASE_HOST', '127.0.0.1');
define('DATABASE_USERNAME', 'root');
define('DATABASE_PASSWORD', 'root');
define('DATABASE_NAME', 'github');
define('DATABASE_DEBUG', FALSE);

// connect to database
//
$db = mysqli_connect(DATABASE_HOST, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME);
if (!$db) {
	die("Could not connect to datbase.");
}

function getValue($object, $name) {
	return property_exists($object, $name)? $object->name : null;
}

function getId($item) {
	if ($item) {
		return $item->id;
	} else {
		return null;
	}
}

function getIds($items) {
	if ($items) {
		$ids = [];
		for ($i = 0; $i < count($items); $i++) {
			array_push($ids, $items[$i]->id);
		}
		return $ids;
	} else {
		return null;
	}
}

function exists($db, $tableName, $row, $key) {
	$query = "SELECT * from $tableName WHERE $row = '$key'";
	$result = mysqli_query($db, $query);
	if ($result) {
		$row = mysql_fetch_assoc($result);
		if ($row) {
			return true;
		}
	}
	return false;
}

function iso8859_1_to_utf8(string $s): string {
    $s .= $s;
    $len = \strlen($s);

    for ($i = $len >> 1, $j = 0; $i < $len; ++$i, ++$j) {
        switch (true) {
            case $s[$i] < "\x80": $s[$j] = $s[$i]; break;
            case $s[$i] < "\xC0": $s[$j] = "\xC2"; $s[++$j] = $s[$i]; break;
            default: $s[$j] = "\xC3"; $s[++$j] = \chr(\ord($s[$i]) - 64); break;
        }
    }

    return substr($s, 0, $j);
}

function insert($db, $tableName, $rows) {

	// get row names
	//
	$keys = array_keys($rows);

	// get row values
	//
	$array = [];
	for ($i = 0; $i < count($rows); $i++) {
		$key = $keys[$i];
		$value = $rows[$key];

		/*
		if (DATABASE_DEBUG) {
			echo "KEY: " . $key . "\n";
			echo "VALUE: " . print_r($value, 1) . "\n";
			echo "\n";
		}
		*/

		// handle nulls
		//
		if ($value == 'NULL') {
			$value = null;

		// handle strings
		//
		} else if (gettype($value) == 'string') {
			if ($value) {
				$value = $db->escape_string(iso8859_1_to_utf8($value));
			}

		// handle arrays
		//
		} else if (is_array($value)) {
			$value = implode(", ", $value);

		// handle booleans
		//
		} else if (gettype($value) == 'bool') {
			$value = boolval($value);

		// handle objects
		//
		} else if (is_object($value)) {
			$value = print_r($value, 1);
			echo "Warning: converted object value of " . $key . " to string: " . $value;
		}

		if ($value !== NULL) {
			array_push($array, "'" . $value . "'");
		} else {
			array_push($array, 'null');
		}
	}

	// format keys, values
	//
	$keys = '`' . implode('`, `', $keys) . '`';
	$values = implode(',', $array);

	$query = "INSERT INTO `$tableName` ($keys) VALUES ($values)";
	if (DATABASE_DEBUG) {
		echo "query = " . $query . "\n";
	}

	// insert into database
	//
	try {
		$result = mysqli_query($db, $query);
	} catch (\Exception $exception) {
		echo "Error: query = " . $query . "\n";
		$result = null;
	}

	if (!$result) {
		die("Could not insert into database." . mysql_error());
	}
}

function update($db, $tableName, $id, $rows) {
	$query = "UPDATE `$tableName`";
	$query .= " SET ";
	$count = 0;
	foreach ($rows as $key => $value) {
		$query .= $key . " = " . $value;
		$count++;
		if ($count < count($rows)) {
			$query .= ',';
		}
	}
	$query .= " WHERE id = " . $id;
	if (DATABASE_DEBUG) {
		echo "query = " . $query . "\n";
	}

	// insert into database
	//
	try {
		$result = mysqli_query($db, $query);
	} catch (\Exception $exception) {
		echo "Error: query = " . $query . "\n";
		$result = null;
	}

	if (!$result) {
		die("Could not update database." . mysql_error());
	}
}

function delete($db, $tableName, $id) {
	$query = "DELETE FROM `$tableName` WHERE id = $id";
	if (DATABASE_DEBUG) {
		echo "query = " . $query . "\n";
	}

	// insert into database
	//
	try {
		$result = mysqli_query($db, $query);
	} catch (\Exception $exception) {
		echo "Error: query = " . $query . "\n";
		$result = null;
	}

	if (!$result) {
		die("Could not delete from database." . mysql_error());
	}
}