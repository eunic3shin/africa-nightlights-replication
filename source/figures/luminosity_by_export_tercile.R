# Port STEP17's master-panel tercile series to a standalone build target.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) {
  stop("Usage: Rscript panel_figures.R MASTER_PANEL OUTPUT_DIR")
}
columns <- c("TRIBE_CODE", "year", "log_lights", "ttl_xpr")
header <- names(read.csv(args[1], nrows = 0L))
stopifnot(all(columns %in% header))
panel <- read.csv(args[1], colClasses = ifelse(header %in% columns, "numeric", "NULL"))
sample <- panel[!is.na(panel$ttl_xpr), ]
sample <- sample[order(sample$TRIBE_CODE), ]
exports <- sample[!duplicated(sample$TRIBE_CODE), c("TRIBE_CODE", "ttl_xpr")]
# Match dplyr::ntile: rank ties by row order and put larger groups first.
exports <- exports[order(exports$ttl_xpr), ]
n <- nrow(exports)
stopifnot(n >= 3L)
sizes <- n %/% 3L + (seq_len(3L) <= n %% 3L)
exports$tercile <- rep(seq_len(3L), sizes)
panel$tercile <- exports$tercile[match(panel$TRIBE_CODE, exports$TRIBE_CODE)]
series <- aggregate(log_lights ~ year + tercile, panel, mean)
series <- series[order(series$tercile, series$year), ]

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

dir.create(args[2], recursive = TRUE, showWarnings = FALSE)
write.csv(series, file.path(args[2], "figure_4_data.csv"), row.names = FALSE)
palette <- c("#E41A1C", "#377EB8", "#4DAF4A")
image_path <- file.path(args[2], "figure_4.png")
if (file.exists(image_path)) unlink(image_path)
open_png(image_path, width = 2250, height = 1350)
plot(range(series$year), range(series$log_lights), type = "n", xlab = "",
     ylab = "Mean log night lights",
     main = "Average luminosity over time by slave-export tercile")
grid()
abline(v = 2010, lty = 3, col = "grey60")
for (i in seq_len(3L)) {
  group <- series[series$tercile == i, ]
  lines(group$year, group$log_lights, col = palette[i], lwd = 2)
}
legend("topleft", legend = seq_len(3L), col = palette, lty = 1, bty = "n",
       title = "Slave-export tercile")
finish_png(image_path)
