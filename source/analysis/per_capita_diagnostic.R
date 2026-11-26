# Reproduce STEP13.ipynb from its archived regression dataset.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) {
  stop("Usage: Rscript lights_per_capita.R INPUT_CSV OUTPUT_CSV")
}
# The archived coefficient table identifies "NA" as a country factor level.
cs <- read.csv(args[1], na.strings = "", colClasses = c(country = "character"))
numeric_columns <- c("log_lights_pc", "log_lights_km2", "log_exports", "log_dist_coast")
cs[numeric_columns] <- lapply(cs[numeric_columns], type.convert, as.is = TRUE)
if (anyDuplicated(cs[c("TRIBE_CODE", "country")])) {
  stop("Expected at most one row per TRIBE_CODE and country")
}

m1 <- lm(log_lights_pc ~ log_exports + factor(country), data = cs)
m2 <- lm(log_lights_pc ~ log_exports + log_dist_coast + factor(country), data = cs)
m3 <- lm(log_lights_km2 ~ log_exports + log_dist_coast + factor(country), data = cs)

c1 <- coef(summary(m1))
c2 <- coef(summary(m2))
c3 <- coef(summary(m3))
out <- data.frame(
  model = c("pc_no_coast", "pc_with_coast", "km2_with_coast"),
  n = c(nobs(m1), nobs(m2), nobs(m3)),
  beta_exports = c(c1["log_exports", 1], c2["log_exports", 1], c3["log_exports", 1]),
  se_exports = c(c1["log_exports", 2], c2["log_exports", 2], c3["log_exports", 2]),
  beta_coast = c(NA, c2["log_dist_coast", 1], c3["log_dist_coast", 1]),
  se_coast = c(NA, c2["log_dist_coast", 2], c3["log_dist_coast", 2]),
  r2 = c(summary(m1)$r.squared, summary(m2)$r.squared, summary(m3)$r.squared)
)
dir.create(dirname(args[2]), recursive = TRUE, showWarnings = FALSE)
write.csv(out, args[2], row.names = FALSE)
