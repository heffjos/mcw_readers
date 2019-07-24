library(tidyverse)
library(readxl)

LETTER_TO_NUMERIC <- 1:length(letters)
names(LETTER_TO_NUMERIC) <- letters

data_dir = normalizePath('../data')
assigned_file = file.path(data_dir, 'comprehensive_sorted_neuropsych.xlsx')
font_file <- file.path(data_dir, 'all_versions_font_properties.xlsm')
out_file = file.path(data_dir, 'clinical_neuroscore_v3d0_variables.tsv')

assigned_data <- read_excel(assigned_file, na = "NA")
font_data <- read_excel(font_file, trim_ws = FALSE)

# we only want tp 1 or no timpeoint variable names to match redcap
# currently there are 975 of them
included <- assigned_data %>%
  filter(tp == 1 | is.na(tp)) %>%
  mutate(redcap = str_replace(variable, '_[:digit:]+$', ''),
         column = as.numeric(LETTER_TO_NUMERIC[str_to_lower(column)])) %>%
  select(redcap, worksheet, row, column)

out_file = file.path(data_dir, 'clinical_neuroscore_v3d0_variables.tsv')

# work on font properties now
processed_data <- font_data %>%
  fill(version) %>%
  mutate(indent_level = ifelse(str_detect(measure, "^ "), indent_level + 1, indent_level),
         measure = str_trim(measure),
         is_bold = ifelse(is_bold == -1 | is.na(is_bold), 1, 0)) %>%
  group_by(version) %>%
  mutate(line = seq(first(line), n() + first(line) - 1),
         bold_header = ifelse(is_bold, measure, NA)) %>%
  fill(bold_header) %>%
  ungroup() %>%
  rename(row = "line") %>%
  filter(!is.na(measure))

# u10.21.16 == u11.01.16  for template sheet
# u1.30 == u2.3 for template sheet except some measure names. u2.3 has a couple different
# names, so use 1.30, because it is consistent with all other versions.

indent_header <- vector("character", nrow(processed_data))
indent_reference <- list()
for (i in 1:nrow(processed_data)) {
  variable <- processed_data$measure[i]
  cur_indent <- processed_data$indent_level[i]

  indent_reference[as.character(cur_indent)] <- variable
  if (cur_indent == 0)
    indent_header[i] <- variable
  else {
    indent_header[i] <- indent_reference[[as.character(cur_indent - 1)]]
  }
}
processed_data$indent_header <- indent_header

# now let's consolidate included and processed_data
reference_v3.0 <- processed_data %>% 
  filter(version == "3.0") %>%
  left_join(included, by = "row")
  
