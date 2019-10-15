/* Heatmaps of some data I pulled from Yelp
 * Uses Leaflet.heatmap plugin: https://github.com/Leaflet/Leaflet.heat
 */

(function($){
$("#map").ready(function(){

  var defaultMapOptions = {
  };

  var map = L.map('map').setView([37.75, -122.41], 12);
  var tiles = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  var mapLayerControl = L.control.layers({}).addTo(map);

  var minLng = -122.52,
      maxLng = -122.35,
      minLat = 37.708,
      maxLat = 37.816;
	function filterPointsToBounds(points) {
    return _.filter(points, function(p) {
      return (p[0] <= maxLat && p[0] >= minLat &&
              p[1] <= maxLng && p[1] >= minLng);
    });
	}

  function addPointsToMap(layerName, points) {
    mapLayerControl.addBaseLayer(
      L.heatLayer(points, defaultMapOptions).addTo(map),
      layerName
    );
		$(mapLayerControl._form).find('input[type=radio]')[0].click();
  }

  // Load local JSON data
  $.getJSON("data/yelp_price_points.json", function(points) {
    points = filterPointsToBounds(points);
    addPointsToMap("Business price point", points);
  });

  $.getJSON("data/yelp_rating_points.json", function(points) {
    points = filterPointsToBounds(points);
    addPointsToMap("Business ratings", points);
  });

  $.getJSON("data/yelp_review_count_points.json", function(points) {
    points = filterPointsToBounds(points);
    addPointsToMap("Business review count", points);
		console.log(points);
		console.log(getHistogram(_.pluck(points, 2)));
  });

	// Histogram fuckery
	function getHistogram(values) {
		console.log(values);
		var scale = d3.scaleLog().domain(
			[_.max([1, _.min(values)]), _.max(values)]);
		var hist = d3.histogram()
			.domain(scale.domain())
			.thresholds(scale.ticks(4))
			(values);
		return _.map(hist, function(bin) {
			return {x0: bin.x0, x1: bin.x1, count: bin.length}
		});
	}

});
})(jQuery);
