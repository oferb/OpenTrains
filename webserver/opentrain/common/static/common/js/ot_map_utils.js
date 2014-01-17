// utility functions for open layers
"use strict";

function MapWrapper() {
	this.trainIcon = L.icon({
		iconUrl : '/static/common/img/open-train.png',
		iconSize : [26, 26]
	});
	this.createTrainMarker = function(stop) {
		var marker = L.marker([stop.lat, stop.lon], {
			icon : this.trainIcon
		}).addTo(this.map);
		var popup = marker.bindPopup('(' + stop.seqId + ') ' + stop.name + "<br/>@" + stop.time);
		if (stop.stopId == this.zoomStopId) {
			popup.openPopup();
		}
	};
	this.createReportsLine = function(reports) {
		var points = [];
		reports.forEach(function(r) {
			points.push([r.lat, r.lon]);
		});
		var that = this;
		var polyline = this.createLineAndZoom(points,{
			color: '#0000CD',
			weight : 3,
			stroke : true,
		});
		points.forEach(function(pt,index) {
			var text = that.toHourMinSec(reports[index].timestamp);
			console.log(text);
			L.circleMarker(pt,{
				radius: 5,
				color: '#0000CD',
				fill : true,
			}).addTo(that.map).bindPopup(text);
		});
		
		
	};
	this.toHourMinSec = function(dt) {
		var h = dt.getHours();
		var m = dt.getMinutes();
		var s = dt.getSeconds();
		m = m < 10 ? '0' + m : '' + m;
		s = s < 10 ? '0' + s : '' + s;
		return '' + h + ':' + m + ':' + s; 
	};
	this.createLine = function(points, options) {
		var polyline = L.polyline(points, options).addTo(this.map);
		return polyline;
	};
	this.createLineAndZoom = function(points, options) {
		var polyline = this.createLine(points,options);
		this.map.fitBounds(polyline.getBounds());
		return polyline;
	};
	this.setDefaultZoom = function() {
		this.map.setView(this.center, 13);
	};
}

function otCreateMap(mapDiv, options) {
	options = options || {};
	var map = L.map(mapDiv);
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom : 18,
		attribution : 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>'
	}).addTo(map);
	var result = new MapWrapper();
	if (options.zoomStopId) {
		result.zoomStopId = options.zoomStopId;
	}
	result.map = map;
	result.center = [options.lat,options.lon];
	return result;
}

