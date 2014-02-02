"use strict";
// app.js

var app = angular.module('live_trains', ['my.services', 'my.filters', 'my.directives', 'my.leaflet', 'leaflet-directive']);

app.controller('LiveTrainsController', ['$scope', 'MyHttp', 'MyUtils', 'MyLeaflet', '$timeout', 'leafletData', '$window', '$interval',
function($scope, MyHttp, MyUtils, MyLeaflet, $timeout, leafletData, $window, $interval) {
	$scope.input = {
		showTrips : {},
	};
	$scope.leftCounter = 0;
	$scope.initialDone = false;
	$scope.progress = 1;
	$scope.tripLayers = {};
	$scope.showTripsChange = function() {
		leafletData.getMap().then(function(map) {
			$scope.refreshLayers(map);
		});
	};
	$scope.refreshLayers = function(map) {
		console.log('In refreshLayers');
		for (var tripId in $scope.tripLayers) {
			var lg = $scope.tripLayers[tripId];
			var toShow = $scope.input.showTrips[tripId];
			if (!toShow) {
				if (map.hasLayer(lg)) {
					map.removeLayer(lg);
				}
			} else {
				if (!map.hasLayer(lg)) {
					map.addLayer(lg);
				}
			}
		}
	};
	$scope.initTrips = function() {
		$scope.tripDatas = {};
		$scope.trips = [];
		MyHttp.get('/api/v1/live-trips/?limit=100').success(function(data) {
			$scope.trips = data.objects;
			$scope.leftCounter = $scope.trips.length;
			$scope.progressSegment = 100 / $scope.trips.length;
			$scope.trips.forEach(function(trip) {
				$scope.loadTripData(trip.trip_id,true);
			});
		});
	};
	$scope.loadTripData = function(trip_id,is_initial) {
		$scope.input.showTrips[trip_id] = true;
		MyHttp.get('/api/v1/trips/' + trip_id + '/').success(function(data) {
			console.log('loaded data for trip ' + trip_id);
			$scope.tripDatas[trip_id] = data;
			$scope.drawTripData(trip_id,is_initial);
		});
	};
	$scope.updateTripsLive = function() {
		MyHttp.get('/api/v1/live-trips/?limit=100').success(function(data) {
			$scope.trips = data.objects;
			$scope.trips.forEach(function(trip) {
				if (!$scope.tripDatas[trip.trip_id]) {
					console.log('!!! found new trip id ' + trip_id);
					$scope.loadTripData(trip.trip_id,false);
				}
			});
		});
	};
	$scope.drawTripData = function(trip_id,is_initial) {
		leafletData.getMap().then(function(map) {
			var tripData = $scope.tripDatas[trip_id];
			var shapes = tripData.shapes;
			var stops = tripData.stop_times.map(function(st) {
				return st.stop;
			});
			var line = MyLeaflet.drawShapes(shapes);
			var markers = MyLeaflet.drawStops(stops);
			var layers = [line];
			layers.push.apply(layers,markers);
			var lg = L.layerGroup(layers);
			$scope.tripLayers[trip_id] = lg;
			lg.addTo(map);
			if (is_initial) {
				$scope.leftCounter--;
				$scope.progress = $scope.progressSegment * ($scope.trips.length - $scope.leftCounter);
				if ($scope.leftCounter <= 0) {
					$scope.refreshBoundBox(map);
				}
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
		$timeout(function() {
			$scope.initialDone = true;
		},500);
		$interval(function() {
			$scope.updateTripsLive();
		},5000);
	};
	$scope.initTrips();
}]);

