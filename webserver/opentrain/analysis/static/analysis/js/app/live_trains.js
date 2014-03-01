"use strict";
// app.js

var app = angular.module('live_trains', ['my.services', 'my.filters', 'my.directives', 'my.leaflet', 'leaflet-directive']);

app.controller('LiveTrainsController', ['$scope', 'MyHttp', 'MyUtils', 'MyLeaflet', '$timeout', 'leafletData', '$window', '$interval',
function($scope, MyHttp, MyUtils, MyLeaflet, $timeout, leafletData, $window, $interval) {
	$scope.input = {
		showOnMap : {},
		showDetails : {},
	};
	$scope.tripsData = {};
	$scope.tripMapInfo = {};
	$scope.layers = [];
	$scope.locationLayers = [];
	$scope.showTripsChange = function() {
		var counterObj = {
			counter : $scope.trips.length,
			decr : function() {
				this.counter--;
				if (this.counter == 0) {
					$scope.refreshMap();
				};
			},
		};
		$scope.trips.forEach(function(trip) {
			var tripId = trip.trip_id;
			if ($scope.input.showOnMap[tripId]) {
				if (!$scope.tripsData[tripId]) {
					MyHttp.get('/api/1/trips/' + tripId + '/details/').success(function(data) {
						$scope.tripsData[tripId] = data;
						counterObj.decr();
					});
				} else {
					counterObj.decr();
				}
			} else {
				$scope.tripsData[tripId] = null;
				counterObj.decr();
			}
		});
	};
	$scope.refreshMap = function() {
		leafletData.getMap().then(function(map) {
			$scope.layers.forEach(function(l) {
				map.removeLayer(l);
			});
			$scope.layers = [];
			$scope.locationLayers.forEach(function(l) {
				map.removeLayer(l);
			});
			$scope.locationLayers = [];
			$scope.trips.forEach(function(trip) {
				if ($scope.input.showOnMap[trip.trip_id]) {
					$scope.addTripToMap(map, trip.trip_id);
				};
			});
		});
	};
	$scope.addTripToMap = function(map, tripId) {
		var tripData = $scope.tripsData[tripId];
		var shapes = tripData.shapes;
		var stops = tripData.stop_times.map(function(st) {
			return st.stop;
		});
		var line = MyLeaflet.drawShapes(shapes);
		var markers = MyLeaflet.drawStops(stops);
		var layers = [line];
		markers.forEach(function(m) {
			layers.push(m);
		});
		var lg = L.layerGroup(layers);
		$scope.layers.push(lg);
		map.addLayer(lg);
	};
	$scope.initTrips = function() {
		$scope.tripDatas = {};
		$scope.trips = [];
		MyHttp.get('/api/1/trips/current/').success(function(data) {
			$scope.isFake = data.meta.is_fake;
			$scope.trips = data.objects;
			$scope.setInitialBox();
		});
		$scope.updateTripsLocation();
		$interval(function() {
			$scope.updateTripsLocation();
		}, 3000);
	};
	$scope.updateTripsLocation = function() {
		var tripIds = [];
		for (var key in $scope.input.showOnMap) {
			if ($scope.input.showOnMap[key]) {
				tripIds.push(key);
			}
		}
		if (tripIds.length > 0) {
			MyHttp.get('/api/1/trips/cur-location/', {
				trip_ids : tripIds.join(','),
			}).success(function(data) {
				leafletData.getMap().then(function(map) {
					$scope.updateLocationsOnMap(map, data.objects);
				});
			});
		} else {
			console.log('no selected trips');
		}
	};

	$scope.zoomToTrip = function(tripId) {
		var points = $scope.tripsData[tripId].shapes;
		leafletData.getMap().then(function(map) {
			var box = MyLeaflet.findBoundBox(points);
			map.fitBounds(box);
		});
	};

	$scope.updateLocationsOnMap = function(map, objects) {
		// remove old layers
		$scope.locationLayers.forEach(function(l) {
			map.removeLayer(l);
		});
		$scope.locationLayers = [];
		objects.forEach(function(obj) {
			var tripData = $scope.tripsData[obj.trip_id];
			if (tripData) {
				var cur = MyLeaflet.getTripMarker(obj, tripData, 'cur');
				var exp = MyLeaflet.getTripMarker(obj, tripData, 'exp');
				if (cur) {
					$scope.locationLayers.push(cur);
					map.addLayer(cur);
					
				}
				$scope.locationLayers.push(exp);
				map.addLayer(exp);
			}
		});
	};
	$scope.setInitialBox = function() {
		leafletData.getMap().then(function(map) {
			var box = [[31.06867403, 34.60432436], [33.00500359, 35.18816094]];
			map.fitBounds(box);
		});
	};
	$scope.resizeMap = function() {
		var w = $(window).width() * 0.6;
		var h = $(window).height() - 70;
		$(".angular-leaflet-map").css('width', 'auto');
		$(".angular-leaflet-map").css('height', h + 'px');
		return false;
	};
	$scope.initTrips();
}]);

app.controller('TripController', ['$scope',
function($scope) {
	$scope.firstStopName = $scope.trip.stop_times[0].stop.stop_name;
	$scope.lastStopName = $scope.trip.stop_times[$scope.trip.stop_times.length - 1].stop.stop_name;
	$scope.tripId = $scope.trip.trip_id;
	$scope.tripData = $scope.tripDatas[$scope.tripId];
}]);
