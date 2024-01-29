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
	"ἀμ",
	"ἀμφ᾽",
	"ἀμφί",
	"ἀμφὶ",
	"ἀντί",
	"ἀντὶ",
	"ἀν᾽",
	"ἀνά",
	"ἀνὰ",
	"ἄνευ",
	"ἀπό",
	"ἀπὸ",
	"ἀπ᾽",
	"ἀφ᾽",
	"δί᾽",
	"διά",
	"διὰ",
	"εἰν",
	"εἰς",
	"ἐκ",
	"ἐν",
	"ἐνί",
	"ἐνὶ",
	"ἐξ",
	"ἐπ᾽",
	"ἐπί",
	"ἐπὶ",
	"ἐς",
	"ἐφ᾽",
	"κάγ",
	"κὰγ",
	"κάδ",
	"κὰδ",
	"κάθ᾽",
	"κάκ",
	"κὰκ",
	"κάπ",
	"κὰπ",
	"κάρ",
	"κὰρ",
	"κάτ",
	"κὰτ",
	"κατ᾽",
	"κατά",
	"κατὰ",
	"μά",
	"μὰ",
	"μήδ᾽",
	"μηδέ",
	"μηδὲ",
	"μηθ᾽",
	"μητ᾽",
	"μήτε",
	"οὐ",
	"οὐδέ",
	"οὐδὲ",
	"οὐθ᾽",
	"οὐκ",
	"οὐτ᾽",
	"οὔτε",
	"οὐχ",
	"αἰ",
	"ἀλλ᾽",
	"ἀλλά",
	"ἀλλὰ",
	"αὐτάρ",
	"αὐτὰρ",
	"εἰ",
	"ἐπεί",
	"ἐπεὶ",
	"ἐπήν",
	"ἐπὴν",
	"ἠ",
	"ἠδ᾽",
	"ἠδέ",
	"ἠδὲ",
	"ἠέ",
	"ἠὲ",
	"ἦε",
	"ἠθ᾽",
	"ἠμέν",
	"ἠμὲν",
	"ἤν",
	"ἠτ᾽",
	"ἰδ᾽",
	"ἰδέ",
	"ἰδὲ",
	"ἵν᾽",
	"ἵνα",
	"καί",
	"καὶ",
	"ὁθ᾽",
	"ὅθι",
	"ὅπερ",
	"ὁτ᾽",
	"ὅτε",
	"ὅτι",
	"ὅταν",
	"ὄφρ᾽",
	"ὄφρα",
	"τόφρ᾽",
	"τόφρα",
	"τῶ",
	"ὤ",
	"ὢ",
	"ὦ",
	"ὡς",
	"ὥς",
	"ὣς",
	"ὁ",
	"ἡ",
	"τό",
	"τὸ",
	"οἱ",
	"τοί",
	"τοὶ",
	"αἱ",
	"ταί",
	"ταὶ",
	"τά",
	"τὰ",
	"τώ",
	"τὼ",
	"τόν",
	"τὸν",
	"τήν",
	"τὴν",
	"τούς",
	"τοὺς",
	"τώς",
	"τὼς",
	"τάς",
	"τὰς",
	"τοῖο",
	"τοῦ",
	"τῆς",
	"τοῖιν",
	"τῶν",
	"τάων",
	"τῷ",
	"τῇ",
	"τοῖς",
	"τοῖσι",
	"τοῖσιν",
	"τῇς",
	"τῇσι",
	"τῇσιν",
	"ὅς",
	"ὃς",
	"ἥν",
	"ἣν",
	"ὥ",
	"ὣ",
	"ἅ",
	"ἃ",
	"οὕς",
	"οὓς",
	"ἅς",
	"ἃς",
	"οὗ",
	"ἧς",
	"ὧν",
	"ᾧ",
	"ᾗ",
	"οἷς",
	"οἷσι",
	"οἷσιν",
	"ᾗς",
	"ᾗσι",
	"ᾗσιν",
	"εὖ",
	"χὠ"

)

ALWAYS_POSTPOSITIVE_WORDS <- c(
	"ἄν",
	"ἂν",
	"ἄρ",
	"ἂρ",
	"ἄρ᾽",
	"ἄρα",
	"γε",
	"γάρ",
	"γὰρ",
	"δέ",
	"δὲ",
	"δή",
	"δὴ",
	"θην",
	"κε",
	"κεν",
	"μέν",
	"μὲν",
	"νυ",
	"νυν",
	"περ",
	"ῥα",
	"τε",
	"πῃ",
	"ποι",
	"ποθ᾽",
	"ποθε",
	"ποθεν",
	"ποθι",
	"ποτ᾽",
	"ποτε",
	"που",
	"πω",
	"πως",
	"με",
	"σε",
	"ἑ",
	"μιν",
	"ἥμιν",
	"ἦμιν",
	"ὕμιν",
	"ὗμιν",
	"μευ",
	"σεθεν",
	"σεο",
	"σευ",
	"τευ",
	"ἑθεν",
	"ἑο",
	"εὑ",
	"σφε",
	"σφας",
	"σφεας",
	"σφι",
	"σφιν",
	"σφω",
	"σφωε",
	"σφεων",
	"σφωιν",
	"σφωι",
	"μοι",
	"τοι",
	"σοι",
	"οἱ",
	"σφισι",
	"σφισιν",
	"τις",
	"τι",
	"τινες",
	"τιν᾽",
	"τινα",
	"τινας",
	"τεο",
	"τινος",
	"του",
	"τινων",
	"τινι",
	"τισι",
	"τισιν",
	"εἰμι",
	"εἰμ᾽",
	"ἐσσι",
	"ἐσθ᾽",
	"ἐστ᾽",
	"ἐστι",
	"ἐστιν",
	"εἰμεν",
	"ἐσμεν",
	"ἐστον",
	"ἐστε",
	"εἰσ᾽",
	"εἰσι",
	"εἰσιν",
	"ἐών",
	"ἐὼν",
	"φημ᾽",
	"φημι",
	"φησι",
	"φησιν",
	"φαμεν",
	"φατ᾽",
	"φατε",
	"φασ᾽",
	"φασι",
	"φασιν",
	"ἔνι",
	"εἵνεκα"

)

always_prepositive <- function(word) {
	word %in% stri_trans_nfd(ALWAYS_PREPOSITIVE_WORDS)
}

always_postpositive <- function(word) {
	word %in% stri_trans_nfd(ALWAYS_POSTPOSITIVE_WORDS)
}

# Load the manual list of appositive instances.
exceptional <- read_csv("exceptional-appositives.csv", na = c(""), col_types = cols(
	work = col_factor(),
	book_n = col_character(),
	line_n = col_character(),
	word_n = col_integer(),
	appositive = col_factor()
))

opts <- parse_args2(OptionParser())

data <- lapply(opts$args, read_csv, na = c(""), col_types = cols(
	work = col_factor(),
	book_n = col_character(),
	line_n = col_character(),
	word_n = col_integer()
)) |>
	bind_rows() |>
	mutate(metrical_shape = replace_na(metrical_shape, ""))

# Sanity check: every row in the list of hardcoded exceptional appositives
# actually matches something in the data (at least among the works present in
# the data).
unmatched <- anti_join(
	exceptional |> filter(work %in% unique(data$work)),
	data,
	by = c("work", "book_n", "line_n", "word_n", "word", "lemma")
)
if (nrow(unmatched) != 0) {
	print(unmatched)
	cat("Unmatched exceptional appositives.\n")
	stop()
}
# Sanity check: only expected appositive types in the hardcoded exceptional
# appositives.
weird <- filter(exceptional, !(appositive %in% c("no", "prepositive", "postpositive", "bidirectional")))
if (nrow(weird) != 0) {
	print(weird)
	cat("Unknown appositive notations.\n")
	stop()
}

data <- data |>
	group_by(work, book_n) |>
	mutate(unique_line_n = cumsum(
		replace_na(line_n, "") != replace_na(coalesce(lag(line_n), line_n), "") |
		word_n <= coalesce(lag(word_n), word_n))
	) |>
	ungroup() |>

	left_join(
		exceptional,
		by = c("work", "book_n", "line_n", "word_n", "word", "lemma")
	) |>
	mutate(
		is_prepositive = ifelse(!is.na(appositive), appositive %in% c("prepositive", "bidirectional"), always_prepositive(word)),
		is_postpositive = ifelse(!is.na(appositive), appositive %in% c("postpositive", "bidirectional"), always_postpositive(word)),
	) |>
	select(!appositive) |>
	group_by(work, book_n, unique_line_n) |>
	mutate(word_n = word_n
		# Merge each prepositive word with the next word by
		# decrementing the word_n of all the words that follow it in
		# the line.
		- cumsum(lag(is_prepositive, default = FALSE))
		# Merge each postpositive word with the previous word by
		# decrementing the word_n of the postpositive word (and that of
		# all words that follow it in the line). But if the previous
		# word is prepositive, the words are already going to be
		# joined, so for the moment pretend this word is not
		# postpositive.
		- cumsum(word_n > 1 & is_postpositive & !lag(is_prepositive, default = FALSE))
	) |>
	ungroup()

# Examine data here to debug appositive classifications.
# data

# Now synthesize new "words" (appositive groups) according to the word_n that
# have been made identical in a line in the previous step.
data <- data |>
	select(!c(is_prepositive, is_postpositive)) |>
	group_by(work, book_n, unique_line_n, word_n) |>
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
		unique_line_n,
		replace_na(str_extract(line_n, "[^\\d]*$"), ""),
		word_n
	) |>
	select(!unique_line_n) |>
	relocate(work, book_n, line_n, word_n)

write_csv(data, stdout(), na = "")
