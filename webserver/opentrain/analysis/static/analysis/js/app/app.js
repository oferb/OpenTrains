// app.js

app = angular.module('show_reports', ['my.services', 'my.filters', 'my.directives', 'my.leaflet', 'leaflet-directive']);

app.controller('ShowReportsController', ['$scope', 'MyHttp', 'MyUtils', 'MyLeaflet', '$timeout', 'leafletData', '$window', '$interval',
function($scope, MyHttp, MyUtils, MyLeaflet, $timeout, leafletData, $window, $interval) {
	$scope.getParameterByName = function(name) {
		name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
		var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"), results = regex.exec($window.location.search);
		return results == null ? null : decodeURIComponent(results[1].replace(/\+/g, " "));
	};
	$scope.input = {
		selectedDevice : null,
		autoZoom : true,
	};
	$scope.initReport = function() {
		var device_id = $scope.getParameterByName('device_id');
		$scope.devices = [];
		$scope.reportsStatus = 'none';
		$scope.liveMode = false;
		$scope.loadDeviceList(device_id);
	};
	$scope.intervalPromise = undefined;
	$scope.goLive = function() {
		$scope.liveMode = true;
		$scope.intervalPromise = $interval(function() {
			$scope.updateDevice();
		}, 10000);
	};
	$scope.stopLive = function() {
		$scope.liveMode = false;
		if (angular.isDefined($scope.intervalPromise)) {
			$interval.cancel($scope.intervalPromise);
			$scope.intervalPromise = undefined;
		}
	};

	$scope.updateDevice = function() {
		$scope.loadLiveReports();
	};

	$scope.loadDeviceList = function(device_id) {
		MyHttp.get('/api/v1/devices/').success(function(data) {
			$scope.devices = data.objects;
			var found = false;
			$scope.devices.forEach(function(d) {
				if (device_id && d.device_id == device_id) {
					$scope.input.selectedDevice = d;
					$scope.loadReports();
					found = true;
				}
			});
			if (!found) {
				if ($scope.devices.length > 0) {
					$scope.input.selectedDevice = $scope.devices[0];
				} else {
					$scope.input.selectedDevice = null;
				}
			}
		});
	};
	$scope.redirectToReports = function() {
		window.location.href = '/analysis/select-device-reports/?device_id=' + $scope.input.selectedDevice.device_id;
	};
	$scope.loadLiveReports = function() {
		var curId = $scope.input.selectedDevice.device_id;
		var last_report_id = $scope.reports.length > 0 ? $scope.reports[$scope.reports.length - 1].id : 0;
		var url = '/api/v1/reports-loc/?device_id=' + curId + '&limit=200&id__gt=' + last_report_id;
		$scope.appendReportsRec(url);
	};
	$scope.loadReports = function() {
		$scope.reportsStatus = 'wip';
		var curId = $scope.input.selectedDevice.device_id;
		$scope.reports = [];
		$scope.lastShownReportIndex = -1;
		var url = '/api/v1/reports-loc/?device_id=' + curId + '&limit=200';
		$scope.appendReportsRec(url);
	};

	$scope.appendReportsRec = function(url) {
		MyHttp.get(url).success(function(data) {
			console.log('GOT ' + data.objects.length);
			$scope.reports.push.apply($scope.reports, data.objects);
			if (data.meta.next) {
				$scope.appendReportsRec(data.meta.next);
			} else {
				$scope.reports.forEach(function(r) {
					r.timestamp = new Date(r.timestamp);
					if (r.loc) {
						r.loc.timestsamp = new Date(r.loc.timestamp);
					}
				});
				$scope.reportsStatus = 'done';
				$timeout(function() {
					$scope.drawMap();
				}, 10);
			}
		});
	};
	$scope.drawMap = function() {
		leafletData.getMap().then(function(map) {
			var reports = $scope.reports.slice($scope.lastShownReportIndex + 1);
			if (reports.length == 0) {
				console.log('no new reports');
			} else {
				var minLon = +Infinity, maxLon = -Infinity, minLat = +Infinity, maxLat = -Infinity;
				$scope.reports.forEach(function(r) {
					if (r.loc) {
						minLon = Math.min(minLon, r.loc.lon);
						maxLon = Math.max(maxLon, r.loc.lon);
						minLat = Math.min(minLat, r.loc.lat);
						maxLat = Math.max(maxLat, r.loc.lat);
					} 
				});
				var lastPoint = null;
				if ($scope.lastShownReportIndex >= 0) {
					var l = $scope.reports[$scope.lastShownReportIndex].loc;
					lastPoint = [l.lat,l.lon];
				}
				var box = [[minLat, minLon], [maxLat,maxLon]];
				if (!$scope.input.autoZoom) {
					box = null;
				}
				MyLeaflet.showReports(map, reports, {
					box : box,
					initialPoint : lastPoint
				});
				$scope.lastShownReportIndex = $scope.reports.length - 1;
			}
		});
	};
	$scope.getDeviceTitle = function(device) {
		return device.device_id + ' @' + device.device_date + ' (' + device.device_count + ')';
	};

	$scope.initReport();
}]);

