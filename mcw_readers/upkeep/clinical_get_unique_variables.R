library(tidyverse)

name_mapper = c(
  "filter_$" = "filter_anc",

  # neuropsych_tests
  "cognitive_change" = "cognitive_change_1",
  "depression_label" = "depression_label_1",
  "depression_label3" = "depression_label_3",
  "HVLT_MemProfile" = "hvlt_memprofile_1",
  "HVLTMemProfile2" = "hvlt_memprofile_2",
  "HVLTMemProfile2_MixedExplained" = "hvlt_memprofile_mixedexplained_2",
  "HVLT_MemProfile_MixedExplained" = "hvlt_memprofile_mixedexplained_1",
  "letfluency_ver" = "letterfluency_ver_1",
  "trails_ver" = "trails_ver_1",
  "wcst_ver" = "wcst_ver_1")


name_delete = c(
  "date")

data <- read_delim("../data/clinical_spss_variables.tsv", delim = "\t")
  
data <- data %>% 
  mutate(variable = recode (variable, !!!name_mapper),
         order = 1:length(variable),
         tp = str_match(variable, "_([:digit:]|[bB][lL])$")[, 2],
         tp = str_to_lower(tp),
         type = case_when(
            str_detect(variable, "_raw_") ~ "raw",
            str_detect(variable, "_ss_") ~ "ss",
            str_detect(variable, "_perc_") ~ "perc",
            TRUE ~ "other"),
         base = str_remove(variable, "_([:digit:]|[bB][lL])$"),
         base = str_to_lower(base),
         tp_fct = fct_lump(tp, 4),
         tp_fct = fct_relevel(tp_fct, "bl", "1", "2", "3", "Other")) %>%
  arrange(tp_fct) %>%
  distinct(base, .keep_all = TRUE) %>%
  select(-tp_fct) %>%
  arrange(order) %>%
  filter(!base %in% name_delete)

write_delim(data, "../data/clinical_unique_spss_variables.tsv", delim = "\t") 
  
