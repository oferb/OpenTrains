"use strict";
// app.js

var app = angular.module('live_trains', ['my.services', 'my.filters', 'my.directives', 'my.leaflet', 'leaflet-directive']);

app.controller('LiveTrainsController', ['$scope', 'MyHttp', 'MyUtils', 'MyLeaflet', '$timeout', 'leafletData', '$window', '$interval',
function($scope, MyHttp, MyUtils, MyLeaflet, $timeout, leafletData, $window, $interval) {
	$scope.input = {
		showTrips : {},
		showDetails : {},
	};
	$scope.leftCounter = 0;
	$scope.initialDone = false;
	$scope.progress = 1;
	$scope.tripMapInfo = {};
	$scope.showTripsChange = function() {
		leafletData.getMap().then(function(map) {
			$scope.refreshLayers(map);
		});
	};
	$scope.showReportedOnly = function() {
		$scope.trips.forEach(function(trip) {
			$scope.input.showTrips[trip.trip_id] = trip.cur_point ? true : false;
		});
		$scope.showTripsChange();
	};
	$scope.showHideAll = function(toShow) {
		$scope.trips.forEach(function(trip) {
			$scope.input.showTrips[trip.trip_id] = toShow;
		});
		$scope.showTripsChange();
	};
	$scope.refreshLayers = function(map) {
		for (var tripId in $scope.tripMapInfo) {
			var lg = $scope.tripMapInfo[tripId].lg;
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
		MyHttp.get('/analysis/api/live-trips/').success(function(data) {
			$scope.isFake = data.meta.is_fake;
			$scope.trips = data.objects;
			if ($scope.trips.length == 0) {
				$scope.refreshInitial();
			}
			$scope.leftCounter = $scope.trips.length;
			$scope.progressSegment = 100 / $scope.trips.length;
			$scope.trips.forEach(function(trip) {
				$scope.loadTripData(trip.trip_id, true);
			});
		});
	};
	$scope.loadTripData = function(trip_id, is_initial) {
		MyHttp.get('/api/1/trips/' + trip_id + '/').success(function(data) {
			$scope.tripDatas[trip_id] = data;
			$scope.drawTripData(trip_id, is_initial);
		});
	};
	$scope.updateTripsLive = function() {
		$scope.intervalCounter++;
		MyHttp.get('/analysis/api/live-trips/', {
			limit : 100,
			counter : $scope.intervalCounter,
		}).success(function(data) {
			$scope.trips = data.objects;
			$scope.trips.forEach(function(trip) {
				if (!$scope.tripDatas[trip.trip_id]) {
					console.log('!!! found new trip id ' + trip.trip_id);
					$scope.loadTripData(trip.trip_id, false);
				}
			});
			leafletData.getMap().then(function(map) {
				$scope.trips.forEach(function(trip) {
					$scope.updateTripStatus(map, trip);
				});
			});
		});
	};

	$scope.zoomToTrip = function(tripId) {
		var points = $scope.tripDatas[tripId].shapes;
		leafletData.getMap().then(function(map) {
			var box = MyLeaflet.findBoundBox(points);
			map.fitBounds(box);
		});
	};

	$scope.updateTripStatus = function(map, trip) {
		var tripData = $scope.tripDatas[trip.trip_id];
		var ti = $scope.tripMapInfo[trip.trip_id];
		if (!ti || !ti.lg) {
			console.log('trip ' + trip.trip_id + ' is not ready yet');
			return;
		}
		var lg = ti.lg;
		var cur = MyLeaflet.getTripMarker(trip, tripData, 'cur');
		var exp = MyLeaflet.getTripMarker(trip, tripData, 'exp');
		if (ti.cur) {
			ti.lg.removeLayer(ti.cur);
		}
		if (ti.exp) {
			ti.lg.removeLayer(ti.exp);
		}
		ti.cur = cur;
		ti.exp = exp;
		if (cur) {
			lg.addLayer(cur);
		}
		lg.addLayer(exp);
	};
	$scope.drawTripData = function(trip_id, is_initial) {
		leafletData.getMap().then(function(map) {
			var tripData = $scope.tripDatas[trip_id];
			var shapes = tripData.shapes;
			var stops = tripData.stop_times.map(function(st) {
				return st.stop;
			});
			var line = MyLeaflet.drawShapes(shapes);
			var markers = MyLeaflet.drawStops(stops);
			var layers = [line];
			layers.push.apply(layers, markers);
			var lg = L.layerGroup(layers);
			$scope.tripMapInfo[trip_id] = {
				lg : lg
			};
			if (is_initial) {
				$scope.leftCounter--;
				$scope.progress = $scope.progressSegment * ($scope.trips.length - $scope.leftCounter);
				if ($scope.leftCounter <= 0) {
					$scope.refreshInitial();
					$scope.intervalCounter = 0;
					$timeout(function() {
						$scope.updateTripsLive();
					}, 500);
					$interval(function() {
						$scope.updateTripsLive();
					}, 3000);
				}
			}
		});
	};
	$scope.refreshInitial = function() {
		leafletData.getMap().then(function(map) {
			if ($scope.trips.length > 0) {
				var trip = $scope.trips[0];
				$scope.input.showTrips[trip.trip_id] = true;
				$scope.refreshLayers(map);
				$scope.zoomToTrip(trip.trip_id);
			} else {
				var box = [[31.06867403, 34.60432436], [33.00500359, 35.18816094]];
				map.fitBounds(box);
			};
			$timeout(function() {
				$scope.initialDone = true;
			}, 500);
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
	console.log(10);
	$scope.tripId = $scope.trip.trip_id;
	$scope.tripData = $scope.tripDatas[$scope.tripId];
}]);
