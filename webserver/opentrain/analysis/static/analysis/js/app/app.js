// app.js

app = angular.module('show_reports', ['my.services', 'my.filters', 'my.directives']);

app.controller('ShowReportsController', ['$scope', '$window','MyHttp',
function($scope, $window,MyHttp) {
	$scope.input = {
		selectedDevice : null,
	};
	$scope.initReport = function() {
		$scope.devices = [];
		$scope.reportsStatus = 'none';
		$scope.loadDeviceList();
	};
	$scope.loadDeviceList = function() {
		MyHttp.get('/api/v1/devices/').success(function(data) {
			$scope.devices = data.objects;
			if ($scope.devices.length > 0) {
				$scope.input.selectedDevice = $scope.devices[0];
			} else {
				$scope.input.selectedDevice = null;
			}
		});
	};
	$scope.loadReports = function() {
		$scope.reportsStatus = 'wip';
		var curId = $scope.input.selectedDevice.device_id;
		$scope.reports = [];
		var url = '/api/v1/reports/?device_id=' + curId + '&limit=200';
		$scope.appendReportsRec(url);
		
	};
	$scope.appendReportsRec = function(url) {
		MyHttp.get(url).success(function(data) {
			$scope.reports.push.apply($scope.reports,data.objects);
			if (data.meta.next) {
				$scope.appendReportsRec(data.meta.next);
			} else {
				$scope.reportsStatus = 'done';
			}
		});
	};
	$scope.getDeviceTitle = function(device) {
		return device.device_id + ' @' + device.device_date + ' (' + device.device_count + ')';
	};
	$scope.initReport();
}]);


