# Redraw spatial figures using recovered map/boxplot transformations.
library(sf)
library(dplyr)
library(readr)
library(ggplot2)
library(rnaturalearth)
library(patchwork)
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==4)
h <- st_read(args[1],quiet=TRUE)
panel <- read_csv(args[2],show_col_types=FALSE)
dist <- read_csv(args[3],show_col_types=FALSE)
out <- args[4]; dir.create(out,recursive=TRUE,showWarnings=FALSE)
countries <- ne_countries(continent="Africa",scale="medium",returnclass="sf") %>% select(country=admin)
hc <- st_join(h,countries,left=TRUE)
tribes <- hc %>% group_by(TRIBE_CODE) %>% summarise(total_exports=sum(total_exports,na.rm=TRUE),.groups="drop")
totals <- hc %>% st_drop_geometry() %>% group_by(country) %>%
  summarise(total_exports=sum(total_exports,na.rm=TRUE),.groups="drop")
cm <- left_join(countries,totals,by="country")
lim <- range(log1p(c(tribes$total_exports,cm$total_exports)),na.rm=TRUE)
theme_map <- theme_void() + theme(legend.position="bottom",plot.title=element_text(hjust=.5))
map <- function(d,title,limits=NULL) ggplot() + geom_sf(data=countries,fill="grey95",color="grey70") +
  geom_sf(data=d,aes(fill=value),linewidth=.1) + scale_fill_viridis_c(limits=limits,na.value="grey90") +
  labs(title=title,fill=NULL) + theme_map
a <- map(mutate(cm,value=log1p(total_exports)),"Country slave exports",lim)
b <- map(mutate(tribes,value=log1p(total_exports)),"Homeland slave exports",lim)
ggsave(file.path(out,"figure_1.png"),a+b,width=12,height=6,dpi=300)
growth <- panel %>% arrange(TRIBE_CODE,year) %>% group_by(TRIBE_CODE) %>%
  summarise(value=last(log_lights[!is.na(log_lights)])-first(log_lights[!is.na(log_lights)]),.groups="drop")
g <- left_join(h,growth,by="TRIBE_CODE")
br <- unique(quantile(g$value,seq(0,1,.2),na.rm=TRUE))
g$category <- cut(g$value,br,include.lowest=TRUE)
ggsave(file.path(out,"figure_2.png"),ggplot(g)+geom_sf(aes(fill=category),color=NA)+
  scale_fill_brewer(palette="YlOrRd",na.value="grey90")+theme_map,width=7,height=6,dpi=300)
# Historical Figure 3 label says per capita; its code actually divided by land area.
hp <- panel %>% group_by(TRIBE_CODE) %>% summarise(value=mean(mean_light/land_area,na.rm=TRUE)+1e-7,.groups="drop")
cp <- panel %>% group_by(country) %>% summarise(value=mean(mean_light/land_area,na.rm=TRUE)+1e-7,.groups="drop")
ggsave(file.path(out,"figure_3_homeland.png"),map(left_join(h,hp,by="TRIBE_CODE") %>% mutate(value=log10(value)),"Homeland lights / land area (log10)"),width=9,height=6,dpi=300)
ggsave(file.path(out,"figure_3_country.png"),map(left_join(countries,cp,by="country") %>% mutate(value=log10(value)),"Country lights / land area (log10)"),width=9,height=6,dpi=300)
levels <- panel %>% filter(year>=2000,year<=2013) %>% group_by(TRIBE_CODE) %>%
  summarise(loglights_lvl=log1p(mean(exp(log_lights)-1,na.rm=TRUE)),.groups="drop") %>%
  left_join(dist,by="TRIBE_CODE") %>% mutate(coastal=dist_coast_km<=100) %>% filter(!is.na(coastal))
ggsave(file.path(out,"figure_6.png"),ggplot(levels,aes(x=coastal,y=loglights_lvl))+geom_boxplot()+
  labs(x="Coastal homeland (within 100 km)",y="Log average night lights, 2000–2013")+theme_minimal(),width=7,height=5,dpi=300)
