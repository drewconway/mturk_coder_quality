setwd("~/Dropbox/Dissertation/Coder Quality/experiment/mturk_coder_quality/data/")
library(foreign)

### First, generate separate data frames for each kind of policy area and
# scale combination that will be used as part of the experiments

# Load sentence data
data_path <- "~/Dropbox/CMP_recoding/analysis/data_created/"
sentences <- read.dta(file.path(data_path, "sentence_level_data.dta"))

sentences <- subset(sentences, year == "1987" | year == "1997")

# List to hold all subsets
data_subsets <- list()

# Create separate data frames for all scale type-by-scale types
min_scale <- 0.5

# Policy position
data_subsets[["econ"]]  <- subset(sentences, gold_position == "Economic")
data_subsets[["soc"]]  <- subset(sentences, gold_position == "Social")
data_subsets[["none"]]  <- subset(sentences, gold_position == "Neither")

# Economic scales
data_subsets[["econ_left"]] <- subset(sentences, propEconLeft > min_scale
                                      & gold_position == "Economic")
data_subsets[["econ_mid"]] <- subset(sentences, propEconMiddle > min_scale
                                     & gold_position == "Economic")
data_subsets[["econ_right"]] <- subset(sentences, propEconRight > min_scale
                                       & gold_position == "Economic")

# Social scales
data_subsets[["soc_left"]] <- subset(sentences, propSocLeft > min_scale
                                     & gold_position == "Social")
data_subsets[["soc_mid"]] <- subset(sentences, propSocMiddle > min_scale
                                    & gold_position == "Social")
data_subsets[["soc_right"]] <- subset(sentences, propSocRight > min_scale
                                      & gold_position == "Social")

### Format the data sets so they can be used in training mode.

# Need to add the two sentence context sentence context 

generateContextDF <- function(df, char_min) {
  # Return a version of the subset data set with clean two-sentence
  # context.
  pre_text_2 <- match(df$sentenceid - 20, sentences$sentenceid)
  pre_text_1 <- match(df$sentenceid - 10, sentences$sentenceid)
  post_text_1 <- match(df$sentenceid + 10, sentences$sentenceid)
  post_text_2 <- match(df$sentenceid + 20, sentences$sentenceid)
  context_df <- data.frame(list(text_unit_id = df$sentenceid,
                                sentence_text = df$sentence_text,
                                pre_text_2 = sentences$sentence_text[pre_text_2],
                                pre_text_1 = sentences$sentence_text[pre_text_1],
                                post_text_1 = sentences$sentence_text[post_text_1],
                                post_text_2 = sentences$sentence_text[post_text_2]),
                           stringsAsFactors=FALSE)
  
  clean_context <- subset(context_df, !is.na(pre_text_2) & !is.na(pre_text_1) &
                                      !is.na(post_text_1) & !is.na(post_text_2))
  # Remove sentence fragments
  clean_context <- clean_context[nchar(clean_context$pre_text_2, allowNA=TRUE) > char_min,]
  clean_context <- clean_context[nchar(clean_context$pre_text_1, allowNA=TRUE) > char_min,]
  clean_context <- clean_context[nchar(clean_context$post_text_1, allowNA=TRUE) > char_min,]
  clean_context <- clean_context[nchar(clean_context$post_text_2, allowNA=TRUE) > char_min,]
  
  return(clean_context)
}

# Create a new list of clean context data sets
data_context <- lapply(names(data_subsets), function(n) { 
  return(generateContextDF(data_subsets[[n]], 3))
})

names(data_context) <- names(data_subsets)

addScales <- function(df, area, econ_scale, soc_scale) {
  df$policy_area_gold <- area
  df$econ_scale_gold <- econ_scale
  df$soc_scale_gold <- soc_scale
  return(df)
}

# Add in the policy area and scale data
data_context[["none"]] <- addScales(data_context[["none"]], 1, NA, NA)
data_context[["econ"]] <- addScales(data_context[["econ"]], 2, NA, NA)
data_context[["soc"]] <- addScales(data_context[["soc"]], 3, NA, NA)
data_context[["econ_left"]] <- addScales(data_context[["econ_left"]], 2, -1, NA)
data_context[["econ_mid"]] <- addScales(data_context[["econ_middle"]], 2, 0, NA)
data_context[["econ_right"]] <- addScales(data_context[["econ_left"]], 2, 1, NA)
data_context[["soc_left"]] <- addScales(data_context[["soc_left"]], 3, NA, -1)
data_context[["soc_mid"]] <- addScales(data_context[["soc_middle"]], 3, NA, 0)
data_context[["soc_right"]] <- addScales(data_context[["soc_right"]], 3, NA, 1)

### Output all the data as individual CSVs
for(n in names(data_context)) {
  write.csv(data_context[[n]], file.path("csv", paste(n, "csv", sep=".")), 
            row.names=FALSE)
}