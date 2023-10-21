---
title: Melting an R DataFrame
description: Writing a function to convert a data frame from wide to tall.
pubDate: 2023-10-21
---

I've recently been making more of an effort to display information graphically, rather than just relying on tables of numbers. As part of that, I've been using [`ggplot2`](https://ggplot2.tidyverse.org/index.html) to display all kinds of information. However, I've run into a common issue: `ggplot` expects a data frame to be 'melted', while I usually prefer that the data are generated in a 'wide' format. Here's an example of what I mean:

```r
# how I usually generate or load data - a 'wide' dataframe
wide_df <- data.frame(
    age=c(18, 25, 45),
    height_measured=c(170, 182, 175),
    height_predicted=c(176, 175, 177)
)
wide_df
```

<table class="dataframe">
<caption>A data.frame: 3 × 3</caption>
<thead>
	<tr><th scope=col>age</th><th scope=col>height_measured</th><th scope=col>height_predicted</th></tr>
	<tr><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>18</td><td>170</td><td>176</td></tr>
	<tr><td>25</td><td>182</td><td>175</td></tr>
	<tr><td>45</td><td>175</td><td>177</td></tr>
</tbody>
</table>

```r
# how ggplot expects the data
tall_df <- data.frame(
    age=c(17, 25, 45, 18, 25, 45),
    height=c(169, 182, 175, 176, 175, 177),
    height_type=c("Measured", "Measured", "Measured", "Predicted", "Predicted", "Predicted")
)
tall_df
```

<table class="dataframe">
<caption>A data.frame: 6 × 3</caption>
<thead>
	<tr><th scope=col>age</th><th scope=col>height</th><th scope=col>height_type</th></tr>
	<tr><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;chr&gt;</th></tr>
</thead>
<tbody>
	<tr><td>17</td><td>169</td><td>Measured </td></tr>
	<tr><td>25</td><td>182</td><td>Measured </td></tr>
	<tr><td>45</td><td>175</td><td>Measured </td></tr>
	<tr><td>18</td><td>176</td><td>Predicted</td></tr>
	<tr><td>25</td><td>175</td><td>Predicted</td></tr>
	<tr><td>45</td><td>177</td><td>Predicted</td></tr>
</tbody>
</table>

Eventually, I'd like to write a function to automate the process of 'melting' a dataframe. However, let's first do it manually. The basic idea is that we will take the 'independent variable' column (`age`) and replicated it for each of the columns that we need to melt. We'll also need to provide a new column, in this case `height_type` and associate a new label with each of the replicated columns.

```r
new_age_column <- rep(wide_df$age, 2)
new_height_column <- c(wide_df$height_measured, wide_df$height_predicted)
new_labels_column <- c(rep("Measured", 3), rep("Predicted", 3))
generated_tall_df <- data.frame(
    age=new_age_column,
    height=new_height_column,
    height_type=new_labels_column
)
generated_tall_df
```

<table class="dataframe">
<caption>A data.frame: 6 × 3</caption>
<thead>
	<tr><th scope=col>age</th><th scope=col>height</th><th scope=col>height_type</th></tr>
	<tr><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;chr&gt;</th></tr>
</thead>
<tbody>
	<tr><td>18</td><td>170</td><td>Measured </td></tr>
	<tr><td>25</td><td>182</td><td>Measured </td></tr>
	<tr><td>45</td><td>175</td><td>Measured </td></tr>
	<tr><td>18</td><td>176</td><td>Predicted</td></tr>
	<tr><td>25</td><td>175</td><td>Predicted</td></tr>
	<tr><td>45</td><td>177</td><td>Predicted</td></tr>
</tbody>
</table>

Doing it manually isn't too bad; we know the names of all the relevant columns and where the data needs to go, so we can easily just transform the data. However, since this is something I do a lot, I would rather have a reusable function that I can just call! So, what does this function need? In the code above, here's what we needed:

-   the 'wide' data frame (in this case, `wide_df`).
-   the name of the 'independent variable' column (`age`)
-   a name for the 'dependent variable' column (`height`)
-   a name for the 'label' column (`height_type`)
-   a vector of columns to be melted (`height_measured`, `height_predicted`)
-   a vector of labels for each of the columns (`Measured`, `Predicted`).

Knowing the arguments, let's write the function!

```r
melt <- function(df, independent_column_name, dependent_column_name, label_column_name, column_names_to_melt, labels) {
    # repeat the independent column once for each column we'll melt
    new_independent_column <- rep(df[[independent_column_name]], length(column_names_to_melt))

    # iteratively build the new dependent column by concatenating all of the ones to melt
    new_dependent_column <- c()
    for (column_name in column_names_to_melt) {
        new_dependent_column <- c(new_dependent_column, df[[column_name]])
    }

    # now iteratively build the labels
    new_labels_column <- c()
    for (label in labels) {
        new_labels_column <- c(new_labels_column, rep(label, length(df[[independent_column_name]])))
    }

    # now build the data frame
    tall_df <- data.frame(
        new_independent_column,
        new_dependent_column,
        new_labels_column
    )

    # this has the correct shape, but the wrong column names - let's fix that
    new_column_names <- c(independent_column_name, dependent_column_name, label_column_name)
    names(tall_df) <- new_column_names
    return(tall_df)
}
```

And now to test the function:

```r
test_tall_df <- melt(wide_df, 'age', 'height', 'height_type', c('height_measured', 'height_predicted'), c('Measured', 'Predicted'))
test_tall_df
```

<table class="dataframe">
<caption>A data.frame: 6 × 3</caption>
<thead>
	<tr><th scope=col>age</th><th scope=col>height</th><th scope=col>height_type</th></tr>
	<tr><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;chr&gt;</th></tr>
</thead>
<tbody>
	<tr><td>18</td><td>170</td><td>Measured </td></tr>
	<tr><td>25</td><td>182</td><td>Measured </td></tr>
	<tr><td>45</td><td>175</td><td>Measured </td></tr>
	<tr><td>18</td><td>176</td><td>Predicted</td></tr>
	<tr><td>25</td><td>175</td><td>Predicted</td></tr>
	<tr><td>45</td><td>177</td><td>Predicted</td></tr>
</tbody>
</table>

So that seems to be working just fine. However, there is one glaring error: what about other columns? In our case the original data frame had only the data that we were melting. However, what if there were other columns with additional data? Let's see what I mean by that

```r

wide_df_with_additional_data <- data.frame(
    age=c(18, 25, 45),
    height_measured=c(170, 182, 175),
    height_predicted=c(176, 175, 177),
    nationality=c("Canada", "Switzerland", "Germany"),
    hair_colour=c("Red", "Brown", "Blue")
)
tall_df <- melt(wide_df_with_additional_data, 'age', 'height', 'height_type', c('height_measured', 'height_predicted'), c('Measured', 'Predicted'))
print(wide_df_with_additional_data)
print(tall_df)
```

      age height_measured height_predicted nationality hair_colour
    1  18             170              176      Canada         Red
    2  25             182              175 Switzerland       Brown
    3  45             175              177     Germany        Blue
      age height height_type
    1  18    170    Measured
    2  25    182    Measured
    3  45    175    Measured
    4  18    176   Predicted
    5  25    175   Predicted
    6  45    177   Predicted

The `nationality` and `hair_colour` columns are missing! In our function, we totally neglect any columns except the ones we explicitly melt. To fix this, we'll need to find all of the names of the other columns and replicate each of those in much the same way as we did the independent variable column (`age`).

```r
melt <- function(df, independent_column_name, dependent_column_name, label_column_name, column_names_to_melt, labels) {
    num_repetitions <- length(column_names_to_melt)

    # repeat the independent column once for each column we'll melt
    new_independent_column <- rep(df[[independent_column_name]], num_repetitions)

    # iteratively build the new dependent column by concatenating all of the ones to melt
    new_dependent_column <- c()
    for (column_name in column_names_to_melt) {
        new_dependent_column <- c(new_dependent_column, df[[column_name]])
    }

    # now iteratively build the labels
    new_labels_column <- c()
    for (label in labels) {
        new_labels_column <- c(new_labels_column, rep(label, length(df[[independent_column_name]])))
    }

    # rescue the other columns
    # first exclude the columns we'll deal with later
    rescued_df <- df[, !(names(df) %in% c(independent_column_name, column_names_to_melt))]
    # now we need to replicate the data frame vertically
    rescued_df <- rescued_df[rep(seq_len(nrow(rescued_df)), num_repetitions), ]
    # reset the row names
    rownames(rescued_df) <- NULL

    # now build the data frame
    tall_df <- data.frame(
        new_independent_column,
        new_dependent_column,
        new_labels_column
    )

    # join this to the colum of rescued data by binding the columns
    tall_df <- cbind(tall_df, rescued_df)

    # this has the correct shape, but the wrong column names - let's fix that. Note that we need to add the rescued column names back in as well
    new_column_names <- c(independent_column_name, dependent_column_name, label_column_name, c(names(rescued_df)))
    names(tall_df) <- new_column_names
    return(tall_df)
}

tall_df <- melt(wide_df_with_additional_data, 'age', 'height', 'height_type', c('height_measured', 'height_predicted'), c('Measured', 'Predicted'))
cat('original dataframe\n')
print(wide_df_with_additional_data)
cat('\ntall version\n')
print(tall_df)
```

    original dataframe
      age height_measured height_predicted nationality hair_colour
    1  18             170              176      Canada         Red
    2  25             182              175 Switzerland       Brown
    3  45             175              177     Germany        Blue

    tall version
      age height height_type nationality hair_colour
    1  18    170    Measured      Canada         Red
    2  25    182    Measured Switzerland       Brown
    3  45    175    Measured     Germany        Blue
    4  18    176   Predicted      Canada         Red
    5  25    175   Predicted Switzerland       Brown
    6  45    177   Predicted     Germany        Blue

And there we have it! A function to 'melt' data frames into the shape we want. Now, this code could certainly be improved; however, it gets the job done, and now that the function is written, I can can continue to improve on it from there.
