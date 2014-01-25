// app.js

app = angular.module('show_reports', ['my.services', 'my.filters', 'my.directives', 'leaflet-directive']);

app.controller('ShowReportsController', ['$scope', 'MyHttp', '$timeout', 'leafletData','$window',
function($scope, MyHttp, $timeout, leafletData,$window) {
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
	$scope.trainIcon = L.icon({
		iconUrl : '/static/common/img/open-train.png',
		iconSize : [26, 26]
	});
	$scope.getDeviceTitle = function(device) {
		return device.device_id + ' @' + device.device_date + ' (' + device.device_count + ')';
	};

	$scope.showReports = function(map) {
		var points = [];
		$scope.noLocCount = 0;
		$scope.locCount = 0;
		$scope.reports.forEach(function(r) {
			if (r.loc) {
				$scope.locCount++;
				points.push([r.loc.lat, r.loc.lon]);
			} else {
				$scope.noLocCount++;
			}
		});
		console.log(points.length);
		var polyline = $scope.createLineAndZoom(map, points, {
			color : '#0000CD',
			weight : 3,
			stroke : true,
		});
		points.forEach(function(pt, index) {
			var report = $scope.reports[index];
			var text = '<a href="/analysis/report-details/?report_id=' + report.id + '">' + report.id + '</a><br/>';// + toHourMinSec(report.timestamp);
			if (report.is_station) {
				L.marker(pt, {
					icon : $scope.trainIcon
				}).addTo(map).bindPopup(text);
			} else {
				L.circleMarker(pt, {
					radius : 5,
					color : '#0000CD',
					fill : true,
				}).addTo(map).bindPopup(text);
			}
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

