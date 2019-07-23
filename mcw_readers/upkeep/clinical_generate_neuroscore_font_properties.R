library(tidyverse)
library(readxl)

in_file <- "../data/all_versions_font_properties.xlsm"
data <- read_excel(in_file, trim_ws = FALSE)

processed_data <- data %>%
  fill(version) %>%
  mutate(indent_level = ifelse(str_detect(measure, "^ "), indent_level + 1, indent_level),
         is_bold = ifelse(is_bold == -1 | is.na(is_bold), 1, 0)) %>%
  group_by(version) %>%
  mutate(line = seq(first(line), n() + first(line) - 1)) %>%
  ungroup() %>%
  filter(!is.na(measure))

