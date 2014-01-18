// utility functions for open train
"use strict";

function toHourMinSec(dt) {
	var h = dt.getHours();
	var m = dt.getMinutes();
	var s = dt.getSeconds();
	m = m < 10 ? '0' + m : '' + m;
	s = s < 10 ? '0' + s : '' + s;
	return '' + h + ':' + m + ':' + s;
};

function toLocalDt(dt) {
	return dt.toString();
}

function toDate(dt) {
	return dt.toDateString();
}

