// Historical GPW population export, supplied by the author.
// Only the project-specific asset path is replaced.
var homelands = ee.FeatureCollection('projects/YOUR_PROJECT/assets/homelands_exports');
var gpw = ee.ImageCollection('CIESIN/GPWv411/GPW_Population_Count');
var year = 2010;
var pop2010 = gpw
  .filterDate(year + '-01-01', (year + 1) + '-01-01')
  .first()
  .select('population_count');
var popPerHomeland = pop2010.reduceRegions({
  collection: homelands,
  reducer: ee.Reducer.sum(),
  scale: 1000
});
popPerHomeland = popPerHomeland.map(function(f) {
  return f.set('year', year);
});
print('Sample pop per homeland', popPerHomeland.limit(5));
Export.table.toDrive({
  collection: popPerHomeland,
  description: 'homelands_pop_2010',
  fileFormat: 'CSV'
});
