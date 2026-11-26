// RECONSTRUCTION, not the recovered original Earth Engine script.
// Upload the joined homeland geometry to your own Earth Engine assets.
// Set the asset ID and use the same geometry for both exports.
// Explicit assumptions: stable_lights band, mean of available satellite composites
// per calendar year, native nominal pixel scale, GPW v4.11 2010 count sum.
// These choices have not been validated against the historical exports.
var asset = 'projects/YOUR_PROJECT/assets/homelands_exports';
var h = ee.FeatureCollection(asset).map(function(f) {
  return ee.Feature(f.geometry(), {
    TRIBE_C: f.get('TRIBE_CODE'),
    NAME: f.get('NAME'),
    ttl_xpr: f.get('total_exports'),
    land_ar: f.get('land_area')
  });
});
var lights = ee.ImageCollection('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS').select('stable_lights');
var annual = ee.FeatureCollection(ee.List.sequence(1992, 2013).map(function(y) {
  y = ee.Number(y);
  var start = ee.Date.fromYMD(y,1,1);
  var series = lights.filterDate(start,start.advance(1,'year'));
  var img = series.mean().setDefaultProjection(lights.first().projection());
  return img.reduceRegions({
    collection: h, reducer: ee.Reducer.mean(),
    scale: lights.first().projection().nominalScale(), tileScale: 4
  }).map(function(f) {return f.set('year',y);});
})).flatten();
Export.table.toDrive({
  collection: annual, description: 'homelands_dmsp_panel',
  fileFormat: 'CSV', selectors: ['TRIBE_C','NAME','ttl_xpr','land_ar','year','mean']
});
var pop = ee.ImageCollection('CIESIN/GPWv411/GPW_Population_Count')
  .filterDate('2010-01-01','2011-01-01').first().select('population_count');
var population = pop.reduceRegions({
  collection: h, reducer: ee.Reducer.sum(),
  scale: pop.projection().nominalScale(), tileScale: 4
});
Export.table.toDrive({
  collection: population, description: 'homelands_pop_2010',
  fileFormat: 'CSV', selectors: ['TRIBE_C','NAME','ttl_xpr','land_ar','sum']
});
