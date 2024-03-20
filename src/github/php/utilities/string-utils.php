<?php

function toTitleCase($string) {
	return ucwords(strtolower($string));
}

function quotate($value) {
	if ($value != 0 && $value != '') {
		return "'" . $value . "'";
	} else {
		return 'null';
	}
}