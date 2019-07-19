library(tidyverse)
library(readxl)

FIRST_DATA_ROW <- 13
LETTER_TO_NUMERIC <- 1:length(letters)
names(LETTER_TO_NUMERIC) <- letters

data_dir = normalizePath('../data')
excel_file = file.path(data_dir, 'comprehensive_sorted_neuropsych.xlsx')
font_file = file.path(data_dir, 'neuroscore_3.0_font_properties.csv')
out_file = file.path(data_dir, 'clinical_neuroscore_v3d0_variables.tsv')

excel_data <- read_excel(excel_file, na = 'NA')

# we only want tp 1 or no timpeoint variable names to match redcap
# currently there are 975 of them
included <- excel_data %>%
  filter(tp == 1 | is.na(tp)) %>%
  mutate(redcap = str_replace(variable, '_[:digit:]+$', ''),
         column = as.numeric(LETTER_TO_NUMERIC[str_to_lower(column)])) %>%
  select(redcap, worksheet, row, column)

write_delim(included, out_file, delim = '\t')

# edit neuroscore_3.0_font_properties
font_properties <- read_delim(font_file, delim = '\t') %>%
  mutate(row = FIRST_DATA_ROW:(n() + FIRST_DATA_ROW - 1),
         is_bold = ifelse(is_bold == "#VALUE!", "-1", is_bold),
         is_bold = as.integer(is_bold),
         is_bold = ifelse(is_bold == -1, 1, is_bold)) %>%
  filter(!is.na(measure)) %>%
  mutate(bold_header = ifelse(is_bold, measure, NA_character_)) %>%
  tidyr::fill(bold_header) %>%
  mutate(indent_level = ifelse(str_detect(measure, '^ '), 
                               indent_level + 1, 
                               indent_level))

indent_header <- vector("character", nrow(font_properties))
indent_reference <- list()
for (i in 1:nrow(font_properties)) {
  variable <- font_properties$measure[i]
  cur_indent <- font_properties$indent_level[i]

  indent_reference[as.character(cur_indent)] <- variable
  if (cur_indent == 0)
    indent_header[i] <- variable
  else {
    indent_header[i] <- indent_reference[[as.character(cur_indent - 1)]]
  }
}
font_properties$indent_header <- indent_header

