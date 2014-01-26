"use strict";

var services = angular.module('my.services', []);

services.factory('MyUtils', function() {
	return {
		toHourMinSec : function(dt) {
			var h = dt.getHours();
			var m = dt.getMinutes();
			var s = dt.getSeconds();
			m = m < 10 ? '0' + m : '' + m;
			s = s < 10 ? '0' + s : '' + s;
			return '' + h + ':' + m + ':' + s;
		}
	};
});
