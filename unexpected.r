library("tidyverse")
library("RcppRoll")

options(width = 10000)
options(crayon.enabled = FALSE) # Disable ANSI escapes for text output.

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
) %>%
group_by(work, book_n) %>%
mutate(unique_line_n = cumsum(
	replace_na(line_n, "") != replace_na(coalesce(lag(line_n), line_n), "") |
	word_n <= coalesce(lag(word_n), word_n))
) %>%
ungroup()

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

WINDOW_SIZE <- 181

cat("\n")

cat(sprintf("Unexpected shapes per window of %d words, archaic corpus\n", WINDOW_SIZE))

data_windows_left <- data %>%
	group_by(work, book_n) %>%
	mutate(unexpected_window = roll_sum(is_unexpected, WINDOW_SIZE, align = "left", fill = NA)) %>%
	ungroup()

archaic_data <- filter(data_windows_left, era == "archaic")
summary(archaic_data$unexpected_window)
x <- table(archaic_data$unexpected_window)
x
x / sum(x) * 100
cumsum(x) / sum(x) * 100
p <- ggplot(archaic_data) +
	geom_bar(aes(unexpected_window)) +
	scale_x_continuous(breaks = 0:10) +
	scale_y_continuous(minor_breaks = waiver()) +
	labs(
		x = "Number of unexpected shapes in window",
		y = "Number of distinct windows",
		title = bquote("Unexpected shapes (" * italic(z) ~ "≤" ~ .(gsub("-", "−", sprintf("%-.1f", Z_THRESHOLD))) * ") per window of" ~ .(WINDOW_SIZE) ~ "lines, Archaic corpus")
	)
ggsave(sprintf("unexpected-window-%d.archaic.png", WINDOW_SIZE), p, width = 7.5, height = 3, dpi = 200)
p <- ggplot(archaic_data) +
	stat_ecdf(aes(unexpected_window), geom = "bar") +
	scale_x_continuous(breaks = 0:10) +
	scale_y_continuous(n.breaks = 11, labels = scales::percent, minor_breaks = NULL) +
	labs(
		x = "Number of unexpected shapes in window",
		y = "Number of distinct windows",
		title = bquote("Unexpected shapes (" * italic(z) ~ "≤" ~ .(gsub("-", "−", sprintf("%-.1f", Z_THRESHOLD))) * ") per window of" ~ .(WINDOW_SIZE) ~ "lines, cumulative, Archaic corpus")
	)
ggsave(sprintf("unexpected-window-%d-cumul.archaic.png", WINDOW_SIZE), p, width = 7.5, height = 3, dpi = 200)

print(data_windows_left %>%
	group_by(work, book_n) %>%
	summarize(mean_unexpected_window = mean(unexpected_window, na.rm = TRUE), era = first(era), .groups = "drop") %>%
	arrange(mean_unexpected_window)
, n = 500)

for (g in list(
	list(
		work = "Hom.Hymn",
		book_n = 4,
		title = FALSE,
		window_size = 181
	),
	list(
		work = "Hom.Hymn",
		book_n = 2,
		title = TRUE,
		window_size = 74
	),
	list(
		work = "Hom.Hymn",
		book_n = 4,
		title = TRUE,
		window_size = 74
	),
	list(
		work = "Sh.",
		book_n = NA,
		title = TRUE,
		window_size = 74
	),
	list(
		work = "Od.",
		book_n = 18,
		title = TRUE,
		window_size = 74
	)
)) {
	plot_data <- filter(data, work == g$work, is.na(g$book_n) | book_n == g$book_n) %>%
		group_by(work, book_n) %>%
		mutate(unique_word_n = 1:n()) %>%
		mutate(unexpected_window = roll_sum(is_unexpected, g$window_size, align = "center", fill = NA)) %>%
		ungroup()
	unique_line_n <- function(line_n) {
		filter(plot_data, line_n == !!line_n)$unique_line_n %>% first()
	}
	p <- ggplot() +
		geom_polygon(data = with(filter(plot_data, !is.na(unexpected_window)), tibble(
			unique_word_n = c(min(unique_word_n), rbind(unique_word_n, unique_word_n + 1), max(unique_word_n) + 1),
			unexpected_window = c(0, rbind(unexpected_window, unexpected_window), 0),
		)), aes(
			x = unique_word_n,
			y = unexpected_window,
		), fill = "#606060") +
		geom_point(data = filter(plot_data, is_unexpected), aes(
			x = unique_word_n,
			y = -0.25,
		), shape = 2, alpha = 0.8, size = 0.2) +
		scale_x_continuous(
			limits = c(min(plot_data$unique_word_n), max(plot_data$unique_word_n)),
			breaks = (plot_data %>% filter(as.integer(line_n) %% 50 == 0 & replace_na(line_n != lag(line_n), TRUE)))$unique_word_n,
			labels = (plot_data %>% filter(as.integer(line_n) %% 50 == 0 & replace_na(line_n != lag(line_n), TRUE)))$line_n,
			minor_breaks = NULL,
			expand = expansion(mult = 0, add = 0),
		) +
		scale_y_continuous(
			limits = c(NA, 16),
			breaks = seq(0, 16, by = 4),
			minor_breaks = seq(0, 16, by = 1),
		) +
		labs(
			x = "Line Number",
			y = "Unexpected Shapes\nPer Window",
			title = if (g$title)
				sprintf("%s%s, window size %d",
					g$work,
					if (is.na(g$book_n)) "" else sprintf(" %d", g$book_n),
					g$window_size
				)
			else
				NULL,
		) +
		theme_minimal(
			# https://github.com/impallari/Libre-Baskerville/raw/2fba7c8e0a8f53f86efd3d81bc4c63674b0c613f/LibreBaskerville-Regular.ttf
			# Copy LibreBaskerville-Regular.ttf to $HOME/.fonts
			# fc-cache
			base_family = "Libre Baskerville",
			base_size = 8,
		) +
		theme (
			axis.title.y = element_text(size = 7),
		)
	ggsave(sprintf("%s%s-windows-%d.png",
		g$work,
		if (is.na(g$book_n)) "" else sprintf(".%d", g$book_n),
		g$window_size
	), p, width = 6.0 - 2 * 0.88, height = 1.25, dpi = 600, bg = "white")
}
