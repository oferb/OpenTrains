// app.js

app = angular.module('show_reports', ['my.services', 'my.filters', 'my.directives', 'my.leaflet','leaflet-directive']);

app.controller('ShowReportsController', ['$scope', 'MyHttp', 'MyUtils','MyLeaflet','$timeout', 'leafletData','$window',
function($scope, MyHttp, MyUtils,MyLeaflet,$timeout, leafletData,$window) {
	$scope.getParameterByName = function(name) {
	    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
	    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
	        results = regex.exec($window.location.search);
	    return results == null ? null : decodeURIComponent(results[1].replace(/\+/g, " "));
	};
	$scope.input = {
		selectedDevice : null,
	};
	$scope.initReport = function() {
		var device_id = $scope.getParameterByName('device_id');
		$scope.devices = [];
		$scope.reportsStatus = 'none';
		$scope.loadDeviceList(device_id);
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
	$scope.loadReports = function() {
		$scope.reportsStatus = 'wip';
		var curId = $scope.input.selectedDevice.device_id;
		$scope.reports = [];
		var url = '/api/v1/reports-loc/?device_id=' + curId + '&limit=200';
		$scope.appendReportsRec(url);
	};
	$scope.appendReportsRec = function(url) {
		MyHttp.get(url).success(function(data) {
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
			MyLeaflet.showReports(map,$scope.reports);
		});
	};
	$scope.getDeviceTitle = function(device) {
		return device.device_id + ' @' + device.device_date + ' (' + device.device_count + ')';
	};

	$scope.initReport();
}]);

