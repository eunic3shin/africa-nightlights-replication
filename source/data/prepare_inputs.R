# Recovered preprocessing from historical research notebooks.
# Requires R packages readr, dplyr, sf, haven, rnaturalearth, rnaturalearthdata.
# Usage: Rscript source/data/prepare_inputs.R data/raw data
# Earth Engine exports must already exist; original export scripts are included.
library(readr)
library(dplyr)
library(sf)
library(haven)
library(rnaturalearth)
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==2)
raw <- args[1]; out <- args[2]
dir.create(out, recursive=TRUE, showWarnings=FALSE)
# Historical Data_Viz: dissolve by tribe/name, join ethnic exports by name.
h <- st_read(file.path(raw,"Murdock_Map_2020.shp"), quiet=TRUE)
e <- read_dta(file.path(raw,"tribe_level_slave_exports_Atlantic_Indian.dta")) %>%
  mutate(total_atlantic=atlantic_all_years,total_indian=indian_all_years,
         total_exports=total_atlantic+total_indian)
h <- h %>% group_by(TRIBE_CODE,NAME) %>% summarise(.groups="drop") %>%
  left_join(e,by=c("NAME"="murdock_name"))
# exports_tribes: aggregate exports; preserve original missing-value treatment.
exports <- h %>% st_drop_geometry() %>% group_by(TRIBE_CODE) %>%
  summarise(totalexports=sum(total_exports,na.rm=TRUE),.groups="drop")
write_csv(exports,file.path(out,"exports_by_tribe.csv"))
# dist_coast_tribe: medium-scale coast, EPSG:3857, no deduplication.
coast <- st_transform(ne_coastline(scale="medium",returnclass="sf"),3857)
cent <- st_centroid(st_transform(h,3857))
dist <- h %>% st_drop_geometry() %>%
  mutate(dist_coast_km=as.numeric(st_distance(cent,coast[st_nearest_feature(cent,coast),],by_element=TRUE))/1000) %>%
  select(TRIBE_CODE,dist_coast_km)
write_csv(dist,file.path(out,"distance_coast_by_tribe.csv"))
# master_panel: original Earth Engine CSV and spatial country join.
countries <- ne_countries(continent="Africa",scale="medium",returnclass="sf") %>% select(country=admin)
crosswalk <- st_join(h,countries,left=TRUE) %>% st_drop_geometry() %>%
  select(TRIBE_CODE,tribe_name=NAME,country) %>% distinct()
panel <- read_csv(file.path(raw,"homelands_dmsp_panel.csv"),show_col_types=FALSE)
master <- panel %>% rename(TRIBE_CODE=TRIBE_C,mean_light=mean,land_area=land_ar) %>%
  left_join(crosswalk,by="TRIBE_CODE") %>% mutate(log_lights=log1p(mean_light)) %>%
  relocate(TRIBE_CODE,tribe_name,country,year)
write_csv(master,file.path(out,"homelands_dmsp_panel_master.csv"))
# Historical levels construction: mean log lights, not log mean lights.
levels <- panel %>% mutate(loglights=log1p(mean),logexports=log1p(ttl_xpr)) %>%
  filter(year>=2000,year<=2013) %>% group_by(TRIBE_C) %>%
  summarise(avg_loglights=mean(loglights,na.rm=TRUE),logexports=mean(logexports,na.rm=TRUE),.groups="drop")
write_csv(levels,file.path(out,"levels_df.csv"))
# Growth: first/last nonmissing log lights, retain country join multiplicity.
growth <- master %>% arrange(TRIBE_CODE,year) %>% group_by(TRIBE_CODE) %>%
  summarise(log_lights_early=first(log_lights[!is.na(log_lights)]),
            log_lights_late=last(log_lights[!is.na(log_lights)]),
            year_early=min(year,na.rm=TRUE),year_late=max(year,na.rm=TRUE),.groups="drop") %>%
  mutate(d_log_lights=log_lights_late-log_lights_early) %>% left_join(exports,by="TRIBE_CODE") %>%
  left_join(distinct(select(master,TRIBE_CODE,country)),by="TRIBE_CODE") %>%
  mutate(log_exports=log1p(totalexports)) %>% filter(!is.na(d_log_lights),!is.na(log_exports),!is.na(country))
write_csv(growth,file.path(out,"growthdf.csv"),na="")
# Country totals, then average over 2000-2013.
ctry <- master %>% filter(!is.na(country)) %>% group_by(country,year) %>%
  summarise(totallight=sum(mean_light*land_area,na.rm=TRUE),land_area=sum(land_area,na.rm=TRUE),.groups="drop") %>%
  filter(year>=2000,year<=2013) %>% group_by(country) %>%
  summarise(meanlight20002013=mean(totallight,na.rm=TRUE),land_area=first(land_area),.groups="drop")
write_csv(ctry,file.path(out,"ctrylights.csv"))
# Per-capita cross-section: original diagnostic's first/sum rules.
pop <- read_csv(file.path(raw,"homelands_pop_2010.csv"),show_col_types=FALSE)
lights <- panel %>% mutate(TRIBE_C=as.character(TRIBE_C)) %>% filter(year>=2000,year<=2013) %>%
  group_by(TRIBE_C) %>% summarise(meanlight_2000_2013=mean(mean,na.rm=TRUE),.groups="drop")
pop_cs <- pop %>% mutate(TRIBE_C=as.character(TRIBE_C)) %>% group_by(TRIBE_C) %>%
  summarise(pop2010=sum(sum,na.rm=TRUE),.groups="drop")
cs <- master %>% mutate(TRIBE_CODE=as.character(TRIBE_CODE),totalexports=as.numeric(ttl_xpr),land_area=as.numeric(land_area)) %>%
  group_by(TRIBE_CODE,country) %>% summarise(totalexports=first(totalexports),land_area=first(land_area),.groups="drop") %>%
  left_join(lights,by=c("TRIBE_CODE"="TRIBE_C")) %>% left_join(pop_cs,by=c("TRIBE_CODE"="TRIBE_C")) %>%
  left_join(dist %>% mutate(TRIBE_CODE=as.character(TRIBE_CODE)) %>% group_by(TRIBE_CODE) %>%
              summarise(dist_coast_km=first(dist_coast_km),.groups="drop"),by="TRIBE_CODE") %>%
  mutate(lights_pc=meanlight_2000_2013/pop2010,log_lights_pc=log1p(lights_pc),
         log_exports=log1p(totalexports),log_dist_coast=log1p(dist_coast_km),
         log_lights_km2=log1p(meanlight_2000_2013/land_area))
write_csv(cs,file.path(out,"homeland_lights_pc_regdata.csv"),na="")
for (name in c("homelands_pop_2010.csv","slave_trade_QJE.dta"))
  if (!file.copy(file.path(raw,name),file.path(out,name),overwrite=TRUE)) stop("Cannot copy ",name)
