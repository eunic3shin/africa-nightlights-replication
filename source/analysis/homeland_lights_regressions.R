# Reproduce the three final STEP16 specifications from archived inputs.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 4L) {
  stop("Usage: Rscript paper_tables.R LEVELS POPULATION DISTANCE OUTPUT_CSV")
}
levels <- read.csv(args[1])
population <- read.csv(args[2])[c("TRIBE_C", "land_ar", "sum")]
distance <- read.csv(args[3])
names(levels)[names(levels) == "TRIBE_C"] <- "TRIBE_CODE"
names(population) <- c("TRIBE_CODE", "land_area", "pop2010")
x <- merge(
  merge(levels, population, by = "TRIBE_CODE", all.x = TRUE),
  distance, by = "TRIBE_CODE", all.x = TRUE
)
x <- x[complete.cases(x[c("avg_loglights","logexports","pop2010","land_area","dist_coast_km")]),]
x$lights_total <- exp(x$avg_loglights)-1
x$lightspc_1e6 <- x$lights_total/pmax(x$pop2010,1)*1e6
x$logdistcoast <- log1p(x$dist_coast_km)
x$log_lights_km2 <- log1p(x$lights_total/pmax(x$land_area,1))
models <- list(
  lm(lightspc_1e6 ~ logexports, data = x),
  lm(lightspc_1e6 ~ logexports + logdistcoast, data = x),
  lm(log_lights_km2 ~ logexports + logdistcoast, data = x)
)
rows <- lapply(seq_along(models), function(i) {
  fit <- models[[i]]
  coefs <- coef(summary(fit))
  data.frame(
    model = i, term = rownames(coefs), estimate = coefs[, 1],
    se = coefs[, 2], p = coefs[, 4], n = nobs(fit),
    r2 = summary(fit)$r.squared
  )
})
dir.create(dirname(args[4]), recursive = TRUE, showWarnings = FALSE)
write.csv(do.call(rbind, rows), args[4], row.names = FALSE)
