"use strict";
// app.js

var app = angular.module('live_trains', ['my.services', 'my.filters', 'my.directives', 'my.leaflet', 'leaflet-directive']);

app.controller('LiveTrainsController', ['$scope', 'MyHttp', 'MyUtils', 'MyLeaflet', '$timeout', 'leafletData', '$window', '$interval',
function($scope, MyHttp, MyUtils, MyLeaflet, $timeout, leafletData, $window, $interval) {
	$scope.input = {
		showTrips : {},
	};
	$scope.leftCounter = 10;
	$scope.initTrips = function() {
		$scope.tripDatas = {};
		$scope.trips = [];
		MyHttp.get('/api/v1/live-trips/?limit=100').success(function(data) {
			$scope.trips = data.objects;
			$scope.leftCounter = $scope.trips.length;
			$scope.trips.forEach(function(trip) {
				$scope.loadTripData(trip.trip_id);
			});
		});
	};
	$scope.loadTripData = function(trip_id) {
		$scope.input.showTrips[trip_id] = true;
		MyHttp.get('/api/v1/trips/' + trip_id + '/').success(function(data) {
			console.log('loaded data for trip ' + trip_id);
			$scope.tripDatas[trip_id] = data;
			$scope.drawTripData(trip_id);
		});
	};
	$scope.drawTripData = function(trip_id) {
		leafletData.getMap().then(function(map) {
			var tripData = $scope.tripDatas[trip_id];
			var shapes = tripData.shapes;
			MyLeaflet.drawShapes(map,shapes);
			$scope.leftCounter--;
			if ($scope.leftCounter <= 0) {
				$scope.refreshBoundBox(map);
			}
		});
	};
	$scope.refreshBoundBox = function(map) {
		var points = [];
		for (var key in $scope.tripDatas) {
			var trip = $scope.tripDatas[key];
			trip.shapes.forEach(function(shape) {
				points.push([shape.shape_pt_lat,shape.shape_pt_lon]);
			});
		};
		var box = MyLeaflet.findBoundBox(points);
		map.fitBounds(box);
		
	};
	$scope.initTrips();
}]);

