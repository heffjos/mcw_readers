library(tidyverse)
library(readxl)

LETTER_TO_NUMERIC <- 1:length(letters)
names(LETTER_TO_NUMERIC) <- letters

data_dir = normalizePath('../data')
assigned_file = file.path(data_dir, 'clinical_v3.0ulatest_labeled.xlsx')
font_file <- file.path(data_dir, 'clinical_versions_font_properties.xlsm')

out_version_key <- file.path(data_dir, 'clinical_version_key.tsv')
out_templates_labeled <- file.path(data_dir, 'clinical_templates_labeled.tsv')
out_redcap_variables <- file.path(data_dir, 'clinical_redcap_variables.tsv')
out_redcap_labeled <- file.path(data_dir, 'clinical_redcap_labeled.tsv')

assigned_data <- read_excel(assigned_file, na = "NA")
font_data <- read_excel(font_file, trim_ws = FALSE)

# clinical_v3.0ulatest_labeled.xlsx has been consolidated to only have unique
# variables, so we do not have to do any filtering any timepoints here, also
# all unique variables have been converted to lower case
redcap_data <- assigned_data %>%
  mutate(column = as.numeric(LETTER_TO_NUMERIC[str_to_lower(column)])) %>%
  select(redcap = base, worksheet, row, column)

redcap_data %>% 
  select(redcap)  %>%
  mutate(values = NA) %>%
  write_delim(out_redcap_variables, delim = '\t')

# work on font properties now
processed_data <- font_data %>%
  fill(version) %>%
  mutate(indent_level = ifelse(str_detect(measure, "^ "), indent_level + 1, indent_level),
         measure = str_trim(measure),
         is_bold = ifelse(is_bold == -1 | is.na(is_bold), 1, 0), 
         worksheet = "Template") %>%
  group_by(version) %>%
  mutate(row = seq(first(row), n() + first(row) - 1),
         bold_header = ifelse(is_bold, measure, NA)) %>%
  fill(bold_header) %>%
  ungroup() %>%
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
v3d0ulatest <- filter(processed_data, version == "3.0ulatest")

# now let's create out_templates_labeled for primarily reference and sanity checks
reference_3.0ulatest <- v3d0ulatest %>% 
  left_join(redcap_data, by = c("row", "worksheet")) %>%
  select(measure, bold_header, indent_header, worksheet, redcap, column)

redcap_processed_data <- processed_data %>%
  select(measure, row, version, bold_header, indent_header, worksheet) %>%
  left_join(reference_3.0ulatest, by = c("measure", "bold_header", "indent_header", "worksheet"))

write_delim(redcap_processed_data, out_templates_labeled, delim = "\t")

# create a version key
version_key <- redcap_processed_data %>%
  select(measure, version, row, column) %>%
  filter(row %in% c(12, 13, 622, 632, 709, 726, 736, 739, 811)) %>%
  complete(row, version) %>%
  arrange(version) %>%
  select(measure, version, row, column) %>%
  mutate(column = 2)

write_delim(version_key, out_version_key, delim = "\t")

# now create out_redcap_labeled which is the file used for actual reading
redcap_data_labeled <- redcap_data %>%
  left_join(v3d0ulatest, by = c("row", "worksheet")) %>%
  select(-version, -indent_level, -is_bold, -row) %>%
  left_join(processed_data %>% select(-indent_level, -is_bold), 
            by = c("worksheet", "measure", "bold_header", "indent_header"))
write_delim(redcap_data_labeled, out_redcap_labeled, delim = "\t")



  
