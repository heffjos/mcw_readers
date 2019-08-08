library(tidyverse)

local_variables <- read_delim("../data/clinical_unique_spss_variables.tsv", delim = "\t")
db_variables <- read_csv("./data/clinical_data_columns.csv") %>%                                                 
  select(variable = `Variable / Field Name`) 

local_extra <- local_variables %>%
  anti_join(db_variables, by = c("base" = "variable")) %>%
  select(-tp, -type) %>%
  write_csv("local_extra.csv")

db_extra <- db_variables %>%
  anti_join(local_variables %>% select(-variable), by = c("variable" = "base")) %>%
  write_delim("db_extra.csv")
