---
title: Creating an R DataFrame the Bad Way
description: A bad but sometimes 'good enough' way of iteratively creating a dataframe.
pubDate: 2023-10-14
---

One of the pieces of advice you'll commonly see when learning about R and dataframes is that you should always, always parallelize your operations. That is: if you're creating a dataframe row-by-row or column-by-column, you're doing it wrong.

This could certainly be correct. However, I am fairly new to R, and sometimes I just don't know how I can go about parallelizing the operation that I'm currently working on. In other cases, I am reasonably sure that there isn't a great way to parallelize the operations in the first place, as other considerations (code structure, &c.) take precedence. I'm also a fan of the idea that when you're building something, get it working _first_, then optimize.

For all these reasons, in this post I'm going to share how you can create a dataframe row-by-row, in a way that is not very efficient but may be useful in some situations.

## Creating the DataFrame

Let's start with a contrived example. Imagine that I have a particle experiencing 1-D Brownian motion; that is, its position at every time step will be based on the previous one, plus some random factor. I want to store the time and position of the particle in a dataframe, potentially for graphing. Before we get started, I want to acknowledge that you could easily optimize this code; the purpose is to demonstrate the method of creating the dataframe.

The basic idea is to create an 'empty' dataframe with the correct columns and types, and then each time through the loop use the `rbind` function to append the new data to the end of the existing data.

```r
# creating the empty dataframe, ensuring that we have the correct types for the columns
existing_data <- data.frame(time=double(), position=double())
position = 0
for (i in 1:10) {
    position <- position + runif(1, -1, 1)
    # creating a new dataframe with the same shape as the empty one
    new_data <- data.frame(time=i, position=position)
    # 'appending' the new data to the old
    existing_data <- rbind(existing_data, new_data)
}
existing_data
```

<table class="dataframe">
<caption>A data.frame: 10 × 2</caption>
<thead>
	<tr><th scope=col>time</th><th scope=col>position</th></tr>
	<tr><th scope=col>&lt;int&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td> 1</td><td>0.85349725</td></tr>
	<tr><td> 2</td><td>1.18046767</td></tr>
	<tr><td> 3</td><td>0.70371025</td></tr>
	<tr><td> 4</td><td>0.03398731</td></tr>
	<tr><td> 5</td><td>0.47465615</td></tr>
	<tr><td> 6</td><td>0.48316093</td></tr>
	<tr><td> 7</td><td>0.01961896</td></tr>
	<tr><td> 8</td><td>0.78249028</td></tr>
	<tr><td> 9</td><td>1.11642522</td></tr>
	<tr><td>10</td><td>1.78370915</td></tr>
</tbody>
</table>

And there we have it! It's just that simple. You can use any of the built-in R types (`double`, `character`, `factor`, &c.) for the column types.
