library(tidyverse)

data <- read_delim("../data/clinical_spss_variables.tsv", delim = "\t") %>%
  mutate(order = 1:length(variable),
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
  write_delim("../data/clinical_unique_spss_variables.tsv", delim = "\t") 
  

