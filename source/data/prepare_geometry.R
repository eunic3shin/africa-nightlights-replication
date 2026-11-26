# Recovered historical Murdock/ethnic-export join.
library(sf)
library(dplyr)
library(haven)
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==3)
h <- st_read(args[1],quiet=TRUE) %>% group_by(TRIBE_CODE,NAME) %>% summarise(.groups="drop")
e <- read_dta(args[2]) %>% mutate(total_atlantic=atlantic_all_years,total_indian=indian_all_years,
                                  total_exports=total_atlantic+total_indian)
h <- left_join(h,e,by=c("NAME"="murdock_name"))
dir.create(dirname(args[3]),recursive=TRUE,showWarnings=FALSE)
st_write(h,args[3],delete_dsn=TRUE,quiet=TRUE)
