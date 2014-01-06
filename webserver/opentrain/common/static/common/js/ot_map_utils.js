// utility functions for open layers
"use strict";

function getLonLat(lon,lat) {
	var fromProjection = new OpenLayers.Projection("EPSG:4326");   // Transform from WGS 1984
    var toProjection   = new OpenLayers.Projection("EPSG:900913"); // to Spherical Mercator Projection
    var result = new OpenLayers.LonLat(lon,lat);
    return result.transform( fromProjection, toProjection);
}
     
function getPoint(lon,lat) {
	var lonlat = getLonLat(lon,lat);
	return new OpenLayers.Geometry.Point(lonlat.lon,lonlat.lat);
}


function getOtIcon() {
	return new OpenLayers.Icon("/static/common/img/open-train.png", {
		w : 26,
		h : 26
	});
}



