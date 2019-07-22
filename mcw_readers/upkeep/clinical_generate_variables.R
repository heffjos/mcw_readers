library(tidyverse)
library(readxl)

FIRST_DATA_ROW <- 13
LETTER_TO_NUMERIC <- 1:length(letters)
names(LETTER_TO_NUMERIC) <- letters

data_dir = normalizePath('../data')
excel_file = file.path(data_dir, 'comprehensive_sorted_neuropsych.xlsx')
font_file = file.path(data_dir, 'neuroscore_3.0_font_properties.csv')
out_file = file.path(data_dir, 'clinical_neuroscore_v3d0_variables.tsv')

excel_data <- read_excel(excel_file)

included <- excel_data %>%
  filter(tp == 1 | is.na(tp)) %>%
  mutate(redcap = str_replace(variable, '_[:digit:]+$', ''),
         column = as.numeric(LETTER_TO_NUMERIC[str_to_lower(column)]))
