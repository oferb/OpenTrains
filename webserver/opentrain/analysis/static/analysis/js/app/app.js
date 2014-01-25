// app.js

app = angular.module('show_reports', ['my.services', 'my.filters', 'my.directives', 'leaflet-directive']);

app.controller('ShowReportsController', ['$scope', 'MyHttp', '$timeout', 'leafletData',
function($scope, MyHttp, $timeout, leafletData) {
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
		var url = '/api/v1/reports-loc/?device_id=' + curId + '&limit=200';
		$scope.appendReportsRec(url);
	};
	$scope.appendReportsRec = function(url) {
		MyHttp.get(url).success(function(data) {
			$scope.reports.push.apply($scope.reports, data.objects);
			if (data.meta.next) {
				$scope.appendReportsRec(data.meta.next);
			} else {
				$scope.reportsStatus = 'done';
				$timeout(function() {
					$scope.drawMap();
				}, 500);
			}
		});
	};
	$scope.drawMap = function() {
		leafletData.getMap().then(function(map) {
			$scope.showReports(map);
		});
	};
	$scope.getDeviceTitle = function(device) {
		return device.device_id + ' @' + device.device_date + ' (' + device.device_count + ')';
	};

	$scope.showReports = function(map) {
		var points = [];
		$scope.reports.forEach(function(r) {
			points.push([r.loc.lat, r.loc.lon]);
		});
		console.log(points.length);
		var polyline = $scope.createLineAndZoom(map, points, {
			color : '#0000CD',
			weight : 3,
			stroke : true,
		});
	};

	$scope.createLine = function(map, points, options) {
		var polyline = L.polyline(points, options).addTo(map);
		return polyline;
	};

	$scope.createLineAndZoom = function(map, points, options) {
		var polyline = $scope.createLine(map,points, options);
		map.fitBounds(polyline.getBounds());
		return polyline;
	};

	/*$scope.resizeMap = function() {
	 var height = ($(window).height() - 20 - $("#deviceMap").offset().top);
	 console.log(height);
	 $('#deviceMap').css("height", height);
	 $('#deviceMap').css("margin-top",20);
	 };*/
	$scope.initReport();
	/*$(window).on("resize",function() {
	 $scope.resizeMap();
	 });
	 $scope.resizeMap();*/
}]);

