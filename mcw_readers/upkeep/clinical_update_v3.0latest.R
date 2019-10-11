library(tidyverse)
library(readxl)

clinical_unique_spss_variables <- read_delim("../data/clinical_unique_spss_variables.tsv", delim = "\t")
clinical_v3.0ulatest_labeled <- read_excel("../data/clinical_v3.0ulatest_labeled.xlsx", na = c("", "NA")) %>%
  select(base, definition, worksheet, row, column)

new_latest <- clinical_unique_spss_variables %>%
  left_join(clinical_v3.0ulatest_labeled, by = "base") %>%
  arrange(row, desc(tp), order)

write_tsv(new_latest, "./data/new_latest.tsv")
