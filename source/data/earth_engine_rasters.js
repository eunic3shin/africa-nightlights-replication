// Historical Africa raster exports, supplied by the author.
// This is a separate workflow from the homeland panel: annual satellite mean.
var dmsp = ee.ImageCollection('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS');
var africaBox = ee.Geometry.Rectangle({
  coords: [-20, -35, 55, 38],
  geodesic: false
});
var years = [
  1992, 1993, 1994, 1995, 1996, 1997,
  1998, 1999, 2000, 2001, 2002, 2003,
  2004, 2005, 2006, 2007, 2008, 2009,
  2010, 2011, 2012, 2013
];
years.forEach(function(year) {
  var img = dmsp
    .filter(ee.Filter.calendarRange(year, year, 'year'))
    .select('stable_lights')
    .mean()
    .clip(africaBox);
  if (year === 2013) {
    Map.clear();
    Map.centerObject(africaBox, 3);
    Map.addLayer(img, {min: 0, max: 63}, 'DMSP Africa ' + year);
  }
  Export.image.toDrive({
    image: img,
    description: 'dmsp_' + year + '_africa_box',
    folder: 'earthengine_dmsp',
    fileNamePrefix: 'dmsp_' + year,
    region: africaBox,
    scale: 1000,
    crs: 'EPSG:4326',
    maxPixels: 1e13
  });
});
