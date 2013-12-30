// utility functions for open layers

function getLonLat(lon,lat) {
	var fromProjection = new OpenLayers.Projection("EPSG:4326");   // Transform from WGS 1984
    var toProjection   = new OpenLayers.Projection("EPSG:900913"); // to Spherical Mercator Projection
    return new OpenLayers.LonLat(lon,lat).transform( fromProjection, toProjection); 
}


