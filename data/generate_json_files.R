setwd("~/Dropbox/Dissertation/Coder Quality/experiment/mturk_coder_quality/data/")
library(RJSONIO)

### For this experiment we will be sampling a number of Economic and Neither
### sentences equal to the total number of Social questions that are
### available to us. Position specific sentence data files are
### generated using the `generate_coding_data.R` file.

# Setting the seed because we need to sample from both the 
# Neither and Economic data sets, and want to have path dependence
# in sample for replication purposes.
seed <- 19820805 # That's my birthday, y'all!
set.seed(seed)

sentence_data_sets <- c("none","econ", "soc")

sentence_data <- lapply(sentence_data_sets, function(n) { 
	read.csv(file.path("csv", paste(n, "csv", sep=".")), 
		stringsAsFactors=FALSE, na.string="NA")
})
names(sentence_data) <- sentence_data_sets

# Sample data

sampleData <- function(df, k) {
  return(df[sample(1:nrow(df), k),])
}

sample.size <- nrow(sentence_data[["soc"]])
sentence_data[["econ_sample"]] <- sampleData(sentence_data[["econ"]], sample.size)
sentence_data[["none_sample"]] <- sampleData(sentence_data[["none"]], sample.size)

# Collapse the Social and sampled data into a single data frame, which will
# constitute the data used from the experiment.

experimental_data <- rbind(sentence_data[["none_sample"]],
                           sentence_data[["econ_sample"]],
                           sentence_data[["soc"]])

# Need to sample from each of these data sets an equal number of training
# sentences, which will be dropped from the sentences to be coded

training_sequence <- c(6,12)
tol_sequence <- c(.67,.84)
training_data <- list()

for(i in 1:length(training_sequence)) {
  for(j in 1:length(tol_sequence)) {
    sample_rows <- sample(1:nrow(experimental_data), training_sequence[i])
    training_data[[paste(training_sequence[i]+tol_sequence[j])]] <- experimental_data[sample_rows,]
  }
}

# Combine Social and sampled data into single data frame, which will
# constitute data set for experiments

# Generate JSON
generateJSON <- function(df) {
  df_list <- lapply(1:nrow(df), function(i) {
    di <- df[i,]
    di$pre_sentence <- paste(di$pre_text_2, di$pre_text_1, sep=" ")
    di$post_sentence <- paste(di$post_text_1, di$post_text_2, sep=" ")
    di <- di[,!(names(df) %in% c("pre_text_2", "pre_text_1", "post_text_1", "post_text_2"))]
    return(di)
  })
  return(toJSON(df_list, .na='""'))
}

training_json <- lapply(training_data, generateJSON)
experimental_json <- generateJSON(experimental_data)
drop_cols <- c("policy_area_gold", "econ_scale_gold", "soc_scale_gold")
experimental_no_ans <- generateJSON(
  experimental_data[,!(names(experimental_data) %in% drop_cols)])

for(i in names(training_json)) {
  f <- file.path("json", "training", paste(gsub(".","_",i,fixed=TRUE), "json", sep="."))
  con <- file(f, "w")
  cat(training_json[[i]], file=con)
  close(con)
}

f <- file.path("json", "experimental.json")
con <- file(f, "w")
cat(experimental_json, file=con)
close(con)

f <- file.path("json", "experimental_no_ans.json")
con <- file(f, "w")
cat(experimental_no_ans, file=con)
close(con)


