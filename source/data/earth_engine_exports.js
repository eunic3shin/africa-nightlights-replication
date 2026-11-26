// Historical homeland-year DMSP export, supplied by the author.
// Only the project-specific asset path is replaced.
// IMPORTANT: first image per year, not mean of satellite composites.
var homelands = ee.FeatureCollection('projects/YOUR_PROJECT/assets/homelands_exports');
var years = ee.List.sequence(1992, 2013);
var dmsp = ee.ImageCollection('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS')
  .select('stable_lights');
var addYearLights = function(y) {
  y = ee.Number(y);
  var img = dmsp.filter(ee.Filter.calendarRange(y, y, 'year'))
                .first();
  var reduced = img.reduceRegions({
    collection: homelands,
    reducer: ee.Reducer.mean(),
    scale: 1000
  });
  return reduced.map(function(f) {
    return f.set('year', y);
  });
};
var panel = ee.FeatureCollection(years.map(addYearLights)).flatten();
print(panel.limit(5));
Export.table.toDrive({
  collection: panel,
  description: 'homelands_dmsp_panel',
  fileFormat: 'CSV'
});
