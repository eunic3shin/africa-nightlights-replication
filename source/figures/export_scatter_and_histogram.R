# Redraw the scatter and histogram using archived homeland inputs.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3L) {
  stop("Usage: Rscript rebuild_figures.R REGDATA EXPORTS OUTPUT_DIR")
}
lights <- read.csv(args[1])
exports <- read.csv(args[2])
lights <- lights[!duplicated(lights$TRIBE_CODE), c("TRIBE_CODE", "meanlight_2000_2013")]
data <- merge(lights, exports, by = "TRIBE_CODE")
positive <- subset(data, totalexports > 0 & meanlight_2000_2013 > 0)
x <- log(positive$totalexports)
y <- log(positive$meanlight_2000_2013)
fit <- lm(y ~ x)
line_x <- seq(min(x), max(x), length.out = 100)
interval <- predict(fit, newdata = data.frame(x = line_x), interval = "confidence")


open_png <- function(path, width, height) {
  device <- if (Sys.info()[["sysname"]] == "Darwin") "quartz" else "cairo"
  png(path, width = width, height = height, res = 300, type = device)
  if (dev.cur() == 1L) {
    stop("Could not open the PNG graphics device: ", device)
  }
}

finish_png <- function(path) {
  invisible(dev.off())
  if (!file.exists(path) || file.size(path) == 0) {
    stop("PNG graphics device did not write ", path)
  }
}

dir.create(args[3], recursive = TRUE, showWarnings = FALSE)
image_path <- file.path(args[3], "figure_5.png")
if (file.exists(image_path)) unlink(image_path)
open_png(image_path, width = 2400, height = 1800)
plot(x, y, type = "n", xlab = "Log slave exports", ylab = "Log mean lights 2000-2013",
     main = "Slave exports vs modern luminosity")
grid()
polygon(c(line_x, rev(line_x)), c(interval[, "lwr"], rev(interval[, "upr"])),
        col = "grey85", border = NA)
points(x, y, pch = 16, cex = 0.55, col = "#00000099")
lines(line_x, interval[, "fit"], col = "red", lwd = 2)
finish_png(image_path)

image_path <- file.path(args[3], "figure_7.png")
if (file.exists(image_path)) unlink(image_path)
open_png(image_path, width = 1950, height = 1350)
hist(log1p(exports$totalexports), breaks = seq(0, max(log1p(exports$totalexports)), length.out = 31),
     col = "steelblue", border = "white", xlab = "log(slave exports + 1)",
     ylab = "Number of ethnic homelands",
     main = "Distribution of historical slave exports across homelands")
finish_png(image_path)
