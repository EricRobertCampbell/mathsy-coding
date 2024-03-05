---
title: Exploring Population Differences Using Bayesian Analysis In R with RStan
description: This post is concerned with the eventual goal of exploring population differences (e.g. differences in means) using Bayesian analysing using Stan and RStan, the R interface to Stan.
pubDate: 2024-04-01
---

Continuing on with the theme of modelling population differences, this post will examine that process using the popular Bayesian language / platform, [Stan](https://mc-stan.org/).

The first step will be to install [RStan](https://mc-stan.org/users/interfaces/rstan). This is an interface between Stan and R, allowing you to run Stan models from within R. This process is notoriously fiddly and difficult, but the instructions on the RStan page are very good and as long as you follow the steps you should be fine.

First, let's load the package.

```r
library(rstan)

# recommended options
options(mc.cores = parallel::detectCores())
rstan_options(auto_write = TRUE)
rstan_options(threads_per_chain = 1)

packageVersion("rstan")
```

    [1] ‘2.32.3’

The first thing that we'll do is run a very simple model: recovering the parameters for a Gaussian from a random selection from the distribution.

$$
\begin{align*}
w &\sim \text{Normal}(\mu, \sigma) \\
\mu &\sim \text{Normal}(0, 1) \\
\sigma &\sim \text{HalfNormal}(1) \\
\end{align*}
$$

```r
NUM_SAMPLES <- 1e3
mu <- 0
sigma <- 1

w <- rnorm(NUM_SAMPLES, mean=mu, sd=sigma)
```

Now that we have the data, we need to write the model in Stan. The format is very similar to the way that we wrote the model above. The code for the above model looks like the below in Stan.

```stan
// simple_model.stan

// this section is the data that we will add to the model
data {
    int<lower=0> n; // number of samples
    vector[n] w; // the actual samples
}

// these are the parameters to be used in the model
parameters {
    real mu;
    real<lower=0> sigma;
}

// the actual model
model {
    mu ~ normal(0, 1);
    sigma ~ normal(0, 1);

    w ~ normal(mu, sigma); // this describes how the data are distributed
}
```

Note that in order to avoid an error saying something about an incomplete line, just add a blank line to the end of the Stan file. Apparently it's a known issue.

Now let's fit the model using the `stan`, get a summary, and then extract the parameters (as samples). We need to specify the file which contains the Stan models, along with the data (formatted as a list).

```r
data <- list(n=length(w), w=w)
fit <- stan(file='simple_model.stan', data=data)
summary(fit)
```

<dl>
	<dt>$summary</dt>
		<dd><table class="dataframe">
<caption>A matrix: 3 × 10 of type dbl</caption>
<thead>
	<tr><th></th><th scope=col>mean</th><th scope=col>se_mean</th><th scope=col>sd</th><th scope=col>2.5%</th><th scope=col>25%</th><th scope=col>50%</th><th scope=col>75%</th><th scope=col>97.5%</th><th scope=col>n_eff</th><th scope=col>Rhat</th></tr>
</thead>
<tbody>
	<tr><th scope=row>mu</th><td>   0.02597236</td><td>0.0005827845</td><td>0.03262796</td><td>  -0.04121622</td><td> 4.538632e-03</td><td>   0.0260687</td><td>   0.04786533</td><td>   0.09049842</td><td>3134.468</td><td>1.000547</td></tr>
	<tr><th scope=row>sigma</th><td>   1.01445024</td><td>0.0004267207</td><td>0.02287461</td><td>   0.97043331</td><td> 9.984133e-01</td><td>   1.0143704</td><td>   1.03004736</td><td>   1.05924737</td><td>2873.557</td><td>1.001364</td></tr>
	<tr><th scope=row>lp__</th><td>-515.24968715</td><td>0.0258127557</td><td>1.02424096</td><td>-518.00629800</td><td>-5.156437e+02</td><td>-514.9284938</td><td>-514.51819964</td><td>-514.24947892</td><td>1574.474</td><td>1.001698</td></tr>
</tbody>
</table>
</dd>
	<dt>$c_summary</dt>
		<dd><style>
.list-inline {list-style: none; margin:0; padding: 0}
.list-inline>li {display: inline-block}
.list-inline>li:not(:last-child)::after {content: "\00b7"; padding: 0 .5ex}
</style>
</dd>
</dl>

Looking at the mean for our parameters, it looks like our model did a good job of recovering the values. Let's take a mode detailed look by extracting some samples.

```r
params <- extract(fit)
summary(params)
```

          Length Class  Mode
    mu    4000   -none- numeric
    sigma 4000   -none- numeric
    lp__  4000   -none- numeric

This contains the different samples for the parameters. With the benefit of knowing the underlying distribution, we can plot some of these to see how well we did.

```r
library(ggplot2)
options(repr.plot.width=15, repr.plot.height=8)
```

```r
x <- seq(-4, 4, by=0.1);
true <- dnorm(x, 0, 1)

plt <- ggplot(data.frame(x=x, y=true), aes(x, y)) +
    geom_line(colour='black', linewidth=2) +
    labs(x='w', y='Density', title="Simulated data for the mean")

for (index in sample(1:nrow(params$mu), 20, replace = TRUE)) {
    df <- data.frame(x=x, y=dnorm(x, mean=params$mu[index]), sd=params$sigma[index])
    plt <- plt +
        geom_line(data=df, mapping=aes(x, y), colour='blue', alpha=0.2)
}

print(plt)
```

![Plot of our predicted and actual data, showing a good match](/2024-04-01/actualAndPosterior1.png)

So this looks pretty good!

Of course, we could do better by doing a posterior predictive check - that is, using our final model to generate some data to ensure that it looks like the data that was used to fit the model. To do this, we can actually add some predicted data into the model. We just need to make a small modification to the Stan model.

```stan
// simple_model_ppc.stan

// this section is the data that we will add to the model
data {
    int<lower=0> n; // number of samples
    vector[n] w; // the actual samples
}

// these are the parameters to be used in the model
parameters {
    real mu;
    real<lower=0> sigma;
}

// the actual model
model {
    mu ~ normal(0, 1);
    sigma ~ normal(0, 1);

    w ~ normal(mu, sigma); // this describes how the data are distributed
}

// this is the section that we change - we want to add a posterior predictive check
generated quantities {
    vector[n] w_sim;

    for (i in 1:n) {
        w_sim[i] = normal_rng(mu, sigma);
    }
}

```

```r
ppc_fit <- stan(file="simple_model_ppc.stan", data=data)
summary(ppc_fit)
ppc_params <- extract(ppc_fit)
```

<dl>
	<dt>$summary</dt>
		<dd><table class="dataframe">
<caption>A matrix: 1003 × 10 of type dbl</caption>
<thead>
	<tr><th></th><th scope=col>mean</th><th scope=col>se_mean</th><th scope=col>sd</th><th scope=col>2.5%</th><th scope=col>25%</th><th scope=col>50%</th><th scope=col>75%</th><th scope=col>97.5%</th><th scope=col>n_eff</th><th scope=col>Rhat</th></tr>
</thead>
<tbody>
	<tr><th scope=row>mu</th><td> 0.025810450</td><td>0.0005388202</td><td>0.03148880</td><td>-0.03338427</td><td> 0.004332818</td><td> 0.025322161</td><td>0.04692252</td><td>0.08776891</td><td>3415.266</td><td>1.0005321</td></tr>
	<tr><th scope=row>sigma</th><td> 1.015913201</td><td>0.0003754666</td><td>0.02276205</td><td> 0.97354499</td><td> 0.999955002</td><td> 1.015059556</td><td>1.03107722</td><td>1.06183558</td><td>3675.192</td><td>0.9999481</td></tr>
	<tr><th scope=row>w_sim[1]</th><td> 0.012561131</td><td>0.0161172391</td><td>1.02058732</td><td>-2.01894175</td><td>-0.657810006</td><td> 0.007209496</td><td>0.69260442</td><td>1.97101691</td><td>4009.766</td><td>0.9996054</td></tr>
	<tr><th scope=row>w_sim[2]</th><td> 0.040253027</td><td>0.0161314894</td><td>1.01840079</td><td>-1.91445011</td><td>-0.656381401</td><td> 0.030597371</td><td>0.73512073</td><td>2.01208962</td><td>3985.552</td><td>0.9995883</td></tr>
	<tr><th scope=row>w_sim[3]</th><td> 0.022706146</td><td>0.0160527865</td><td>1.01124083</td><td>-1.95816825</td><td>-0.651363176</td><td> 0.044916355</td><td>0.71121470</td><td>1.96146212</td><td>3968.335</td><td>1.0006904</td></tr>
	<tr><th scope=row>w_sim[28]</th><td> 0.033896862</td><td>0.0172899348</td><td>1.01121499</td><td>-2.00957414</td><td>-0.629203502</td><td> 0.035372024</td><td>0.70714091</td><td>1.99001365</td><td>3420.584</td><td>1.0002338</td></tr>
	<tr><th scope=row>⋮</th><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td></tr>
	<tr><th scope=row>w_sim[972]</th><td> 5.552801e-02</td><td>0.01623083</td><td>1.0229120</td><td>  -1.983298</td><td>  -0.6182711</td><td> 5.770454e-02</td><td>   0.7213428</td><td>   2.055063</td><td>3971.872</td><td>0.9997000</td></tr>
	<tr><th scope=row>w_sim[1000]</th><td> 4.159035e-02</td><td>0.01720112</td><td>1.0235276</td><td>  -2.003147</td><td>  -0.6280401</td><td> 6.721470e-02</td><td>   0.7225033</td><td>   2.064001</td><td>3540.670</td><td>0.9998228</td></tr>
	<tr><th scope=row>lp__</th><td>-5.152061e+02</td><td>0.02251679</td><td>0.9588736</td><td>-517.805703</td><td>-515.5911481</td><td>-5.149248e+02</td><td>-514.5125150</td><td>-514.251023</td><td>1813.467</td><td>1.0002974</td></tr>
</tbody>
</table>
</dd>
	<dt>$c_summary</dt>
		<dd><style>
.list-inline {list-style: none; margin:0; padding: 0}
.list-inline>li {display: inline-block}
.list-inline>li:not(:last-child)::after {content: "\00b7"; padding: 0 .5ex}
</style>
</dd>
</dl>

Now we can compare our data to the simulated results by choosing 10 random bunches of simulated data and graphing it, along with the actual data.

```r
df <- data.frame(w=w)

plt <- ggplot(df, aes(w)) +
    geom_density(aes(y=after_stat(scaled)), linewidth=2, colour='black') +
    labs(x='w', y="Density", title="Comparison of actual vs. simulated data")


for(index in sample(1:nrow(ppc_params$w_sim), 10)) {
    plt <- plt +
        geom_density(data=data.frame(x=ppc_params$w_sim[index,]), mapping=aes(x, y=after_stat(scaled)), colour=alpha('blue', 0.2))
}
print(plt)
```

![Another plot of the density of the data with some sample densities, showing a good match between the data](/2024-04-01/actualAndPosterior2.png)

## Using Summary Statistics

In addition to using the actual data, we can also use the summary statistics (sample mean and sample standard deviation) to generate a posterior. I've found this to be useful in the case where the raw data is inaccessible (due to age or other restrictions) but the summary statistics have been published. To do this, we rely on two facts:

$$
\begin{align*}
\bar{X} &\sim \text{Normal}(\mu, \sigma / \sqrt{n}) \\
\frac{(n-1)s^2}{\sigma^2} &\sim \chi^2(n - 1) \\
\end{align*}
$$

Both of these facts can be encode in a Stan model.

```stan
// simple_model_ppc_summary.stan

// this section is the data that we will add to the model
data {
    int<lower=0> n; // number of samples
    real x_bar; // sample mean
    real<lower=0> s; // sample standard deviation
}

// these are the parameters to be used in the model
parameters {
    real mu;
    real<lower=0> sigma;
}

// the actual model
model {
    mu ~ normal(0, 1);
    sigma ~ normal(0, 1);

    real modified_s = (n - 1) * s^2 / sigma^2;

    x_bar ~ normal(mu, sigma / sqrt(n)); // this describes how the data are distributed
    modified_s ~ chi_square(n - 1);
}

// data for the posterior predictive check
generated quantities {
    vector[n] w_sim;

    for (i in 1:n) {
        w_sim[i] = normal_rng(mu, sigma);
    }
}

```

```r
summary_fit <- stan(file='simple_model_ppc_summary.stan', data=list(n=length(w), x_bar=mean(w), s=sd(w)))
summary(summary_fit)
```

<dl>
	<dt>$summary</dt>
		<dd><table class="dataframe">
<caption>A matrix: 1003 × 10 of type dbl</caption>
<thead>
	<tr><th></th><th scope=col>mean</th><th scope=col>se_mean</th><th scope=col>sd</th><th scope=col>2.5%</th><th scope=col>25%</th><th scope=col>50%</th><th scope=col>75%</th><th scope=col>97.5%</th><th scope=col>n_eff</th><th scope=col>Rhat</th></tr>
</thead>
<tbody>
	<tr><th scope=row>mu</th><td> 0.024834235</td><td>0.0005916098</td><td>0.03339289</td><td>-0.03943811</td><td> 0.002238256</td><td> 0.024639415</td><td>0.04706407</td><td>0.09141525</td><td>3185.937</td><td>1.0013604</td></tr>
	<tr><th scope=row>sigma</th><td> 1.015434182</td><td>0.0004143965</td><td>0.02306986</td><td> 0.97260845</td><td> 0.999503487</td><td> 1.014924975</td><td>1.03053549</td><td>1.06160283</td><td>3099.258</td><td>1.0000964</td></tr>
	<tr><th scope=row>w_sim[1]</th><td> 0.014455045</td><td>0.0159013104</td><td>1.01510507</td><td>-1.91725272</td><td>-0.690326722</td><td> 0.018145823</td><td>0.69572528</td><td>2.00411045</td><td>4075.268</td><td>1.0010727</td></tr>
	<tr><th scope=row>w_sim[28]</th><td> 0.042364698</td><td>0.0157351743</td><td>0.99763643</td><td>-1.93211158</td><td>-0.630438791</td><td> 0.046843407</td><td>0.72574547</td><td>1.97958825</td><td>4019.773</td><td>1.0014029</td></tr>
	<tr><th scope=row>⋮</th><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td></tr>
	<tr><th scope=row>w_sim[972]</th><td> 1.024258e-02</td><td>0.01653087</td><td>1.0225007</td><td>  -2.018235</td><td>  -0.6773512</td><td> 2.487396e-02</td><td>   0.7090567</td><td>   1.980203</td><td>3825.918</td><td>1.0001160</td></tr>
	<tr><th scope=row>w_sim[1000]</th><td>-5.485209e-03</td><td>0.01707601</td><td>1.0254360</td><td>  -2.008587</td><td>  -0.6838811</td><td>-2.336391e-04</td><td>   0.6810644</td><td>   2.015877</td><td>3606.153</td><td>1.0010102</td></tr>
	<tr><th scope=row>lp__</th><td> 2.945402e+03</td><td>0.02635960</td><td>1.0639737</td><td>2942.602144</td><td>2944.9820042</td><td> 2.945726e+03</td><td>2946.1466281</td><td>2946.430291</td><td>1629.237</td><td>1.0020386</td></tr>
</tbody>
</table>
</dd>
	<dt>$c_summary</dt>
		<dd><style>
.list-inline {list-style: none; margin:0; padding: 0}
.list-inline>li {display: inline-block}
.list-inline>li:not(:last-child)::after {content: "\00b7"; padding: 0 .5ex}
</style>
</dd>
</dl>

```r
summary_params <- extract(summary_fit)
```

Once again, we can visually check against the original data.

```r
df <- data.frame(w=w)

plt <- ggplot(df, aes(w)) +
    geom_density(aes(y=after_stat(scaled)), linewidth=2, colour='black') +
    labs(x='w', y="Density", title="Comparison of actual vs. simulated data (from summary data)")


for(index in sample(1:nrow(summary_params$w_sim), 10)) {
    plt <- plt +
        geom_density(data=data.frame(x=summary_params$w_sim[index,]), mapping=aes(x, y=after_stat(scaled)), colour=alpha('blue', 0.2))
}
print(plt)
```

![A plot of a good match between the original data and some data simulated from the posterior](/2024-04-01/ppc.png)

## Difference of Means

Now that we have the basics out of the way, we can look at the distribution of the differences in means between two populations! The first method we'll use is to model each population separately, and then get the distribution of the difference of means from that.

```stan
data {
    int<lower=0> N;
    vector[N] w_1;
    vector[N] w_2;
}

parameters {
    real mu_1;
    real mu_2;
    real<lower=0> sigma;
}

model {
    mu_1 ~ normal(0, 2);
    mu_2 ~ normal(0, 2);
    sigma ~ normal(0, 1);

    w_1 ~ normal(mu_1, sigma);
    w_2 ~ normal(mu_2, sigma);
}

```

```r
mu <-c(-1, 1)
sigma <- 1

w_1 <- rnorm(NUM_SAMPLES, mean=mu[1], sd=sigma)
w_2 <- rnorm(NUM_SAMPLES, mean=mu[2], sd=sigma)

difference_fit <- stan(file='difference_means.stan', data=list(N=NUM_SAMPLES, w_1=w_1, w_2=w_2))
summary(difference_fit)
```

<dl>
	<dt>$summary</dt>
		<dd><table class="dataframe">
<caption>A matrix: 4 × 10 of type dbl</caption>
<thead>
	<tr><th></th><th scope=col>mean</th><th scope=col>se_mean</th><th scope=col>sd</th><th scope=col>2.5%</th><th scope=col>25%</th><th scope=col>50%</th><th scope=col>75%</th><th scope=col>97.5%</th><th scope=col>n_eff</th><th scope=col>Rhat</th></tr>
</thead>
<tbody>
	<tr><th scope=row>mu_1</th><td>  -1.0106497</td><td>0.0004784863</td><td>0.03100593</td><td>  -1.0720868</td><td>  -1.0305666</td><td>  -1.0105328</td><td>  -0.9895498</td><td>  -0.9509228</td><td>4199.043</td><td>0.9995809</td></tr>
	<tr><th scope=row>mu_2</th><td>   0.9976796</td><td>0.0004909118</td><td>0.03090297</td><td>   0.9376764</td><td>   0.9767728</td><td>   0.9977505</td><td>   1.0185254</td><td>   1.0587181</td><td>3962.721</td><td>0.9996719</td></tr>
	<tr><th scope=row>sigma</th><td>   0.9820112</td><td>0.0002207197</td><td>0.01584171</td><td>   0.9512097</td><td>   0.9714469</td><td>   0.9818158</td><td>   0.9922650</td><td>   1.0131478</td><td>5151.362</td><td>1.0000500</td></tr>
	<tr><th scope=row>lp__</th><td>-964.0037707</td><td>0.0275646936</td><td>1.26107968</td><td>-967.1965946</td><td>-964.5648992</td><td>-963.6988244</td><td>-963.0975006</td><td>-962.5887301</td><td>2093.046</td><td>1.0043513</td></tr>
</tbody>
</table>
</dd>
	<dt>$c_summary</dt>
		<dd><style>
.list-inline {list-style: none; margin:0; padding: 0}
.list-inline>li {display: inline-block}
.list-inline>li:not(:last-child)::after {content: "\00b7"; padding: 0 .5ex}
</style>
</dd>
</dl>

```r
difference_params <- extract(difference_fit)
differences <- difference_params$mu_1 - difference_params$mu_2

ggplot(data.frame(x=differences), aes(x)) +
    geom_density(aes(y=after_stat(scaled))) +
    labs(x="Difference", y="Density", title="Distribution of the Difference")
```

![A plot of the empirical distribution of the difference of means, showing it centred around -2 as we expectd.](/2024-04-01/meanDifferenceDistribution.png)

This is basically what we expected to see - a difference of 2. If we wanted, we could also extract a credible interval from the data.

```r
diff_ci <- quantile(differences, probs=c(0.025, 0.975))
diff_ci
```

<style>
.dl-inline {width: auto; margin:0; padding: 0}
.dl-inline>dt, .dl-inline>dd {float: none; width: auto; display: inline-block}
.dl-inline>dt::after {content: ":\0020"; padding-right: .5ex}
.dl-inline>dt:not(:first-of-type) {padding-left: .5ex}
</style><dl class=dl-inline><dt>2.5%</dt><dd>-2.09156770868759</dd><dt>97.5%</dt><dd>-1.92164095109226</dd></dl>

So our 95% credible interval is roughly -2.1 - -1.9.

Of course, if all we wanted was the difference, we could also just model the difference itself as a normally distributed random variable. Since we've done that quite a bit already in this post, I'll leave that one as an exercise for the reader.

## Conclusion

In this post, I've gone through a few simple examples of using Stan through the RStan package in order to fit Bayesian models, with the the goal of looking at population differences (e.g. a difference in the means). Personally, I quite like using Stan; everything seems to work in a reasonable way, the documentation is good, and creating and extracting information from the models is straightforward.

## Further Reading

-   The Stan [YouTube]() channel, particularly the [introductory videos](https://www.youtube.com/playlist?list=PLCrWEzJgSUqwL85xIj1wubGdY15C5Gf7H) are an excellent start.
-   The [Stan User Guide](https://mc-stan.org/users/documentation/) I've found to be a good resource
