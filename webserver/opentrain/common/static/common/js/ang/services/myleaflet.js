"use strict";

var services = angular.module('my.leaflet', ['my.services']);

services.factory('MyLeaflet', ['MyUtils',
function(MyUtils) {
	return {
		trainIcon : L.icon({
			iconUrl : '/static/common/img/open-train.png',
			iconSize : [26, 26],
			iconAnchor : [12, 25]
		}),
		expIcon : L.icon({
			iconUrl : '/static/common/img/exp.png',
			iconSize : [26, 26],
			iconAnchor : [12, 25],
		}),
		curIcon : L.icon({
			iconUrl : '/static/common/img/cur.png',
			iconSize : [26, 26],
			iconAnchor : [12, 25],
		}),
		getTripMarker : function(loc, tripData, kind) {
			if (kind != 'cur' && kind != 'exp') {
				alert('wrong kind ' + kind);
				return;
			}
			var is_cur = kind == 'cur';
			var trip_pt = is_cur ? loc.cur_point : loc.exp_point;
			if (!trip_pt) {
				return null;
			}
			var title = '<b>' + ( is_cur ? gettext('cur') : gettext('exp')) + '</b> @ ' + gettext(tripData.stop_times[0].stop.stop_name) + ' ' + gettext('to') + ' ' + gettext(tripData.stop_times[tripData.stop_times.length - 1].stop.stop_name);
			var icon = is_cur ? this.curIcon : this.expIcon;
			return L.marker(trip_pt, {
				icon : icon,
				title : title,
			}).bindPopup(title);
		},
		drawShapes : function(points) {
			var polyline = this.createLine(null, points, {
				color : '#0000CD',
				weight : 3,
				stroke : true,
			});
			return polyline;
		},
		drawStops : function(stops) {
			var that = this;
			var result = [];
			stops.forEach(function(stop) {
				var text = gettext(stop.stop_name);
				var pt = stop.latlon;
				var marker = L.marker(pt, {
					icon : that.trainIcon
				}).bindPopup(text);
				result.push(marker);
			});
			return result;
		},
		findBoundBox : function(points) {
			var initialBox = [[points[0][0], points[0][1]], [points[0][0], points[0][1]]];
			return points.reduce(function(box, p) {
				return [[Math.min(box[0][0], p[0]), Math.min(box[0][1], p[1])], [Math.max(box[1][0], p[0]), Math.max(box[1][1], p[1])]];
			}, initialBox);
		},
		removeAllLayers : function(m) {
			for (var i in m._layers) {
				if (m._layers[i]._path != undefined) {
					try {
						m.removeLayer(m._layers[i]);
					} catch(e) {
						console.log("problem with " + e + m._layers[i]);
					}
				}
			}
		},
		showReports : function(map, reports, showConfig) {
			showConfig = showConfig || {};
			var box = showConfig.box;
			var initialPoint = showConfig.initialPoint;
			var that = this;
			var points = [];
			if (initialPoint) {
				points.push(initialPoint);
			}
			reports.forEach(function(r) {
				if (r.loc) {
					points.push([r.loc.lat, r.loc.lon]);
				}
			});
			var polyline = this.createLine(map, points, {
				color : '#0000CD',
				weight : 3,
				stroke : true,
			});
			if (box) {
				map.fitBounds(box);
			};
			reports.forEach(function(report) {
				if (report.loc) {
					var pt = [report.loc.lat, report.loc.lon];
					var text = '<a href="/analysis/report-details/?report_id=' + report.id + '">' + report.id + '</a><br/>' + MyUtils.toHourMinSec(report.timestamp);
					if (report.is_station) {
						L.marker(pt, {
							icon : that.trainIcon
						}).addTo(map).bindPopup(text);
					} else {
						L.circleMarker(pt, {
							radius : 5,
							color : '#0000CD',
							fill : true,
						}).addTo(map).bindPopup(text);
					}
				}
			});
		},
		createLine : function(map, points, options) {
			var polyline = L.polyline(points, options);
			if (map != null) {
				polyline.addTo(map);
			};
			return polyline;
		},
	};
}]);
