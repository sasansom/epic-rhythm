# Usage:
#   Rscript merge-appositive.r INPUT.CSV...
#
# Merges words with adjacent appositives in CSV files as output by SEDES
# tei2csv. The `word` and `lemma` columns in merged rows are joined by spaces.
# The `metrical_shape` columns are concatenated.

library("stringi")
library("tidyverse")
library("optparse")

ALWAYS_PREPOSITIVE_WORDS <- c(
	"ἐν"
)

ALWAYS_POSTPOSITIVE_WORDS <- c(

)

is_prepositive <- function(word) {
	word %in% stri_trans_nfd(ALWAYS_PREPOSITIVE_WORDS)
}

is_postpositive <- function(word) {
	word %in% stri_trans_nfd(ALWAYS_POSTPOSITIVE_WORDS)
}

opts <- parse_args2(OptionParser())

data <- lapply(opts$args, read_csv, na = c(""), col_types = cols(
	work = col_factor(),
	book_n = col_character(),
	line_n = col_character(),
	word_n = col_integer()
)) |>
	bind_rows() |>
	mutate(metrical_shape = replace_na(metrical_shape, ""))

data <- data |>
	mutate(
		is_prepositive = is_prepositive(word),
		is_postpositive = is_postpositive(word),
	) |>
	group_by(work, book_n, line_n) |>
	mutate(word_n = word_n
		# Merge postpositive with the previous word by decrementing its
		# word_n (and that of all words in the line that follow).
		- cumsum(is_postpositive)
		# Merge prepositive with the following word by decrementing the
		# word_n of the words that follow it in the line.
		- cumsum(lag(is_prepositive, default = FALSE))
	) |>
	ungroup()

# Examine data here to debug appositive classifications.
# data

# Now synthesize new "words" (appositive groups) according to the word_n that
# have been made identical in a line in the previous step.
data <- data |>
	select(!c(is_prepositive, is_postpositive)) |>
	group_by(work, book_n, line_n, word_n) |>
	summarize(
		word = paste0(word, collapse = " "),
		lemma = paste0(lemma, collapse = " "),
		sedes = first(sedes),
		metrical_shape = paste0(metrical_shape, collapse = ""),
		across(everything(), first),
		.groups = "drop"
	) |>
	# Sort in a sensible order.
	arrange(
		work,
		# Deal with numeric and non-numeric book names.
		replace_na(as.integer(str_extract(book_n, "^\\d+")), 0),
		replace_na(str_extract(book_n, "[^\\d]*$"), ""),
		# Deal with line numbers that may have a non-numeric suffix.
		replace_na(as.integer(str_extract(line_n, "^\\d+")), 0),
		replace_na(str_extract(line_n, "[^\\d]*$"), ""),
		word_n
	)

write_csv(data, stdout())
