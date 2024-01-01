library("tidyverse")

Z_THRESHOLD <- -2.0

data <- read_csv("joined.sedes-metrical_shape.csv", col_types = cols(
	work = col_character(),
	book_n = col_character(),
	line_n = col_character(),
	x = col_double(),
	z = col_double(),
)) %>% mutate(
	is_unexpected = z <= Z_THRESHOLD,
)

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
print(iliad %>% group_by(book_n) %>% summarize(num_words = n(), num_unexpected = sum(is_unexpected, na.rm = TRUE), pct_unexpected = num_unexpected / num_words * 100) %>% arrange(pct_unexpected), n = 100)

cat("\n")

cat("Longer poems\n")

print(data %>% group_by(work, book_n) %>% summarize(num_words = n(), num_unexpected = sum(is_unexpected, na.rm = TRUE), pct_unexpected = num_unexpected / num_words * 100) %>% filter(num_words > 1000) %>% arrange(pct_unexpected), n = 500)
