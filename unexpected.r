library("tidyverse")
library("RcppRoll")

Z_THRESHOLD <- -2.0

data <- read_csv("joined.sedes-metrical_shape.csv", col_types = cols(
	work = col_character(),
	book_n = col_character(),
	line_n = col_character(),
	x = col_double(),
	z = col_double(),
)) %>% mutate(
	is_unexpected = !is.na(z) & z <= Z_THRESHOLD,
	era = fct(case_when(
		work %in% c("Il.", "Od.", "Hom.Hymn", "Theog.", "W.D.", "Sh.") ~ "archaic",
		work %in% c("Argon.", "Callim.Hymn", "Phaen.", "Theoc.") ~ "hellenistic",
		work %in% c("Q.S.", "Dion.") ~ "imperial",
	), levels = c("archaic", "hellenistic", "imperial")),
)

if (any(is.na(data$era))) {
	stop()
}

cat(sprintf("z threshold is <= %+.2f\n", Z_THRESHOLD))

num_words <- nrow(data)
num_unexpected <- nrow(filter(data, is_unexpected))

cat(sprintf("Percentage of unexpected words %d/%d = %.2f%%\n", num_unexpected, num_words, num_unexpected / num_words * 100))

cat("\n")

cat("Iliad\n")

iliad <- filter(data, work == "Il.")

num_words_iliad <- nrow(iliad)
num_unexpected_iliad <- nrow(filter(iliad, is_unexpected))
cat(sprintf("Percentage of unexpected words %d/%d = %.2f%%\n", num_unexpected_iliad, num_words_iliad, num_unexpected_iliad / num_words_iliad * 100))
cat(sprintf("Unexpected words per book %d/%d = %.2f\n", num_unexpected_iliad, 24, num_unexpected_iliad / 24))
cat(sprintf("Average words per book %d/%d = %.2f\n", num_words_iliad, 24, num_words_iliad / 24))
print(iliad %>% group_by(book_n) %>% summarize(num_words = n(), num_unexpected = sum(is_unexpected, na.rm = TRUE), pct_unexpected = num_unexpected / num_words * 100, era = first(era)) %>% arrange(pct_unexpected), n = 100)

cat("\n")

cat("Longer poems, by book\n")

print(data %>% group_by(work, book_n) %>% summarize(num_words = n(), num_unexpected = sum(is_unexpected, na.rm = TRUE), pct_unexpected = num_unexpected / num_words * 100, era = first(era), .groups = "drop") %>% filter(num_words > 1000) %>% arrange(pct_unexpected), n = 500)

cat("\n")

cat("By work\n")

print(data %>% group_by(work) %>% summarize(num_words = n(), num_unexpected = sum(is_unexpected, na.rm = TRUE), pct_unexpected = num_unexpected / num_words * 100, era = first(era), .groups = "drop") %>% filter(num_words > 1000) %>% arrange(pct_unexpected), n = 500)

cat("\n")

cat("By era\n")

print(data %>% group_by(era) %>% summarize(num_words = n(), num_unexpected = sum(is_unexpected, na.rm = TRUE), pct_unexpected = num_unexpected / num_words * 100, era = first(era), .groups = "drop") %>% filter(num_words > 1000) %>% arrange(pct_unexpected), n = 500)

cat("\n")

cat("Unexpected shapes per window of 50 words, archaic corpus\n")

data <- data %>%
	group_by(work, book_n) %>%
	mutate(unexpected_50 = roll_sum(is_unexpected, 50, align = "left", fill = NA)) %>%
	ungroup()

archaic_data <- filter(data, era == "archaic")
summary(archaic_data$unexpected_50)
x <- table(archaic_data$unexpected_50)
x
x / sum(x) * 100
cumsum(x) / sum(x) * 100
p <- ggplot(archaic_data) +
	geom_bar(aes(unexpected_50)) +
	scale_x_continuous(breaks = 0:10) +
	scale_y_continuous(minor_breaks = waiver()) +
	labs(
		x = "Number of unexpected shapes in window",
		y = "Number of distinct windows",
		title = bquote("Unexpected shapes (" * italic(z) ~ "≤" ~ .(gsub("-", "−", sprintf("%-.1f", Z_THRESHOLD))) * ") per window of 50 lines, Archaic corpus")
	)
ggsave("unexpected-window-50.archaic.png", p, width = 7.5, height = 3, dpi = 200)
p <- ggplot(archaic_data) +
	stat_ecdf(aes(unexpected_50), geom = "bar") +
	scale_x_continuous(breaks = 0:10) +
	scale_y_continuous(n.breaks = 11, labels = scales::percent, minor_breaks = NULL) +
	labs(
		x = "Number of unexpected shapes in window",
		y = "Number of distinct windows",
		title = bquote("Unexpected shapes (" * italic(z) ~ "≤" ~ .(gsub("-", "−", sprintf("%-.1f", Z_THRESHOLD))) * ") per window of 50 lines, cumulative, Archaic corpus")
	)
ggsave("unexpected-window-50-cumul.archaic.png", p, width = 7.5, height = 3, dpi = 200)

print(data %>%
	group_by(work, book_n) %>%
	summarize(mean_unexpected_50 = mean(unexpected_50, na.rm = TRUE), era = first(era), .groups = "drop") %>%
	arrange(mean_unexpected_50)
, n = 500)
