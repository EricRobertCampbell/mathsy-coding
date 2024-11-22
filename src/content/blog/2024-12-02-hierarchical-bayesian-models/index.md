---
title: Hierarchical Bayesian Models
description: A look at hierarchical models, a kind of model that allows you to share information between different clusters of data. We'll start with a simple example and then apply it to a real-world situation.
pubDate: 2024-12-02
---

Recently I've been learning about multilevel models. These are a kind of model where, by clustering the data in some way, you can 'share' information between different pieces of the model. That makes them an excellent way to get the most out of the often limited data that you might have available. Another advantage of these models is that it provides a way to account for additional uncertainty, in much the same way that a mixture model does. Let's go through and see how to construct such a model (specifically, a varying-intercepts model) and cap it off with a real-world application!

## Example - Heights

Let's start off with a relatively simple example. We're going to look at the simulated heights of people in different countries. In this situation, there is a natural hierarchical nature to the data: each height belongs to a person and each student belongs to a country. We might naturally expect that the country that a person is part of will have some influence on their score. There are a few ways that we could approach this:

1. **Ignore the countries** We could just ignore the fact that the people are in different countries and group them all together when making our model. This approach is called _complete pooling_.
2. **Fit separate models** Another approach would be to fit a separate model to each country completely independently. This is the _no pooling_ approach.

At least in this case, both of those seem unsatisfactory. It seems very likely that there is some similarity between the countries - if you learn the mean for one country, that might influence your belief about the next country you visit. So how can we incorporate that information? Essentially, we're going to fit a model for each country, _but_ each one will share a common prior. This prior will be influenced by the data, and since it is shared between each country that will allow the information from one country to influence the model for the others.

This approach, where we share some information between the different clusters (countries, in this case) is called _partial pooling_. In the case where there is a hierarchical structure to the data, we call it a _hierarchical model_.

Let's try this on some simulated data to see how it works before we apply it to some real data on diploma exam results in Alberta.

### Simulation

First let's set up the situation. For simplicity, we'll assume that each person's height is drawn from a normal distribution, and that the mean of that distribution is specific to each country. However, we'll also assume that the means for the different countries are drawn from a common distribution as well. This will show up in the model as a shared prior.

Let's use this process to generate some data, and then we'll use the same model to recover it.

```r
# Set up the environment
library(ggplot2)
library(cmdstanr)
library(posterior)
library(readxl)

options(repr.plot.width = 17, repr.plot.height = 8)
```

```r
set.seed(500)

# country parameters
NUM_COUNTRIES <- 4
country_means <- rnorm(NUM_COUNTRIES, 176, 10)
country_sigma <- rexp(1, 1)

# now generate some people
NUM_PEOPLE <- 20
country_data <- data.frame(
    country_index = as.factor(rep(1:NUM_COUNTRIES, each = NUM_PEOPLE)),
    height = rnorm(
        n = NUM_COUNTRIES * NUM_PEOPLE,
        mean = rep(country_means, each = NUM_PEOPLE),
        sd = 3
    )
)

ggplot(country_data, aes(height)) +
    geom_density(aes(group = country_index, colour = country_index)) +
    geom_vline(data = data.frame(country = as.factor(1:NUM_COUNTRIES), mean = country_means), mapping = aes(xintercept = mean, colour = country)) +
    labs(x = "Height (cm)", y = "Density", colour = "Country") +
    theme_bw() +  # Set background to white
    theme(
        panel.grid.major.y = element_line(size = 0.5, linetype = 'dashed', colour = "grey")
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_2_0.png)

To recover the values, let's use the following model.

$$
\begin{align*}
H_i &\sim \text{Normal}( \mu_i, \sigma ) \\
\mu_i &\sim \text{Normal}(\mu_{\text{COUNTRY}[i]}, \sigma_{\text{COUNTRY}}) \\
\mu_{\text{COUNTRY}} &\sim \text{Normal}(\bar{\alpha}, 2) \\
\bar{\alpha} &\sim \text{Normal}(176, 1) \\
\sigma_{\text{COUNTRY}} &\sim \text{Exponential}(1) \\
\sigma &\sim \text{Exponential}(1) \\
\end{align*}
$$

The way that we're going to share the information between the countries is through the $\bar\alpha$ parameter. Because this mean value for the prior for each country must be the same for each of the different countries, it provides a way for that data to flow between them as the model is fit.

Now that we have the data and know the generative process behind it, let's ensure that we can recover those same values using the model.

```r
stan_model_code <- "
data {
    int<lower = 0> N_COUNTRIES; // number of countries
    int<lower = 0> N; // number of people
    vector[N] heights;
    array[N] int<lower = 0, upper = N_COUNTRIES> country_id; // the country id corresponding to each height
}
parameters {
    vector[N_COUNTRIES] mu_country;
    real<lower = 1e-3> sigma; // sd for the heights
    real<lower = 1e-3> sigma_country; // sd for the country mean values
    real alpha_bar;
}
model {
    heights ~ normal(mu_country[country_id], sigma);
    mu_country ~ normal(alpha_bar, 10);
    alpha_bar ~ normal(176, 1);
    sigma_country ~ exponential(1);
    sigma ~ exponential(1);
}
"
stan_model_file <- write_stan_file(stan_model_code)
stan_model <- cmdstan_model(stan_model_file)

stan_model_data <- list(
    N_COUNTRIES = NUM_COUNTRIES,
    N = nrow(country_data),
    heights = country_data$height,
    country_id = as.integer(country_data$country_index)
)
fit <- stan_model$sample(
    data = stan_model_data,
    chains = 4
)
```

    Running MCMC with 4 sequential chains...

    All 4 chains finished successfully.
    Mean chain execution time: 0.0 seconds.
    Total execution time: 0.5 seconds.

```r
fit$summary()
```

<table class="dataframe">
<caption>A draws_summary: 8 × 10</caption>
<thead>
	<tr><th scope=col>variable</th><th scope=col>mean</th><th scope=col>median</th><th scope=col>sd</th><th scope=col>mad</th><th scope=col>q5</th><th scope=col>q95</th><th scope=col>rhat</th><th scope=col>ess_bulk</th><th scope=col>ess_tail</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>lp__         </td><td>-144.334351</td><td>-143.9545000</td><td>1.9631562</td><td>1.7183334</td><td>-148.04970000</td><td>-141.819900</td><td>1.000846</td><td>1640.376</td><td>2355.089</td></tr>
	<tr><td>mu_country[1]</td><td> 185.073222</td><td> 185.0600000</td><td>0.7513226</td><td>0.7405587</td><td> 183.82495000</td><td> 186.320100</td><td>1.000304</td><td>6575.682</td><td>3154.603</td></tr>
	<tr><td>mu_country[2]</td><td> 194.750996</td><td> 194.7570000</td><td>0.7414349</td><td>0.7220262</td><td> 193.50895000</td><td> 195.958100</td><td>1.001592</td><td>7044.055</td><td>2985.646</td></tr>
	<tr><td>mu_country[3]</td><td> 185.335148</td><td> 185.3370000</td><td>0.7385066</td><td>0.6983046</td><td> 184.07985000</td><td> 186.547750</td><td>1.001719</td><td>7405.325</td><td>2834.630</td></tr>
	<tr><td>mu_country[4]</td><td> 176.916428</td><td> 176.9180000</td><td>0.7482134</td><td>0.7650216</td><td> 175.69300000</td><td> 178.154050</td><td>1.001806</td><td>6358.099</td><td>2966.653</td></tr>
	<tr><td>sigma        </td><td>   3.342929</td><td>   3.3194700</td><td>0.2687868</td><td>0.2637768</td><td>   2.93077650</td><td>   3.815515</td><td>1.001739</td><td>6754.819</td><td>3248.544</td></tr>
	<tr><td>sigma_country</td><td>   1.000606</td><td>   0.6943115</td><td>0.9873734</td><td>0.7047710</td><td>   0.04307331</td><td>   2.940308</td><td>1.000265</td><td>3774.295</td><td>1877.089</td></tr>
	<tr><td>alpha_bar    </td><td> 176.364408</td><td> 176.3655000</td><td>0.9784172</td><td>0.9748095</td><td> 174.74800000</td><td> 177.984050</td><td>1.000514</td><td>7930.243</td><td>2686.251</td></tr>
</tbody>
</table>

From the summary table, we can see that our posterior values are close to the true values. Let's see the same thing graphically.

```r
height_draws <- as_draws_matrix(fit)
head(height_draws)
```

<table class="dataframe">
<caption>A draws_matrix: 6 × 8 of type dbl</caption>
<thead>
	<tr><th></th><th scope=col>lp__</th><th scope=col>mu_country[1]</th><th scope=col>mu_country[2]</th><th scope=col>mu_country[3]</th><th scope=col>mu_country[4]</th><th scope=col>sigma</th><th scope=col>sigma_country</th><th scope=col>alpha_bar</th></tr>
</thead>
<tbody>
	<tr><th scope=row>1</th><td>-144.016</td><td>185.422</td><td>194.549</td><td>185.765</td><td>176.804</td><td>3.57034</td><td>0.0527758</td><td>175.646</td></tr>
	<tr><th scope=row>2</th><td>-143.700</td><td>184.574</td><td>194.249</td><td>184.553</td><td>176.397</td><td>3.26862</td><td>3.6745100</td><td>177.132</td></tr>
	<tr><th scope=row>3</th><td>-145.799</td><td>183.510</td><td>195.764</td><td>184.747</td><td>176.220</td><td>3.36722</td><td>0.3739620</td><td>175.124</td></tr>
	<tr><th scope=row>4</th><td>-144.623</td><td>185.169</td><td>193.716</td><td>184.875</td><td>176.145</td><td>3.54078</td><td>1.0502200</td><td>178.216</td></tr>
	<tr><th scope=row>5</th><td>-143.933</td><td>184.849</td><td>195.680</td><td>185.868</td><td>177.684</td><td>3.21139</td><td>0.9323830</td><td>174.692</td></tr>
	<tr><th scope=row>6</th><td>-144.299</td><td>185.165</td><td>193.932</td><td>184.807</td><td>176.049</td><td>3.46684</td><td>1.2301000</td><td>178.207</td></tr>
</tbody>
</table>

```r
country_mean_results <- height_draws[, grep('mu_country', colnames(height_draws))]
results_df <- data.frame(
    country_id = 1:NUM_COUNTRIES,
    mean = apply(country_mean_results, 2, mean),
    lower = apply(country_mean_results, 2, function(row) quantile(row, 0.025)),
    upper = apply(country_mean_results, 2, function(row) quantile(row, 0.975)),
    type = "Posterior"
)

posterior_alpha_bar <- mean(height_draws[, 'alpha_bar'])

ggplot(results_df, aes(country_id, mean)) +
    geom_point(aes(colour = type)) +
    geom_errorbar(aes(ymin = lower, ymax = upper)) +
    geom_point(data = data.frame(country_id = 1:NUM_COUNTRIES, mean = country_means, type = "Actual"), mapping = aes(colour = type)) +
    geom_hline(mapping = aes(yintercept = posterior_alpha_bar), linetype = 'dashed') +
    labs(x = "Country", y = "Height (cm)", colour = "Type") +
    theme_bw() +  # Set background to white
    theme(
        panel.grid.major.y = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_9_0.png)

One thing to note is that we have a larger error than we would expect if we fit each country individually. The reason for that is that a hierarchical model like this tends to 'shrink' estimates towards the mean. You can see this here by the fact that the values of the posterior tend to be closer to the mean than the actual values. While it may seem crazy to deliberately choose a model that will tend to do worse on the data, in fact this is just part of the overfitting / underfitting tradeoff - by biasing estimates to the mean, we will do worse on our training set but better on outside data.

So now that we've seen a relatively simple example, let's try to build our way towards our eventual goal of applying this idea to school test scores.

## Example - School Test Scores

Imagine that you have a number of different schools in a school division, and you're interested in how the students in those schools are doing on a test. We believe that each school has an effect on the students, and we also believe that the school division has an effect on the school. Here we have two nested pools - each student belongs to a school, and each school belongs to a district.

### Simulation

Imagine that you have nine schools taking part in some sort of standardized exam. Each school has some number of students that are taking the exam, and they each get a grade. The grade they get is a combination of luck, their own properties, and some influence of the school. The influence of the school is itself dependent on the school district. Let's try to generate some data, then create a model to recover the original values. By doing so, we're ensuring that our model is fit for purpose.

Since this model is a bit more complex, let's take it one step at a time.

First, let's start with a single school. The distribution for the school's students will be drawn from a beta distribution. The beta is the perfect distribution for this since it's a distribution of probabilities, which is what we're looking for. The beta distribution has two parameters, $\alpha$ and $\beta$. The mean is $\alpha / (\alpha + \beta)$, and the variance is $\alpha\beta / (\alpha + \beta)^2 (\alpha + \beta + 1)$. If we're thinking of the beta distribution as being related to a Binomial random process (i.e. a set of coin flips), then we can think of $\alpha$ as the number of successes and $\beta$ as the number of failures. This is not quite correct, but it's pretty close.

So let's say that we want the school average to be about 75%. There are a few different values of $\alpha$ and $\beta$ that we could choose; we just need the mean $\alpha / (\alpha + \beta) = 0.75$. For instance, $\alpha = 3$ and $\beta = 1$ would work. So would any multiple of the those: 6 and 2, 4 and $\frac{4}{3}$, &c.

```r
alpha_base <- 3
beta_base <- 1

multiples <- seq.int(from = 1, to = 4)
plot_df <- data.frame(p = numeric(), density = numeric(), type = character())

probs <- seq(from = 0, to = 1, length.out = 100)
for (multiple in multiples) {
    alpha <- alpha_base * multiple
    beta <- beta_base * multiple
    data <- data.frame(p = probs, density = dbeta(probs, alpha, beta), type = paste("alpha = ", alpha, " beta = ", beta))
    plot_df <- rbind(plot_df, data)
}

ggplot(plot_df, aes(p, density, group = type, colour = type)) +
    geom_line() +
    labs(x = "p", y = "Density", colour = "Parameter Values") +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +  # Set background to white
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_12_0.png)

Note that although the mean for each of these is at $0.75$, that's not the same as having the peak value be there.

If we're thinking forward to making our model, it's not clear to me exactly what we should be thinking of the parameters $\alpha$ and $\beta$ as representing. Intuitively, I'd prefer to think in terms of the mean and variance (or even more generally, the centre and the spread) of the expected data. Luckily, it turns out that there is a reparameterization of the beta in terms of these:

$$
\begin{align*}
\mu &= \frac{\alpha}{\alpha + \beta} & [\text{The mean - centre}]\\
\nu &= \alpha + \beta & [\text{The `sample size' - spread}]
\end{align*}
$$

Solving for $\alpha$ and $\beta$,

$$
\begin{align*}
\alpha &= \mu\nu \\
\beta &= (1 - \mu)\nu
\end{align*}
$$

Let's recreate the above using this parameterization to convince ourselves that it works. Since we're fixing our mean, the spread parameter is the only one that needs to change.

```r
mu <- 0.75
spread <- 4 # 'sample size'

plot_df <- data.frame(p = numeric(), density = numeric(), type = character())

probs <- seq(from = 0, to = 1, length.out = 100)
for (sample_size in seq.int(from = 4, to = 16, by = 4)) {
    alpha <- mu * sample_size
    beta <- (1 - mu) * sample_size
    data <- data.frame(p = probs, density = dbeta(probs, alpha, beta), type = paste("mu = ", mu, " nu = ", sample_size))
    plot_df <- rbind(plot_df, data)
}

ggplot(plot_df, aes(p, density, group = type, colour = type)) +
    geom_line() +
    labs(x = "p", y = "Density", colour = "Parameter Values") +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +  # Set background to white
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_14_0.png)

Great! So now we have our parameterization. Let's make sure that we can model at least this part of the problem. Let's say that we have a school where the average test score is 75%, and let's simulate a class of 20 students.

```r
NUM_STUDENTS <- 20
school_mu <- 0.75
school_nu <- 10 # this is *not* the same as the number of students!

alpha <- school_mu * school_nu
beta <- (1 - school_mu) * school_nu

actual_student_scores <- rbeta(NUM_STUDENTS, alpha, beta)

p <- seq(from = 0, to = 1, length.out = 100)
line_data <- data.frame(p = p, density = dbeta(p, alpha, beta))
student_data <- data.frame(p = actual_student_scores, density = dbeta(actual_student_scores, alpha, beta))
ggplot() +
    geom_line(data = line_data, mapping = aes(p, density)) +
    geom_point(data = student_data, mapping = aes(p, density)) +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_16_0.png)

So here we can see the theoretical distribution of the students' scores along with the actual scores. Now let's use a model to recover those values!

$$
\begin{align*}
\text{s} &\sim \text{Beta}(\alpha, \beta) \\
\alpha &= \mu * \nu \\
\beta &= (1 - \mu) * \nu \\
\mu &\sim \text{beta}(12, 4) \\
\nu &\sim \text{Normal}(10, 1)
\end{align*}
$$

How did we arrive at those priors? We ran some simulations of the model with different parameters to find ones that were reasonable. In a real model we would do this _before_ looking at the data, but in this case that's not really possible. We'll just pretend that we don't know what the data should look like. Also, when checking a model like this, it's not unreasonable to start with a model that reflects the true underlying process - the idea here is that we are ground-truthing it. If the model can't get back the correct values even when we know the model is correct and the values are close, then it really isn't fit for purpose.

```r
NUM_SIM_STUDENTS <- 100
nu <- rnorm(NUM_SIM_STUDENTS, 10, 1)
mu <- rbeta(NUM_SIM_STUDENTS, 12, 4)
alpha <- mu * nu
beta <- (1 - mu) * nu
s <- rbeta(NUM_SIM_STUDENTS, alpha, beta)

plot_df <- data.frame(s = s)
ggplot(plot_df, aes(s)) +
    geom_density() +
    labs(x = "Score", y = "Density") +
    coord_cartesian(xlim = c(0, 1)) +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_18_0.png)

```r
ggplot(data.frame(nu = nu), aes(nu)) +
    geom_density() +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    labs(x = "Score", y = "Density") +
    theme_bw() +
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_19_0.png)

Before we do anything else, let's do a prior predictive check. The idea here is to see what kind of values our model is producing before we feed it any data. In large part this should help to constrain our priors - are the data that we're seeing come out of the model in line with our expectations? Are they plausible? If not, we'll have to go back and revise our priors. We can actually use Stan to help us with this.

```r
student_score_model_pp_code <- "
data {
    int<lower = 0> N; // number of students
}
parameters {
    real<lower = 0, upper = 1> mu;
    real<lower = 0> nu;
}
 transformed parameters {
    real<lower = 0> a = mu * nu;
    real<lower = 0> b = (1 - mu) * nu;
}
model {
    mu ~ beta(12, 4);
    nu ~ normal(10, 1);
}
generated quantities {
    vector[N] s_sim;
    for (n in 1:N) {
        s_sim[n] = beta_rng(a, b);
    }
}
"

student_score_model_pp_file <- write_stan_file(student_score_model_pp_code)
student_score_pp_model <- cmdstan_model(student_score_model_pp_file)

student_score_model_pp_data <- list(
    N = 100
)

student_score_pp_fit <- student_score_pp_model$sample(
    data = student_score_model_pp_data,
    chains = 4
)
student_score_pp_fit$summary()
```

    Running MCMC with 4 sequential chains...

    All 4 chains finished successfully.
    Mean chain execution time: 0.0 seconds.
    Total execution time: 0.5 seconds.

<table class="dataframe">
<caption>A draws_summary: 105 × 10</caption>
<thead>
	<tr><th scope=col>variable</th><th scope=col>mean</th><th scope=col>median</th><th scope=col>sd</th><th scope=col>mad</th><th scope=col>q5</th><th scope=col>q95</th><th scope=col>rhat</th><th scope=col>ess_bulk</th><th scope=col>ess_tail</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>lp__     </td><td>-7.7472137</td><td>-7.3961950</td><td>1.1037489</td><td>0.7291056</td><td>-10.0643700</td><td>-6.7499540</td><td>1.0005178</td><td>1726.762</td><td>1776.441</td></tr>
	<tr><td>mu       </td><td> 0.7536242</td><td> 0.7642695</td><td>0.1042146</td><td>0.1057909</td><td>  0.5686431</td><td> 0.9068932</td><td>1.0015275</td><td>3183.736</td><td>1685.494</td></tr>
	<tr><td>nu       </td><td> 9.9871312</td><td>10.0048000</td><td>1.0097168</td><td>0.9897838</td><td>  8.2924295</td><td>11.6080150</td><td>1.0008779</td><td>3470.894</td><td>2249.882</td></tr>
	<tr><td>a        </td><td> 7.5237364</td><td> 7.5277800</td><td>1.2812031</td><td>1.2879643</td><td>  5.3965645</td><td> 9.6125255</td><td>1.0006855</td><td>3423.556</td><td>2280.696</td></tr>
	<tr><td>b        </td><td> 2.4633951</td><td> 2.3360800</td><td>1.0812236</td><td>1.0767531</td><td>  0.8796699</td><td> 4.3757240</td><td>1.0014289</td><td>3148.109</td><td>1744.702</td></tr>
	<tr><td>s_sim[1] </td><td> 0.7519102</td><td> 0.7771395</td><td>0.1645582</td><td>0.1691661</td><td>  0.4368936</td><td> 0.9719049</td><td>0.9997345</td><td>3638.240</td><td>3666.031</td></tr>
	<tr><td>s_sim[2] </td><td> 0.7511981</td><td> 0.7766295</td><td>0.1655453</td><td>0.1734783</td><td>  0.4370754</td><td> 0.9752769</td><td>1.0019282</td><td>3536.600</td><td>2732.750</td></tr>
	<tr><td>s_sim[3] </td><td> 0.7534096</td><td> 0.7796105</td><td>0.1623245</td><td>0.1685798</td><td>  0.4469912</td><td> 0.9749123</td><td>1.0000188</td><td>3211.546</td><td>2890.503</td></tr>
	<tr><td>s_sim[4] </td><td> 0.7516449</td><td> 0.7772990</td><td>0.1643784</td><td>0.1697799</td><td>  0.4385267</td><td> 0.9744425</td><td>0.9998382</td><td>3465.035</td><td>3140.728</td></tr>
	<tr><td>s_sim[5] </td><td> 0.7500511</td><td> 0.7759265</td><td>0.1690192</td><td>0.1730068</td><td>  0.4296476</td><td> 0.9745945</td><td>1.0011223</td><td>3213.409</td><td>2759.927</td></tr>
	<tr><td>s_sim[6] </td><td> 0.7546354</td><td> 0.7789480</td><td>0.1622561</td><td>0.1683270</td><td>  0.4521205</td><td> 0.9721189</td><td>1.0016519</td><td>3591.587</td><td>2984.244</td></tr>
	<tr><td>s_sim[7] </td><td> 0.7550554</td><td> 0.7788565</td><td>0.1603555</td><td>0.1662313</td><td>  0.4607637</td><td> 0.9725681</td><td>1.0003974</td><td>3557.438</td><td>2779.617</td></tr>
	<tr><td>s_sim[8] </td><td> 0.7549163</td><td> 0.7815435</td><td>0.1658129</td><td>0.1695472</td><td>  0.4389618</td><td> 0.9750677</td><td>0.9996789</td><td>3018.343</td><td>2864.190</td></tr>
	<tr><td>s_sim[9] </td><td> 0.7557622</td><td> 0.7824510</td><td>0.1628229</td><td>0.1724256</td><td>  0.4547386</td><td> 0.9739696</td><td>1.0000825</td><td>3615.700</td><td>3202.578</td></tr>
	<tr><td>s_sim[10]</td><td> 0.7580823</td><td> 0.7858460</td><td>0.1645778</td><td>0.1722047</td><td>  0.4479410</td><td> 0.9737689</td><td>0.9997881</td><td>3390.171</td><td>3311.547</td></tr>
	<tr><td>s_sim[11]</td><td> 0.7526162</td><td> 0.7805120</td><td>0.1665224</td><td>0.1725220</td><td>  0.4385346</td><td> 0.9756622</td><td>1.0006392</td><td>3648.114</td><td>3135.257</td></tr>
	<tr><td>s_sim[12]</td><td> 0.7547576</td><td> 0.7769915</td><td>0.1628121</td><td>0.1683196</td><td>  0.4495085</td><td> 0.9720077</td><td>0.9997057</td><td>3701.263</td><td>3590.140</td></tr>
	<tr><td>s_sim[13]</td><td> 0.7549515</td><td> 0.7827305</td><td>0.1646374</td><td>0.1691936</td><td>  0.4403020</td><td> 0.9741046</td><td>1.0009201</td><td>3463.333</td><td>3247.366</td></tr>
	<tr><td>s_sim[14]</td><td> 0.7562782</td><td> 0.7825465</td><td>0.1624611</td><td>0.1725020</td><td>  0.4543448</td><td> 0.9743693</td><td>1.0007592</td><td>3531.548</td><td>3317.929</td></tr>
	<tr><td>s_sim[15]</td><td> 0.7555521</td><td> 0.7797795</td><td>0.1632866</td><td>0.1702054</td><td>  0.4528257</td><td> 0.9755237</td><td>0.9996543</td><td>3702.652</td><td>2749.965</td></tr>
	<tr><td>s_sim[16]</td><td> 0.7554666</td><td> 0.7803640</td><td>0.1629003</td><td>0.1675064</td><td>  0.4497360</td><td> 0.9738368</td><td>0.9997797</td><td>3369.579</td><td>3193.877</td></tr>
	<tr><td>s_sim[17]</td><td> 0.7496401</td><td> 0.7786345</td><td>0.1679984</td><td>0.1743945</td><td>  0.4295800</td><td> 0.9750243</td><td>1.0006391</td><td>3546.795</td><td>3577.849</td></tr>
	<tr><td>s_sim[18]</td><td> 0.7557703</td><td> 0.7809600</td><td>0.1658010</td><td>0.1700186</td><td>  0.4469792</td><td> 0.9739523</td><td>1.0006038</td><td>3835.557</td><td>3256.432</td></tr>
	<tr><td>s_sim[19]</td><td> 0.7559281</td><td> 0.7823020</td><td>0.1618966</td><td>0.1639392</td><td>  0.4468340</td><td> 0.9732376</td><td>0.9996622</td><td>3645.435</td><td>2824.582</td></tr>
	<tr><td>s_sim[20]</td><td> 0.7528602</td><td> 0.7790840</td><td>0.1680849</td><td>0.1709890</td><td>  0.4281760</td><td> 0.9750786</td><td>1.0001791</td><td>3651.577</td><td>3719.415</td></tr>
	<tr><td>s_sim[21]</td><td> 0.7523741</td><td> 0.7761915</td><td>0.1644295</td><td>0.1704575</td><td>  0.4476327</td><td> 0.9764495</td><td>0.9997132</td><td>3746.216</td><td>3333.132</td></tr>
	<tr><td>s_sim[22]</td><td> 0.7561313</td><td> 0.7855385</td><td>0.1638816</td><td>0.1694990</td><td>  0.4448916</td><td> 0.9734162</td><td>1.0009543</td><td>3417.160</td><td>2777.871</td></tr>
	<tr><td>s_sim[23]</td><td> 0.7499353</td><td> 0.7768145</td><td>0.1655774</td><td>0.1709453</td><td>  0.4405739</td><td> 0.9753409</td><td>1.0001462</td><td>3678.281</td><td>2928.156</td></tr>
	<tr><td>s_sim[24]</td><td> 0.7507685</td><td> 0.7770365</td><td>0.1643030</td><td>0.1680290</td><td>  0.4446655</td><td> 0.9708647</td><td>0.9996292</td><td>2999.935</td><td>3179.589</td></tr>
	<tr><td>s_sim[25]</td><td> 0.7539305</td><td> 0.7809975</td><td>0.1634029</td><td>0.1679719</td><td>  0.4425114</td><td> 0.9729435</td><td>1.0006023</td><td>3634.668</td><td>3420.166</td></tr>
	<tr><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td></tr>
	<tr><td>s_sim[71] </td><td>0.7523116</td><td>0.7806950</td><td>0.1657678</td><td>0.1687421</td><td>0.4386995</td><td>0.9737648</td><td>1.0013223</td><td>3680.581</td><td>2971.260</td></tr>
	<tr><td>s_sim[72] </td><td>0.7583762</td><td>0.7842995</td><td>0.1617939</td><td>0.1736006</td><td>0.4545544</td><td>0.9710739</td><td>0.9996976</td><td>3301.585</td><td>2840.791</td></tr>
	<tr><td>s_sim[73] </td><td>0.7556720</td><td>0.7820165</td><td>0.1627936</td><td>0.1684300</td><td>0.4478169</td><td>0.9726397</td><td>1.0012680</td><td>3499.080</td><td>3208.706</td></tr>
	<tr><td>s_sim[74] </td><td>0.7547181</td><td>0.7809220</td><td>0.1610201</td><td>0.1644411</td><td>0.4516467</td><td>0.9715066</td><td>1.0000198</td><td>3399.117</td><td>3014.405</td></tr>
	<tr><td>s_sim[75] </td><td>0.7533381</td><td>0.7742685</td><td>0.1628741</td><td>0.1689408</td><td>0.4496273</td><td>0.9764632</td><td>1.0006530</td><td>3359.687</td><td>3042.876</td></tr>
	<tr><td>s_sim[76] </td><td>0.7532482</td><td>0.7778980</td><td>0.1649907</td><td>0.1723345</td><td>0.4448392</td><td>0.9764751</td><td>1.0001158</td><td>3729.772</td><td>3561.618</td></tr>
	<tr><td>s_sim[77] </td><td>0.7540697</td><td>0.7776255</td><td>0.1620004</td><td>0.1687421</td><td>0.4493149</td><td>0.9748428</td><td>0.9999781</td><td>3709.743</td><td>2924.111</td></tr>
	<tr><td>s_sim[78] </td><td>0.7552318</td><td>0.7787180</td><td>0.1617609</td><td>0.1699089</td><td>0.4518985</td><td>0.9716803</td><td>1.0002355</td><td>3542.855</td><td>3354.554</td></tr>
	<tr><td>s_sim[79] </td><td>0.7513719</td><td>0.7772095</td><td>0.1658203</td><td>0.1766436</td><td>0.4388728</td><td>0.9748116</td><td>1.0006742</td><td>3688.171</td><td>3517.024</td></tr>
	<tr><td>s_sim[80] </td><td>0.7554185</td><td>0.7786930</td><td>0.1624798</td><td>0.1663314</td><td>0.4521462</td><td>0.9719680</td><td>1.0010131</td><td>3649.007</td><td>3431.718</td></tr>
	<tr><td>s_sim[81] </td><td>0.7529500</td><td>0.7810250</td><td>0.1663739</td><td>0.1738519</td><td>0.4480554</td><td>0.9728977</td><td>0.9997702</td><td>3675.678</td><td>3117.200</td></tr>
	<tr><td>s_sim[82] </td><td>0.7584932</td><td>0.7843625</td><td>0.1628715</td><td>0.1717866</td><td>0.4469598</td><td>0.9736029</td><td>1.0007292</td><td>3708.661</td><td>2922.429</td></tr>
	<tr><td>s_sim[83] </td><td>0.7551523</td><td>0.7812750</td><td>0.1621680</td><td>0.1705917</td><td>0.4538208</td><td>0.9739764</td><td>0.9998353</td><td>3542.688</td><td>3206.694</td></tr>
	<tr><td>s_sim[84] </td><td>0.7517418</td><td>0.7747835</td><td>0.1657026</td><td>0.1712974</td><td>0.4443958</td><td>0.9745813</td><td>1.0003951</td><td>3590.600</td><td>3007.862</td></tr>
	<tr><td>s_sim[85] </td><td>0.7546482</td><td>0.7788100</td><td>0.1613026</td><td>0.1697799</td><td>0.4558926</td><td>0.9730513</td><td>1.0003160</td><td>3801.188</td><td>3413.002</td></tr>
	<tr><td>s_sim[86] </td><td>0.7567569</td><td>0.7850845</td><td>0.1637229</td><td>0.1612750</td><td>0.4398513</td><td>0.9756185</td><td>1.0008255</td><td>3110.995</td><td>3298.655</td></tr>
	<tr><td>s_sim[87] </td><td>0.7539145</td><td>0.7805230</td><td>0.1656245</td><td>0.1711195</td><td>0.4407317</td><td>0.9758564</td><td>0.9999048</td><td>3385.537</td><td>3236.119</td></tr>
	<tr><td>s_sim[88] </td><td>0.7532113</td><td>0.7794330</td><td>0.1635724</td><td>0.1741670</td><td>0.4490222</td><td>0.9743499</td><td>1.0008099</td><td>3492.836</td><td>3293.382</td></tr>
	<tr><td>s_sim[89] </td><td>0.7517793</td><td>0.7806965</td><td>0.1663839</td><td>0.1742381</td><td>0.4344092</td><td>0.9739365</td><td>1.0005292</td><td>3617.638</td><td>3039.248</td></tr>
	<tr><td>s_sim[90] </td><td>0.7536933</td><td>0.7797350</td><td>0.1630973</td><td>0.1666465</td><td>0.4467467</td><td>0.9694501</td><td>0.9997169</td><td>3493.019</td><td>3535.025</td></tr>
	<tr><td>s_sim[91] </td><td>0.7573752</td><td>0.7821005</td><td>0.1613137</td><td>0.1701543</td><td>0.4571854</td><td>0.9733186</td><td>1.0001893</td><td>3728.733</td><td>2855.958</td></tr>
	<tr><td>s_sim[92] </td><td>0.7499069</td><td>0.7755345</td><td>0.1668960</td><td>0.1723574</td><td>0.4416318</td><td>0.9717048</td><td>1.0002116</td><td>3454.466</td><td>2728.611</td></tr>
	<tr><td>s_sim[93] </td><td>0.7544595</td><td>0.7786440</td><td>0.1623672</td><td>0.1724004</td><td>0.4516196</td><td>0.9726107</td><td>1.0008192</td><td>3533.927</td><td>3457.289</td></tr>
	<tr><td>s_sim[94] </td><td>0.7578421</td><td>0.7856785</td><td>0.1638296</td><td>0.1698348</td><td>0.4472335</td><td>0.9747376</td><td>0.9999161</td><td>3605.345</td><td>3350.634</td></tr>
	<tr><td>s_sim[95] </td><td>0.7530364</td><td>0.7766930</td><td>0.1627019</td><td>0.1702551</td><td>0.4503490</td><td>0.9751747</td><td>1.0001220</td><td>3690.476</td><td>2992.951</td></tr>
	<tr><td>s_sim[96] </td><td>0.7544495</td><td>0.7785435</td><td>0.1628462</td><td>0.1691906</td><td>0.4541267</td><td>0.9745491</td><td>0.9999704</td><td>3711.595</td><td>3040.620</td></tr>
	<tr><td>s_sim[97] </td><td>0.7531373</td><td>0.7830350</td><td>0.1628663</td><td>0.1649704</td><td>0.4441329</td><td>0.9745094</td><td>1.0005597</td><td>3653.499</td><td>3222.520</td></tr>
	<tr><td>s_sim[98] </td><td>0.7550406</td><td>0.7807990</td><td>0.1623796</td><td>0.1687466</td><td>0.4426782</td><td>0.9725074</td><td>0.9997867</td><td>3655.128</td><td>3620.627</td></tr>
	<tr><td>s_sim[99] </td><td>0.7545676</td><td>0.7812840</td><td>0.1648859</td><td>0.1710935</td><td>0.4401541</td><td>0.9733861</td><td>0.9995537</td><td>3310.877</td><td>3100.817</td></tr>
	<tr><td>s_sim[100]</td><td>0.7513484</td><td>0.7802295</td><td>0.1663923</td><td>0.1774435</td><td>0.4426189</td><td>0.9735879</td><td>1.0006365</td><td>3509.837</td><td>3482.959</td></tr>
</tbody>
</table>

From the above summary the values of the parameters `mu` and `nu` look correct, as do the values for the simulated student scores. The `rhat` for each parameter also looks good (close to 1) and the effective sample size (`ess_bulk`) is also good. There was a minor problem in the fitting where a nan value was generated, but that's a rare thing and only happens intermittently. Overall, this looks good! Now let's get the data.

```r
draws <- as_draws_matrix(student_score_pp_fit)
head(draws)
```

<table class="dataframe">
<caption>A draws_matrix: 6 × 105 of type dbl</caption>
<thead>
	<tr><th></th><th scope=col>lp__</th><th scope=col>mu</th><th scope=col>nu</th><th scope=col>a</th><th scope=col>b</th><th scope=col>s_sim[1]</th><th scope=col>s_sim[2]</th><th scope=col>s_sim[3]</th><th scope=col>s_sim[4]</th><th scope=col>s_sim[5]</th><th scope=col>⋯</th><th scope=col>s_sim[91]</th><th scope=col>s_sim[92]</th><th scope=col>s_sim[93]</th><th scope=col>s_sim[94]</th><th scope=col>s_sim[95]</th><th scope=col>s_sim[96]</th><th scope=col>s_sim[97]</th><th scope=col>s_sim[98]</th><th scope=col>s_sim[99]</th><th scope=col>s_sim[100]</th></tr>
</thead>
<tbody>
	<tr><th scope=row>1</th><td> -6.95483</td><td>0.667633</td><td> 9.97229</td><td>6.65783</td><td>3.314450</td><td>0.456435</td><td>0.664123</td><td>0.711574</td><td>0.447643</td><td>0.734297</td><td>⋯</td><td>0.498274</td><td>0.754939</td><td>0.726993</td><td>0.456323</td><td>0.703468</td><td>0.969384</td><td>0.719329</td><td>0.285399</td><td>0.578132</td><td>0.768713</td></tr>
	<tr><th scope=row>2</th><td> -8.32990</td><td>0.657733</td><td> 8.48227</td><td>5.57907</td><td>2.903200</td><td>0.768042</td><td>0.804358</td><td>0.498766</td><td>0.565657</td><td>0.611261</td><td>⋯</td><td>0.665832</td><td>0.934308</td><td>0.768160</td><td>0.528255</td><td>0.680999</td><td>0.446552</td><td>0.549291</td><td>0.703405</td><td>0.675308</td><td>0.620042</td></tr>
	<tr><th scope=row>3</th><td>-10.93100</td><td>0.944694</td><td> 8.70912</td><td>8.22745</td><td>0.481670</td><td>0.999742</td><td>0.956379</td><td>0.906580</td><td>0.895511</td><td>0.937207</td><td>⋯</td><td>0.991936</td><td>0.811721</td><td>0.989481</td><td>0.901462</td><td>0.982731</td><td>0.996148</td><td>0.797290</td><td>0.964812</td><td>0.756131</td><td>0.917414</td></tr>
	<tr><th scope=row>4</th><td> -7.77407</td><td>0.883106</td><td>10.01070</td><td>8.84047</td><td>1.170190</td><td>0.827503</td><td>0.868712</td><td>0.780807</td><td>0.922841</td><td>0.902845</td><td>⋯</td><td>0.725912</td><td>0.814534</td><td>0.861869</td><td>0.816770</td><td>0.909844</td><td>0.965625</td><td>0.880752</td><td>0.953130</td><td>0.911444</td><td>0.711088</td></tr>
	<tr><th scope=row>5</th><td> -8.18839</td><td>0.899799</td><td> 9.86949</td><td>8.88056</td><td>0.988932</td><td>0.982008</td><td>0.934849</td><td>0.971897</td><td>0.987508</td><td>0.929194</td><td>⋯</td><td>0.996558</td><td>0.889514</td><td>0.993364</td><td>0.945195</td><td>0.745194</td><td>0.865354</td><td>0.919428</td><td>0.896571</td><td>0.738742</td><td>0.974191</td></tr>
	<tr><th scope=row>6</th><td> -7.55440</td><td>0.646480</td><td>11.06220</td><td>7.15148</td><td>3.910700</td><td>0.676698</td><td>0.280590</td><td>0.649463</td><td>0.611321</td><td>0.680222</td><td>⋯</td><td>0.632214</td><td>0.426887</td><td>0.810964</td><td>0.408792</td><td>0.752207</td><td>0.704922</td><td>0.556105</td><td>0.785266</td><td>0.632428</td><td>0.470659</td></tr>
</tbody>
</table>

Now that we have the draws, let's plot a few different classes of 100 students (`s_sim`) to see what kind of variation the model is producing.

```r
set.seed(2024)
s_sim_draws <- draws[, grep('s_sim', colnames(draws))]
s_sim_means <- mean(apply(s_sim_draws, 2, mean))

p <- ggplot() +
    coord_cartesian(xlim = c(0, 1)) +
    geom_vline(data = data.frame(xintercept = s_sim_means), mapping = aes(xintercept=xintercept)) +
    labs(x = "Score", y = "Density") +
    scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +  # Set background to white
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )

for (row in sample(1:4000, size = 100)) {
    data <- data.frame(s = as.vector(s_sim_draws[row, ]))
    p <- p + geom_density(data = data, mapping = aes(s), colour = alpha('black', 0.1))
}

print(p)
```

![png](/2024-12-02-hierarchical-bayesian-models/output_25_0.png)

What we see here are the results of 100 randomly chosen simulated classes. This seems roughly reasonable to me - the mean is firmly centred around 75% and there's considerable variation. Looking at this, there is maybe a bit too much variation - I would expect almost all of the weight to be in the range 50% - 100%, and there are a few classes with a significant amount of weight below 50%. On the other hand, it's probably not the worst thing in the world for this to have too much variation - the data should be able to fix that.

Now let's actually train the model on some data and see what happens. We'll have to slightly modify the model we used for our prior predictive check to incorporate the data, but otherwise it will look very similar.

```r
student_score_model_code <- "
data {
    int<lower = 0> N; // number of students
    vector[N] s; // student scores
}
parameters {
    real<lower = 0, upper = 1> mu;
    real<lower = 0> nu;
}
 transformed parameters {
    real<lower = 0> a = mu * nu;
    real<lower = 0> b = (1 - mu) * nu;
}
model {
    s ~ beta(a, b);
    mu ~ beta(12, 4);
    nu ~ normal(10, 1);
}
"

student_score_model_file <- write_stan_file(student_score_model_code)
student_score_model <- cmdstan_model(student_score_model_file)

student_score_model_data <- list(
    N = NUM_STUDENTS,
    s = actual_student_scores
)
student_score_fit <- student_score_model$sample(
    data = student_score_model_data,
    chains = 4
)
student_score_fit$summary()
```

    Running MCMC with 4 sequential chains...

    All 4 chains finished successfully.
    Mean chain execution time: 0.0 seconds.
    Total execution time: 0.6 seconds.

<table class="dataframe">
<caption>A draws_summary: 5 × 10</caption>
<thead>
	<tr><th scope=col>variable</th><th scope=col>mean</th><th scope=col>median</th><th scope=col>sd</th><th scope=col>mad</th><th scope=col>q5</th><th scope=col>q95</th><th scope=col>rhat</th><th scope=col>ess_bulk</th><th scope=col>ess_tail</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>lp__</td><td>7.9908730</td><td>8.3131950</td><td>0.9971564</td><td>0.70121791</td><td>5.9504810</td><td> 8.9398085</td><td>1.001998</td><td>1874.212</td><td>2717.678</td></tr>
	<tr><td>mu  </td><td>0.8019337</td><td>0.8031015</td><td>0.0247588</td><td>0.02413969</td><td>0.7597064</td><td> 0.8411199</td><td>1.000958</td><td>2543.792</td><td>2389.431</td></tr>
	<tr><td>nu  </td><td>9.9267693</td><td>9.9146750</td><td>0.9365335</td><td>0.93079852</td><td>8.4171405</td><td>11.4982400</td><td>1.000450</td><td>3232.958</td><td>2479.932</td></tr>
	<tr><td>a   </td><td>7.9625121</td><td>7.9612550</td><td>0.8081238</td><td>0.81650489</td><td>6.6524980</td><td> 9.3088245</td><td>0.999826</td><td>3037.912</td><td>2657.738</td></tr>
	<tr><td>b   </td><td>1.9642571</td><td>1.9528450</td><td>0.2943620</td><td>0.29113816</td><td>1.4906390</td><td> 2.4721195</td><td>1.001831</td><td>3197.077</td><td>2450.331</td></tr>
</tbody>
</table>

```r
draws <- as_draws_matrix(student_score_fit)

# mu
ggplot(data.frame(mu = draws[, 'mu'])) +
    geom_density(aes( mu )) +
    geom_vline(aes(xintercept = 0.75)) +
    coord_cartesian(xlim = c(0, 1)) +
    labs(x = "mu", y = "Density") +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +  # Set background to white
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )

# nu
ggplot(data.frame(nu = draws[, 'nu'])) +
    geom_density(aes(nu)) +
    geom_vline(aes(xintercept = 10)) +
    labs(x = "nu", y = "Density") +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +  # Set background to white
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_28_0.png)

![png](/2024-12-02-hierarchical-bayesian-models/output_28_1.png)

Great! So this model seems to be doing a good job of recovering the actual values. Now that we have some confidence in this part of the model, let's extend it a bit more to consider the situation of different schools, each with their own means, which now influence the scores of their students. We'll assume that the schools each draw their means from a single beta distribution, and we'll also assument that each student draws their score from a beta distribution whose mean is the school mean.

```r
set.seed(1234)
NUM_SCHOOLS <- 5
school_mu <- 0.75
school_nu <- 50

school_alpha <- school_mu * school_nu
school_beta <- (1 - school_mu) * school_nu

school_means <- rbeta(NUM_SCHOOLS, school_alpha, school_beta)

ps <- seq(from = 0, to = 1, length.out = 100)
density <- dbeta(ps, school_alpha, school_beta)
ggplot() +
    geom_line(data = data.frame(p = ps, density = density), mapping = aes(p, density)) +
    geom_point(data = data.frame(p = school_means, density = dbeta(school_means, school_alpha, school_beta)), mapping = aes(p, density)) +
    labs(x = "School-Specific Mean", y = "Density") +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +  # Set background to white
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_30_0.png)

Now we'll simulate some students for each of these schools.

```r
STUDENT_NU <- 30

student_alpha <- school_means * STUDENT_NU
student_beta <- (1 - school_means) * STUDENT_NU

ps <- seq(from = 0, to = 1, length.out = 100)
plot_df <- data.frame(p = numeric(), density = numeric(), school = integer())
for (school_id in 1:NUM_SCHOOLS) {
    alpha <- student_alpha[school_id]
    beta <- student_beta[school_id]
    school_data <- data.frame(
        p = ps,
        density = dbeta(ps, alpha, beta),
        school = school_id
    )
    plot_df <- rbind(plot_df, school_data)
}
plot_df$school <- as.factor(plot_df$school)

ggplot(plot_df, aes(p, density, group = school, colour = school)) +
    geom_line() +
    labs(x = "p", y = 'Density', colour = "School") +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +  # Set background to white
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_32_0.png)

Here we can see the distribution of scores from which each student will draw their scores.

```r
set.seed(1234)
STUDENTS_PER_SCHOOL <- 20
student_scores <- data.frame(s = numeric(), school = integer())

for (school in 1:NUM_SCHOOLS) {
    alpha <- student_alpha[school]
    beta <- student_beta[school]
    school_data <- data.frame(
        s = rbeta(STUDENTS_PER_SCHOOL, alpha, beta),
        school = school
    )
    student_scores <- rbind(student_scores, school_data)
}
student_scores$school <- as.factor(student_scores$school)

ggplot(student_scores, aes(s, colour = school, group = school)) +
    geom_density() +
    coord_cartesian(xlim = c(0, 1)) +
    labs(x = 'Score', y = 'Density', colour = "School") +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_34_0.png)

```r
plot_df <- data.frame(true_mean = numeric(), empirical_mean = numeric())
for (school_id in 1:NUM_SCHOOLS) {
    school_data <- student_scores[student_scores$school == school_id, ]
    plot_df <- rbind(plot_df, data.frame(true_mean = school_means[school_id], empirical_mean = mean(school_data$s)))
}

empirical_school_means <- plot_df$empirical_mean

ggplot(plot_df, aes(true_mean, empirical_mean)) +
    geom_point() +
    geom_abline(intercept = 0, slope = 1, linetype = 'dashed') +
    labs(x = "True Mean", y = "Empirical Mean") +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )

```

![png](/2024-12-02-hierarchical-bayesian-models/output_35_0.png)

First, let's run an unpooled model - that is, one where we estimate each school's values separately. That model looks like

$$
\begin{align*}
\text{s} &\sim \text{Beta}(\alpha[\text{school}], \beta[\text{school}]) \\
\alpha[\text{school}] &= \mu[\text{school}] * \nu[\text{school}] \\
\beta[\text{school}] &= (1 - \mu[\text{school}]) * \nu[\text{school}] \\
\mu[\text{school}] &\sim \text{Beta}(3, 1) \\
\nu[\text{school}] &\sim \text{Normal}(10, 1) \\
\end{align*}
$$

```r
student_school_unpooled_model_code <- "
data {
    int<lower = 0> N_students; // number of students
    int<lower = 0> N_schools; // number of schools
    vector[N_students] s; // student scores
    array[N_students] int school_id; // the school id for each student
}
parameters {
    array[N_schools] real<lower = 0, upper = 1> mu_school;
    array[N_schools] real<lower = 0> nu_school;
}
 transformed parameters {
    array[N_schools] real<lower = 0> a_school;
    array[N_schools] real<lower = 0> b_school;
    for (i in 1:N_schools) {
        a_school[i] = mu_school[i] * nu_school[i];
        b_school[i] = (1 - mu_school[i]) * nu_school[i];
    }
}
model {
    for (student_index in 1:N_students) {
        s[student_index] ~ beta(a_school[school_id[student_index]], b_school[school_id[student_index]]);
    }
    mu_school ~ beta(3, 1);
    nu_school ~ normal(30, 4);
}
"

student_school_unpooled_model_file <- write_stan_file(student_school_unpooled_model_code)
student_school_unpooled_model <- cmdstan_model(student_school_unpooled_model_file)

student_school_model_data <- list(
    N_students = nrow(student_scores),
    N_schools = NUM_SCHOOLS,
    s = student_scores$s,
    school_id = as.integer(student_scores$school)
)
student_school_unpooled_fit <- student_school_unpooled_model$sample(
    data = student_school_model_data,
    chains = 4
)
student_school_unpooled_fit$summary()
```

    Running MCMC with 4 sequential chains...

    All 4 chains finished successfully.
    Mean chain execution time: 0.2 seconds.
    Total execution time: 0.9 seconds.

<table class="dataframe">
<caption>A draws_summary: 21 × 10</caption>
<thead>
	<tr><th scope=col>variable</th><th scope=col>mean</th><th scope=col>median</th><th scope=col>sd</th><th scope=col>mad</th><th scope=col>q5</th><th scope=col>q95</th><th scope=col>rhat</th><th scope=col>ess_bulk</th><th scope=col>ess_tail</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>lp__        </td><td>133.2063127</td><td>133.5330000</td><td>2.28559835</td><td>2.11715280</td><td>128.9039000</td><td>136.2762000</td><td>1.0005406</td><td>1383.865</td><td>2676.246</td></tr>
	<tr><td>mu_school[1]</td><td>  0.8466306</td><td>  0.8467865</td><td>0.01451341</td><td>0.01407951</td><td>  0.8222164</td><td>  0.8700590</td><td>1.0012989</td><td>9296.896</td><td>2773.345</td></tr>
	<tr><td>mu_school[2]</td><td>  0.7631883</td><td>  0.7633160</td><td>0.01666534</td><td>0.01648503</td><td>  0.7358237</td><td>  0.7897457</td><td>1.0000816</td><td>7172.713</td><td>2855.873</td></tr>
	<tr><td>mu_school[3]</td><td>  0.6985636</td><td>  0.6984615</td><td>0.01903218</td><td>0.01865037</td><td>  0.6669859</td><td>  0.7296387</td><td>1.0027091</td><td>7569.557</td><td>2383.093</td></tr>
	<tr><td>mu_school[4]</td><td>  0.8986209</td><td>  0.8987715</td><td>0.01110209</td><td>0.01102758</td><td>  0.8803896</td><td>  0.9161687</td><td>1.0006262</td><td>6881.045</td><td>2579.987</td></tr>
	<tr><td>mu_school[5]</td><td>  0.7082870</td><td>  0.7088845</td><td>0.01838196</td><td>0.01870893</td><td>  0.6780569</td><td>  0.7377980</td><td>1.0002342</td><td>8158.005</td><td>2954.655</td></tr>
	<tr><td>nu_school[1]</td><td> 30.5954286</td><td> 30.5384500</td><td>3.60381506</td><td>3.63333369</td><td> 24.7442450</td><td> 36.6404500</td><td>1.0011241</td><td>6743.832</td><td>2632.137</td></tr>
	<tr><td>nu_school[2]</td><td> 30.3578492</td><td> 30.3070000</td><td>3.71383749</td><td>3.70813086</td><td> 24.3044150</td><td> 36.6859250</td><td>1.0022297</td><td>8089.165</td><td>2602.090</td></tr>
	<tr><td>nu_school[3]</td><td> 28.9024282</td><td> 28.8947500</td><td>3.59228813</td><td>3.67084347</td><td> 22.9660100</td><td> 34.8531500</td><td>1.0014781</td><td>7393.074</td><td>2979.367</td></tr>
	<tr><td>nu_school[4]</td><td> 32.0602813</td><td> 32.0718500</td><td>3.67326279</td><td>3.72807183</td><td> 26.0406500</td><td> 38.0546350</td><td>1.0018923</td><td>7189.690</td><td>2859.561</td></tr>
	<tr><td>nu_school[5]</td><td> 30.7457093</td><td> 30.6825500</td><td>3.78388583</td><td>3.78374346</td><td> 24.5528400</td><td> 37.0404800</td><td>1.0004906</td><td>7702.508</td><td>2870.507</td></tr>
	<tr><td>a_school[1] </td><td> 25.9068463</td><td> 25.8534500</td><td>3.11506217</td><td>3.11612868</td><td> 20.8941350</td><td> 31.2008100</td><td>1.0008923</td><td>6732.695</td><td>2500.360</td></tr>
	<tr><td>a_school[2] </td><td> 23.1730379</td><td> 23.1326500</td><td>2.91251817</td><td>2.86645884</td><td> 18.5673600</td><td> 28.0946000</td><td>1.0028086</td><td>7867.279</td><td>2794.205</td></tr>
	<tr><td>a_school[3] </td><td> 20.1909199</td><td> 20.2093000</td><td>2.57330288</td><td>2.56801146</td><td> 15.9950150</td><td> 24.4977450</td><td>1.0010490</td><td>7449.585</td><td>2740.689</td></tr>
	<tr><td>a_school[4] </td><td> 28.8145096</td><td> 28.8517000</td><td>3.35774104</td><td>3.36780003</td><td> 23.3074450</td><td> 34.2775750</td><td>1.0015005</td><td>7155.198</td><td>2752.986</td></tr>
	<tr><td>a_school[5] </td><td> 21.7806440</td><td> 21.6924500</td><td>2.76944387</td><td>2.74147566</td><td> 17.2344200</td><td> 26.5064300</td><td>1.0012976</td><td>7711.507</td><td>3129.558</td></tr>
	<tr><td>b_school[1] </td><td>  4.6885823</td><td>  4.6692700</td><td>0.68187457</td><td>0.69292276</td><td>  3.5813565</td><td>  5.8415735</td><td>0.9999706</td><td>8123.741</td><td>2632.944</td></tr>
	<tr><td>b_school[2] </td><td>  7.1848123</td><td>  7.1599950</td><td>0.98184417</td><td>1.00975438</td><td>  5.6196490</td><td>  8.8247815</td><td>1.0013434</td><td>8428.792</td><td>2801.349</td></tr>
	<tr><td>b_school[3] </td><td>  8.7115083</td><td>  8.6948950</td><td>1.20813189</td><td>1.27687442</td><td>  6.7770070</td><td> 10.7226350</td><td>1.0012211</td><td>7377.469</td><td>2786.540</td></tr>
	<tr><td>b_school[4] </td><td>  3.2457709</td><td>  3.2309500</td><td>0.48446246</td><td>0.49350565</td><td>  2.4725655</td><td>  4.0622545</td><td>1.0008731</td><td>7247.993</td><td>2369.960</td></tr>
	<tr><td>b_school[5] </td><td>  8.9650650</td><td>  8.9528950</td><td>1.20969315</td><td>1.20415289</td><td>  6.9710085</td><td> 11.0267150</td><td>1.0012507</td><td>7371.608</td><td>2881.813</td></tr>
</tbody>
</table>

```r
unpooled_student_school_draws <- as_draws_matrix(student_school_unpooled_fit$draws())
```

```r
# school means
unpooled_school_means_draws <- unpooled_student_school_draws[, grep('mu_school', colnames(unpooled_student_school_draws))]
unpooled_school_mean_means <- apply(unpooled_school_means_draws, 2, mean)
unpooled_school_mean_lower <- apply(unpooled_school_means_draws, 2, function(col) quantile(col, 0.025))
unpooled_school_mean_upper <- apply(unpooled_school_means_draws, 2, function(col) quantile(col, 0.975))

unpooled_means_plot_df <- data.frame(school = 1:NUM_SCHOOLS, mean = unpooled_school_mean_means, lower = unpooled_school_mean_lower, upper = unpooled_school_mean_upper)

unpooled_school_means_plot <- ggplot() +
    geom_errorbar(data = unpooled_means_plot_df, mapping = aes(school, ymin = lower, ymax = upper)) +
    geom_point(data = unpooled_means_plot_df, aes(school, mean)) +
    geom_point(data = data.frame(school = 1:NUM_SCHOOLS, mean = school_means), mapping = aes(school, mean, colour = "True Mean")) +
    geom_point(data = data.frame(school = 1:NUM_SCHOOLS, mean = empirical_school_means), mapping = aes(school, mean, colour = 'Empirical Mean')) +
    labs(x = "School", y = "Mean Score", colour = "Type") +
    scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
print(unpooled_school_means_plot)
```

![png](/2024-12-02-hierarchical-bayesian-models/output_39_0.png)

This looks pretty good! We're doing a good job of recovering these values. Now let's share information among the schools by using a hierarchical model.

We'll use the following model to recover the values.

$$
\begin{align*}
\text{s} &\sim \text{Beta}(\alpha[\text{school}], \beta[\text{school}]) \\
\alpha[\text{school}] &= \mu[\text{school}] * \nu[\text{school}] \\
\beta[\text{school}] &= (1 - \mu[\text{school}]) * \nu[\text{school}] \\
\mu[\text{school}] &\sim \text{Beta}(\bar\alpha, \bar\beta) \\
\nu[\text{school}] &\sim \text{Normal}(\bar\nu, \sigma_\nu) \\
\bar\alpha &\sim \text{Normal}(3, 0.5) \\
\bar\beta &\sim \text{Normal}(1, 0.3) \\
\bar\nu &\sim \text{Normal}(30, 5) \\
\sigma_\nu &\sim \text{Exponential}(1) \\
\end{align*}
$$

```r

student_school_model_code <- "
data {
    int<lower = 0> N_students; // number of students
    int<lower = 0> N_schools; // number of schools
    vector[N_students] s; // student scores
    array[N_students] int school_id; // the school id for each student
}
parameters {
    array[N_schools] real<lower = 0, upper = 1> mu_school;
    array[N_schools] real<lower = 0> nu_school_raw; // non-centred parameterization; implies nu_school ~ normal(nu_bar, sigma_bar)
    real<lower = 0> alpha_bar;
    real<lower = 0> beta_bar;
    real<lower = 0> nu_bar;
    real<lower = 0> sigma_nu;
}
 transformed parameters {
    array[N_schools] real<lower = 0> nu_school;
    array[N_schools] real<lower = 0> a_school;
    array[N_schools] real<lower = 0> b_school;
    for (i in 1:N_schools) {
        nu_school[i] = nu_bar + sigma_nu * nu_school_raw[i];
        a_school[i] = mu_school[i] * nu_school[i];
        b_school[i] = (1 - mu_school[i]) * nu_school[i];
    }
}
model {
    for (student_index in 1:N_students) {
        s[student_index] ~ beta(a_school[school_id[student_index]], b_school[school_id[student_index]]);
    }
    mu_school ~ beta(alpha_bar, beta_bar);
    nu_school_raw ~ std_normal();
    alpha_bar ~ normal(3, 0.5);
    beta_bar ~ normal(1, 0.3);
    nu_bar ~ normal(30, 5);
    sigma_nu ~ exponential(1);
}
"

student_school_model_file <- write_stan_file(student_school_model_code)
student_school_model <- cmdstan_model(student_school_model_file)

student_school_fit <- student_school_model$sample(
    data = student_school_model_data,
    chains = 4,
    iter_warmup = 1000,
    adapt_delta = 0.95
)
student_school_fit$summary()
```

    Running MCMC with 4 sequential chains...

    All 4 chains finished successfully.
    Mean chain execution time: 0.4 seconds.
    Total execution time: 1.9 seconds.

<table class="dataframe">
<caption>A draws_summary: 30 × 10</caption>
<thead>
	<tr><th scope=col>variable</th><th scope=col>mean</th><th scope=col>median</th><th scope=col>sd</th><th scope=col>mad</th><th scope=col>q5</th><th scope=col>q95</th><th scope=col>rhat</th><th scope=col>ess_bulk</th><th scope=col>ess_tail</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>lp__            </td><td>120.2997945</td><td>120.6395000</td><td>2.88945094</td><td>2.76875550</td><td>114.91420000</td><td>124.4150000</td><td>1.0048682</td><td>1490.839</td><td>2390.733</td></tr>
	<tr><td>mu_school[1]    </td><td>  0.8470211</td><td>  0.8472085</td><td>0.01358558</td><td>0.01298165</td><td>  0.82471955</td><td>  0.8688271</td><td>1.0010532</td><td>5050.164</td><td>2470.032</td></tr>
	<tr><td>mu_school[2]    </td><td>  0.7638199</td><td>  0.7639385</td><td>0.01594188</td><td>0.01603803</td><td>  0.73703180</td><td>  0.7900103</td><td>1.0010624</td><td>5844.673</td><td>3214.262</td></tr>
	<tr><td>mu_school[3]    </td><td>  0.6989982</td><td>  0.6991170</td><td>0.01758573</td><td>0.01766592</td><td>  0.67012455</td><td>  0.7275320</td><td>1.0017414</td><td>5188.370</td><td>3085.584</td></tr>
	<tr><td>mu_school[4]    </td><td>  0.8983489</td><td>  0.8985485</td><td>0.01102625</td><td>0.01115063</td><td>  0.88029595</td><td>  0.9159538</td><td>1.0025573</td><td>5146.175</td><td>3025.248</td></tr>
	<tr><td>mu_school[5]    </td><td>  0.7082870</td><td>  0.7083660</td><td>0.01716313</td><td>0.01705657</td><td>  0.67989185</td><td>  0.7368971</td><td>0.9997209</td><td>5376.621</td><td>3100.150</td></tr>
	<tr><td>nu_school_raw[1]</td><td>  0.8128569</td><td>  0.6926650</td><td>0.61102128</td><td>0.60914400</td><td>  0.07260510</td><td>  1.9961565</td><td>1.0004995</td><td>3516.625</td><td>1721.888</td></tr>
	<tr><td>nu_school_raw[2]</td><td>  0.7895747</td><td>  0.6723220</td><td>0.60165921</td><td>0.59760344</td><td>  0.05733236</td><td>  1.9660335</td><td>1.0005797</td><td>3220.242</td><td>1853.584</td></tr>
	<tr><td>nu_school_raw[3]</td><td>  0.7553973</td><td>  0.6324210</td><td>0.58797066</td><td>0.56209072</td><td>  0.05570231</td><td>  1.9002925</td><td>1.0004686</td><td>2797.938</td><td>1643.460</td></tr>
	<tr><td>nu_school_raw[4]</td><td>  0.8333840</td><td>  0.7106100</td><td>0.62189482</td><td>0.62426430</td><td>  0.05943881</td><td>  2.0247330</td><td>0.9998461</td><td>2781.631</td><td>1139.225</td></tr>
	<tr><td>nu_school_raw[5]</td><td>  0.8048431</td><td>  0.6786530</td><td>0.61165042</td><td>0.60419731</td><td>  0.06066773</td><td>  2.0173890</td><td>1.0009278</td><td>2768.546</td><td>1470.845</td></tr>
	<tr><td>alpha_bar       </td><td>  3.1320128</td><td>  3.1337150</td><td>0.46785786</td><td>0.47165954</td><td>  2.35937800</td><td>  3.8970855</td><td>1.0019146</td><td>5119.352</td><td>2751.850</td></tr>
	<tr><td>beta_bar        </td><td>  1.0907279</td><td>  1.0844350</td><td>0.24464134</td><td>0.24603302</td><td>  0.69713060</td><td>  1.5043975</td><td>1.0009313</td><td>5496.958</td><td>2344.933</td></tr>
	<tr><td>nu_bar          </td><td> 31.5787906</td><td> 31.5582500</td><td>3.37920085</td><td>3.41346411</td><td> 26.21277500</td><td> 37.1670300</td><td>1.0003554</td><td>4995.001</td><td>3090.744</td></tr>
	<tr><td>sigma_nu        </td><td>  1.0272002</td><td>  0.7143280</td><td>1.02022647</td><td>0.73669653</td><td>  0.05808706</td><td>  3.0601565</td><td>1.0002520</td><td>4038.993</td><td>2059.170</td></tr>
	<tr><td>nu_school[1]    </td><td> 32.4157204</td><td> 32.3271500</td><td>3.43742095</td><td>3.45297540</td><td> 26.91420000</td><td> 38.1362350</td><td>1.0009389</td><td>4991.626</td><td>3188.874</td></tr>
	<tr><td>nu_school[2]    </td><td> 32.3700213</td><td> 32.2914000</td><td>3.43706176</td><td>3.44141112</td><td> 26.87087000</td><td> 38.0587250</td><td>1.0006216</td><td>5166.621</td><td>3033.495</td></tr>
	<tr><td>nu_school[3]    </td><td> 32.3245989</td><td> 32.2764500</td><td>3.42172188</td><td>3.45601473</td><td> 26.84857000</td><td> 38.0114750</td><td>1.0005946</td><td>5223.580</td><td>3131.844</td></tr>
	<tr><td>nu_school[4]    </td><td> 32.4816132</td><td> 32.4246500</td><td>3.47454623</td><td>3.44066982</td><td> 26.96652500</td><td> 38.3314700</td><td>1.0007982</td><td>5070.896</td><td>3205.803</td></tr>
	<tr><td>nu_school[5]    </td><td> 32.3932509</td><td> 32.2758500</td><td>3.43845039</td><td>3.44600718</td><td> 26.99057000</td><td> 38.1477100</td><td>1.0007019</td><td>5338.495</td><td>3007.364</td></tr>
	<tr><td>a_school[1]     </td><td> 27.4618737</td><td> 27.3681500</td><td>2.99122402</td><td>2.98136034</td><td> 22.71480500</td><td> 32.3846850</td><td>1.0005317</td><td>4961.919</td><td>3132.647</td></tr>
	<tr><td>a_school[2]     </td><td> 24.7285854</td><td> 24.6540000</td><td>2.70788908</td><td>2.68691598</td><td> 20.37299000</td><td> 29.2811650</td><td>1.0002278</td><td>5146.804</td><td>3083.624</td></tr>
	<tr><td>a_school[3]     </td><td> 22.5988739</td><td> 22.5553500</td><td>2.49258392</td><td>2.49840339</td><td> 18.63084000</td><td> 26.8150650</td><td>1.0001400</td><td>5127.857</td><td>3115.493</td></tr>
	<tr><td>a_school[4]     </td><td> 29.1838142</td><td> 29.0871500</td><td>3.17859264</td><td>3.14333439</td><td> 24.18315500</td><td> 34.4842300</td><td>1.0010808</td><td>4943.275</td><td>3131.463</td></tr>
	<tr><td>a_school[5]     </td><td> 22.9453409</td><td> 22.8683500</td><td>2.51432791</td><td>2.52901908</td><td> 19.04795500</td><td> 27.2467150</td><td>1.0001032</td><td>5396.115</td><td>3104.879</td></tr>
	<tr><td>b_school[1]     </td><td>  4.9538464</td><td>  4.9310000</td><td>0.64619137</td><td>0.64508667</td><td>  3.93117700</td><td>  6.0525920</td><td>1.0019177</td><td>5480.992</td><td>3080.917</td></tr>
	<tr><td>b_school[2]     </td><td>  7.6414370</td><td>  7.6174150</td><td>0.93165746</td><td>0.91027192</td><td>  6.15480500</td><td>  9.2250720</td><td>1.0012027</td><td>5484.039</td><td>3014.747</td></tr>
	<tr><td>b_school[3]     </td><td>  9.7257252</td><td>  9.6761700</td><td>1.14435871</td><td>1.16653192</td><td>  7.94368300</td><td> 11.6919750</td><td>1.0018870</td><td>5549.259</td><td>2891.207</td></tr>
	<tr><td>b_school[4]     </td><td>  3.2977995</td><td>  3.2701050</td><td>0.47490024</td><td>0.46661129</td><td>  2.53166850</td><td>  4.1071670</td><td>1.0008953</td><td>5902.171</td><td>2746.835</td></tr>
	<tr><td>b_school[5]     </td><td>  9.4479103</td><td>  9.4035900</td><td>1.13083864</td><td>1.13598295</td><td>  7.68017550</td><td> 11.3531550</td><td>1.0005881</td><td>5082.952</td><td>3188.104</td></tr>
</tbody>
</table>

```r
student_school_draws <- as_draws_matrix(student_school_fit$draws())
```

```r
# # school means
school_means_draws <- student_school_draws[, grep('mu_school', colnames(student_school_draws))]
school_mean_means <- apply(school_means_draws, 2, mean)
school_mean_lower <- apply(school_means_draws, 2, function(col) quantile(col, 0.025))
school_mean_upper <- apply(school_means_draws, 2, function(col) quantile(col, 0.975))

means_plot_df <- data.frame(school = 1:NUM_SCHOOLS, mean = school_mean_means, lower = school_mean_lower, upper = school_mean_upper)

prior_mean <- mean(student_school_draws[, 'alpha_bar'] / (student_school_draws[, 'alpha_bar'] + student_school_draws[, 'beta_bar']))

pooled_school_means_plot <- ggplot() +
    geom_errorbar(data = means_plot_df, mapping = aes(school, ymin = lower, ymax = upper)) +
    geom_point(data = means_plot_df, aes(school, mean)) +
    geom_point(data = data.frame(school = 1:NUM_SCHOOLS, mean = school_means), mapping = aes(school, mean, colour = 'True Mean')) +
    geom_point(data = data.frame(school = 1:NUM_SCHOOLS, mean = unpooled_school_mean_means), aes(school, mean, colour = "Unpooled Mean")) +
    geom_hline(mapping = aes(yintercept = prior_mean), linetype = 'dashed') +
    labs(x = "School", y = "Value", colour = "Mean Type") +
    scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
print(pooled_school_means_plot)
```

![png](/2024-12-02-hierarchical-bayesian-models/output_43_0.png)

So as we can see, pooling didn't have too much of an effect; there's a minimal change from the pooled mean (black) and the unpooled mean (blue).

Now we're ready to tackle a more complex hierarchical model with multiple layers! To start off, let's say we have some districts. Each district will have some schools, and each school will have some students. Each of the students will have a score that is the school mean plus some standard deviation, drawn from a beta distribution. In turn, each of the school means for a district will be drawn from the same distribution. Finally, each of the district means will be drawn from a different shared distribution.

```r
set.seed(1234)

NUM_DISTRICTS <- 3
SCHOOLS_PER_DISTRICT <- 3
TOTAL_SCHOOLS <- NUM_DISTRICTS * SCHOOLS_PER_DISTRICT
STUDENTS_PER_SCHOOL <- 20
TOTAL_STUDENTS <- TOTAL_SCHOOLS * STUDENTS_PER_SCHOOL

district_mu <- 0.75
district_nu <- 30
district_alpha <- district_mu * district_nu
district_beta <- (1 - district_mu) * district_nu

district_means <- rbeta(NUM_DISTRICTS, district_alpha, district_beta)
ps <- seq(from = 0, to = 1, length.out = 100)
district_distribution_df <- data.frame(
    p = ps,
    density = dbeta(ps, district_alpha, district_beta)
)
districts_df <- data.frame(
    p = district_means,
    density = dbeta(district_means, district_alpha, district_beta)
)
ggplot(NULL, aes(p, density)) +
    geom_line(data = district_distribution_df) +
    geom_point(data = districts_df) +
    labs(x = "p", y = "Density") +
    scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_46_0.png)

So now we have the district means coming from a single distribution. Within that, each district will have schools, each of whose means comes from a distribution whose mean is the district mean!

```r
set.seed(2024)
ps <- seq(from = 0, to = 1, length.out = 1e3)
school_params <- data.frame(district = integer(), school_id = integer(), school_mu = numeric())
district_nu <- 40
for (district_id in 1:NUM_DISTRICTS) {
    district_mu <- district_means[district_id]
    district_alpha <- district_mu * district_nu
    district_beta <- (1 - district_mu) * district_nu
    school_data <- data.frame(
        district = rep(district_id, SCHOOLS_PER_DISTRICT),
        school_id = district_id + 1:SCHOOLS_PER_DISTRICT,
        school_mu = rbeta(SCHOOLS_PER_DISTRICT, district_alpha, district_beta)
    )
    school_params <- rbind(school_params, school_data)

    district_distribution_df <- data.frame(p = ps, density = dbeta(ps, district_alpha, district_beta))
    school_means_df <- data.frame(p = school_data$school_mu, density = dbeta(school_data$school_mu, district_alpha, district_beta))
    school_plot <- ggplot(NULL, aes(p, density)) +
        geom_line(data = district_distribution_df) +
        geom_point(data = school_means_df) +
        labs(x = "p", y = "Density", title = paste("Distribution and school means for district ", district_id)) +
        scale_x_continuous(labels = scales::percent_format(accuracy = 1)) +
        theme_bw() +
        theme(
            panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
        )
    print(school_plot)
}
```

![png](/2024-12-02-hierarchical-bayesian-models/output_48_0.png)

![png](/2024-12-02-hierarchical-bayesian-models/output_48_1.png)

![png](/2024-12-02-hierarchical-bayesian-models/output_48_2.png)

Now that we have the school information, we can generate a simulated group of students for each school. Each student will draw their score from a distribution whose mean is the school mean.

```r
set.seed(2024)
ps <- seq(from = 0, to = 1, length.out = 1e3)
student_data <- data.frame(district_id = integer(), school_id = integer(), score = numeric())
student_nu <- 30
for (school_id in 1:TOTAL_SCHOOLS) {
    district_id <- school_params[school_id, 'district']
    school_mu <- school_params[school_id, 'school_mu']
    student_alpha <- school_mu * student_nu
    student_beta <- (1 - school_mu) * student_nu
    school_scores <- data.frame(
        district_id = rep(district_id, STUDENTS_PER_SCHOOL),
        school_id <- rep(school_id, STUDENTS_PER_SCHOOL),
        score = rbeta(STUDENTS_PER_SCHOOL, student_alpha, student_beta)
    )
    student_data <- rbind(student_data, school_scores)
}
student_data$student_id <- as.factor(seq_len(nrow(student_data)))
student_data$school_id <- as.factor(student_data$school_id)
student_data$district_id <- as.factor(student_data$district_id)

student_plot <- ggplot(student_data, aes(student_id, score)) +
    geom_point(aes(colour = school_id, shape = district_id)) +
    labs(x = "Student", y = "Score", colour = "School", shape = "District") +
    scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +  # Set background to white
    theme(
        panel.grid.major.x = element_blank(),
        panel.grid.minor.x = element_blank(),
        panel.grid.major.y = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
        axis.ticks.x = element_blank(),
        axis.text.x = element_blank(),
    )
for (district_id in 1:(NUM_DISTRICTS - 1)) {
    print(district_id)
    student_plot <- student_plot +
        geom_vline(xintercept = SCHOOLS_PER_DISTRICT * STUDENTS_PER_SCHOOL * district_id + 0.5)
}
print(student_plot)
```

    [1] 1
    [1] 2

![png](/2024-12-02-hierarchical-bayesian-models/output_50_1.png)

Great! Now that we have the data and a good handle on the generation process, let's look what this looks like as a model. Again, there are a few levels here. There will be a shared district-level set of parameters as well as a shared school-level set of parameters influenced by the district. The student will in turn have their own parameters, again inheriting from the school parameters. There's a lot here, but let's see what it looks like in Stan!

```r

# NB: this is the non-centred parameterization to avoid divergent transitions
student_school_district_model_code <- "
data {
    int<lower = 0> N_students; // number of students
    int<lower = 0> N_schools; // number of schools
    int<lower = 0> N_districts; // number of districts
    vector[N_students] s; // student scores
    array[N_students] int school_id; // the school id for each student
    array[N_schools] int district_id; // the district for each school
}
parameters {
    array[N_districts] real<lower = 0, upper = 1> mu_district;
    array[N_districts] real<lower = 0> nu_district_raw; // standard normal -> implies nu_school ~ normal(nu_bar, sigma_nu)
    array[N_schools] real<lower = 0, upper = 1> mu_school;
    array[N_schools] real<lower = 0> nu_school;
    real<lower = 0> alpha_bar;
    real<lower = 0> beta_bar;
    real<lower = 0> nu_bar;
    real<lower = 0> sigma_nu;
}
 transformed parameters {
    // array[N_schools] real<lower = 0> nu_school;
    array[N_schools] real<lower = 0> a_school;
    array[N_schools] real<lower = 0> b_school;
    array[N_districts] real<lower = 0> a_district;
    array[N_districts] real <lower = 0> b_district;
    array[N_districts] real <lower = 0> nu_district;
    for (i in 1:N_schools) {
        // nu_school[i] = nu_bar + sigma_nu * nu_school_raw[i];
        a_school[i] = mu_school[i] * nu_school[i];
        b_school[i] = (1 - mu_school[i]) * nu_school[i];
    }
    for (district_index in 1:N_districts) {
        nu_district[district_index] = nu_bar + sigma_nu * nu_district_raw[district_index];
        a_district[district_index] = mu_district[district_index] * nu_district[district_index];
        b_district[district_index] = (1 - mu_district[district_index]) * nu_district[district_index];
    }
}
model {
    for (student_index in 1:N_students) {
        s[student_index] ~ beta(a_school[school_id[student_index]], b_school[school_id[student_index]]);
    }
    for (school_index in 1:N_schools) {
        mu_school[school_index] ~ beta(a_district[district_id[school_index]], b_district[district_id[school_index]]);
    }
    mu_district ~ beta(alpha_bar, beta_bar);
    nu_district_raw ~ std_normal();

    // hyperpriors
    alpha_bar ~ normal(3, 0.5);
    beta_bar ~ normal(1, 0.3);
    nu_bar ~ normal(40, 5);
    sigma_nu ~ exponential(1);
}
"

student_school_district_model_file <- write_stan_file(student_school_district_model_code)
student_school_district_model <- cmdstan_model(student_school_district_model_file)

student_school_district_model_data <- list(
    N_students = nrow(student_data),
    N_schools = length(unique(student_data$school_id)),
    N_districts = length(unique(student_data$district_id)),
    s = student_data$score,
    school_id = student_data$school_id,
    district_id = school_params$district
)

student_school_district_fit <- student_school_district_model$sample(
    data = student_school_district_model_data,
    chains = 4,
    iter_warmup = 1000,
    adapt_delta = 0.95
)
student_school_district_fit$summary()
```

    Running MCMC with 4 sequential chains...

    All 4 chains finished successfully.
    Mean chain execution time: 0.9 seconds.
    Total execution time: 3.9 seconds.

<table class="dataframe">
<caption>A draws_summary: 56 × 10</caption>
<thead>
	<tr><th scope=col>variable</th><th scope=col>mean</th><th scope=col>median</th><th scope=col>sd</th><th scope=col>mad</th><th scope=col>q5</th><th scope=col>q95</th><th scope=col>rhat</th><th scope=col>ess_bulk</th><th scope=col>ess_tail</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>lp__              </td><td>222.7176947</td><td>223.0595000</td><td> 3.93686660</td><td> 3.79693860</td><td>215.76725000</td><td>228.5353500</td><td>1.0035301</td><td>1654.261</td><td>2357.782</td></tr>
	<tr><td>mu_district[1]    </td><td>  0.8108640</td><td>  0.8118355</td><td> 0.03423787</td><td> 0.03307384</td><td>  0.75313205</td><td>  0.8667575</td><td>1.0005594</td><td>5053.485</td><td>2857.642</td></tr>
	<tr><td>mu_district[2]    </td><td>  0.6840614</td><td>  0.6850335</td><td> 0.04265020</td><td> 0.04337569</td><td>  0.61480330</td><td>  0.7528840</td><td>1.0017076</td><td>3930.215</td><td>2879.500</td></tr>
	<tr><td>mu_district[3]    </td><td>  0.6941475</td><td>  0.6959630</td><td> 0.04198568</td><td> 0.04179153</td><td>  0.62348970</td><td>  0.7613662</td><td>1.0008498</td><td>5018.537</td><td>2966.480</td></tr>
	<tr><td>nu_district_raw[1]</td><td>  0.8080386</td><td>  0.6769430</td><td> 0.60914963</td><td> 0.60004825</td><td>  0.06027230</td><td>  1.9802930</td><td>0.9999384</td><td>3687.749</td><td>1631.689</td></tr>
	<tr><td>nu_district_raw[2]</td><td>  0.7951544</td><td>  0.6724660</td><td> 0.59759151</td><td> 0.58762851</td><td>  0.06592412</td><td>  1.9247665</td><td>1.0015042</td><td>2791.602</td><td>1709.045</td></tr>
	<tr><td>nu_district_raw[3]</td><td>  0.8103433</td><td>  0.6857005</td><td> 0.60298377</td><td> 0.59143509</td><td>  0.06953199</td><td>  1.9685580</td><td>1.0001191</td><td>3552.671</td><td>1907.645</td></tr>
	<tr><td>mu_school[1]      </td><td>  0.7745501</td><td>  0.7750630</td><td> 0.02028668</td><td> 0.01939241</td><td>  0.73972350</td><td>  0.8062264</td><td>1.0015966</td><td>4542.343</td><td>2547.013</td></tr>
	<tr><td>mu_school[2]      </td><td>  0.8342911</td><td>  0.8349070</td><td> 0.01277099</td><td> 0.01272219</td><td>  0.81273770</td><td>  0.8545590</td><td>1.0011919</td><td>4220.755</td><td>3036.484</td></tr>
	<tr><td>mu_school[3]      </td><td>  0.8395642</td><td>  0.8404945</td><td> 0.01672362</td><td> 0.01640942</td><td>  0.81096990</td><td>  0.8656431</td><td>1.0010039</td><td>4468.803</td><td>2866.154</td></tr>
	<tr><td>mu_school[4]      </td><td>  0.7244529</td><td>  0.7250115</td><td> 0.01776163</td><td> 0.01737237</td><td>  0.69428420</td><td>  0.7529640</td><td>1.0009774</td><td>3779.505</td><td>2623.897</td></tr>
	<tr><td>mu_school[5]      </td><td>  0.6209195</td><td>  0.6212540</td><td> 0.02417814</td><td> 0.02367193</td><td>  0.58176280</td><td>  0.6599121</td><td>1.0006665</td><td>4574.196</td><td>2910.079</td></tr>
	<tr><td>mu_school[6]      </td><td>  0.7070876</td><td>  0.7075630</td><td> 0.01730462</td><td> 0.01654804</td><td>  0.67776680</td><td>  0.7344344</td><td>0.9997740</td><td>4020.686</td><td>2711.795</td></tr>
	<tr><td>mu_school[7]      </td><td>  0.6434111</td><td>  0.6434790</td><td> 0.01701471</td><td> 0.01667184</td><td>  0.61544455</td><td>  0.6715378</td><td>1.0011385</td><td>4227.745</td><td>2632.624</td></tr>
	<tr><td>mu_school[8]      </td><td>  0.7353718</td><td>  0.7358175</td><td> 0.01382481</td><td> 0.01381042</td><td>  0.71246380</td><td>  0.7575197</td><td>1.0012051</td><td>3897.445</td><td>2490.404</td></tr>
	<tr><td>mu_school[9]      </td><td>  0.7056546</td><td>  0.7066625</td><td> 0.01718360</td><td> 0.01605433</td><td>  0.67772540</td><td>  0.7324504</td><td>1.0004752</td><td>4186.585</td><td>2553.651</td></tr>
	<tr><td>nu_school[1]      </td><td> 19.2145683</td><td> 18.5469500</td><td> 5.71679088</td><td> 5.46189840</td><td> 11.00878000</td><td> 29.4999550</td><td>0.9997007</td><td>4618.797</td><td>2857.748</td></tr>
	<tr><td>nu_school[2]      </td><td> 43.2529643</td><td> 41.9769500</td><td>13.32993696</td><td>12.86148087</td><td> 24.15926000</td><td> 67.6573800</td><td>1.0001604</td><td>4144.801</td><td>2702.517</td></tr>
	<tr><td>nu_school[3]      </td><td> 25.7384937</td><td> 24.9508000</td><td> 7.72034944</td><td> 7.77319767</td><td> 14.41916500</td><td> 39.5445250</td><td>1.0004349</td><td>3992.273</td><td>3020.537</td></tr>
	<tr><td>nu_school[4]      </td><td> 30.0836856</td><td> 29.1282000</td><td> 9.12058981</td><td> 8.83051386</td><td> 16.85719500</td><td> 46.4470350</td><td>1.0002684</td><td>4392.158</td><td>2939.064</td></tr>
	<tr><td>nu_school[5]      </td><td> 18.6909772</td><td> 18.1623000</td><td> 5.52931243</td><td> 5.42742795</td><td> 10.69125500</td><td> 28.4436700</td><td>1.0003793</td><td>4818.263</td><td>3010.402</td></tr>
	<tr><td>nu_school[6]      </td><td> 34.3268246</td><td> 33.3853000</td><td>10.33198302</td><td> 9.93253044</td><td> 19.77090500</td><td> 52.8546050</td><td>1.0001168</td><td>4400.425</td><td>2784.537</td></tr>
	<tr><td>nu_school[7]      </td><td> 38.6659344</td><td> 37.6974000</td><td>11.69556233</td><td>11.55316050</td><td> 21.88963000</td><td> 59.5734650</td><td>1.0024960</td><td>5346.653</td><td>2871.480</td></tr>
	<tr><td>nu_school[8]      </td><td> 55.3977254</td><td> 53.8983000</td><td>17.19780834</td><td>16.83129063</td><td> 30.63416500</td><td> 86.0647300</td><td>1.0006023</td><td>4799.014</td><td>3115.822</td></tr>
	<tr><td>nu_school[9]      </td><td> 36.4689579</td><td> 35.2106500</td><td>11.43582314</td><td>11.03187834</td><td> 20.13321000</td><td> 57.4454050</td><td>1.0001742</td><td>4279.718</td><td>2810.782</td></tr>
	<tr><td>alpha_bar         </td><td>  3.0422431</td><td>  3.0382050</td><td> 0.48231749</td><td> 0.47995469</td><td>  2.24597800</td><td>  3.8459800</td><td>0.9999978</td><td>5304.740</td><td>2262.935</td></tr>
	<tr><td>beta_bar          </td><td>  1.1143574</td><td>  1.1040950</td><td> 0.25961945</td><td> 0.27084730</td><td>  0.70305225</td><td>  1.5594570</td><td>1.0024779</td><td>4861.593</td><td>2044.442</td></tr>
	<tr><td>nu_bar            </td><td> 40.9648167</td><td> 40.9428500</td><td> 4.80195340</td><td> 4.84209747</td><td> 33.12208000</td><td> 48.9125500</td><td>1.0006440</td><td>4662.214</td><td>2713.798</td></tr>
	<tr><td>sigma_nu          </td><td>  1.0194074</td><td>  0.7193850</td><td> 0.99442673</td><td> 0.73303228</td><td>  0.06086981</td><td>  2.9616380</td><td>1.0005527</td><td>3729.072</td><td>1817.774</td></tr>
	<tr><td>a_school[1]       </td><td> 14.8995139</td><td> 14.3299500</td><td> 4.50320965</td><td> 4.33193481</td><td>  8.48290100</td><td> 22.9380250</td><td>0.9996985</td><td>4538.265</td><td>2901.148</td></tr>
	<tr><td>a_school[2]       </td><td> 36.1175329</td><td> 34.9564500</td><td>11.23951209</td><td>10.78080003</td><td> 20.09869000</td><td> 56.4363000</td><td>1.0001898</td><td>4065.883</td><td>2650.351</td></tr>
	<tr><td>a_school[3]       </td><td> 21.6456836</td><td> 20.9735000</td><td> 6.61668905</td><td> 6.61232187</td><td> 11.94504000</td><td> 33.4753800</td><td>1.0004215</td><td>3870.308</td><td>2884.144</td></tr>
	<tr><td>a_school[4]       </td><td> 21.8187776</td><td> 21.1334500</td><td> 6.70637210</td><td> 6.41261565</td><td> 12.10184500</td><td> 33.7943250</td><td>1.0003935</td><td>4254.781</td><td>2893.809</td></tr>
	<tr><td>a_school[5]       </td><td> 11.6109026</td><td> 11.2779000</td><td> 3.47769899</td><td> 3.46460640</td><td>  6.62352250</td><td> 17.8284000</td><td>0.9997981</td><td>4838.969</td><td>3135.722</td></tr>
	<tr><td>a_school[6]       </td><td> 24.2936537</td><td> 23.5578000</td><td> 7.40209612</td><td> 6.96792348</td><td> 13.78885000</td><td> 37.6521700</td><td>1.0002818</td><td>4319.045</td><td>2782.099</td></tr>
	<tr><td>a_school[7]       </td><td> 24.8864011</td><td> 24.2969500</td><td> 7.58076818</td><td> 7.54791660</td><td> 13.91935000</td><td> 38.3683450</td><td>1.0021202</td><td>5219.617</td><td>2808.585</td></tr>
	<tr><td>a_school[8]       </td><td> 40.7653610</td><td> 39.6687500</td><td>12.76235897</td><td>12.46696101</td><td> 22.32013000</td><td> 63.8617600</td><td>1.0004592</td><td>4707.321</td><td>2921.420</td></tr>
	<tr><td>a_school[9]       </td><td> 25.7575809</td><td> 24.7504000</td><td> 8.16618410</td><td> 7.81196766</td><td> 14.07162000</td><td> 40.8460400</td><td>1.0002553</td><td>4164.509</td><td>2748.807</td></tr>
	<tr><td>b_school[1]       </td><td>  4.3150550</td><td>  4.1789750</td><td> 1.28389551</td><td> 1.27316051</td><td>  2.49373000</td><td>  6.6448395</td><td>1.0000253</td><td>5010.965</td><td>2645.208</td></tr>
	<tr><td>b_school[2]       </td><td>  7.1354307</td><td>  6.8631350</td><td> 2.16551649</td><td> 2.07649991</td><td>  4.02084000</td><td> 11.1983650</td><td>1.0001576</td><td>4643.735</td><td>2639.532</td></tr>
	<tr><td>b_school[3]       </td><td>  4.0928110</td><td>  3.9709350</td><td> 1.18284069</td><td> 1.13933362</td><td>  2.36425450</td><td>  6.2035020</td><td>1.0003813</td><td>4963.040</td><td>2705.370</td></tr>
	<tr><td>b_school[4]       </td><td>  8.2649078</td><td>  8.0173400</td><td> 2.48574372</td><td> 2.36380555</td><td>  4.64036200</td><td> 12.7424900</td><td>1.0000374</td><td>4801.247</td><td>2700.400</td></tr>
	<tr><td>b_school[5]       </td><td>  7.0800751</td><td>  6.8545050</td><td> 2.12275121</td><td> 2.09103680</td><td>  4.03383650</td><td> 10.8581950</td><td>1.0016265</td><td>4784.077</td><td>3056.471</td></tr>
	<tr><td>b_school[6]       </td><td> 10.0331710</td><td>  9.7383350</td><td> 3.00523071</td><td> 2.88286381</td><td>  5.76717100</td><td> 15.4092950</td><td>1.0000639</td><td>4591.238</td><td>2680.650</td></tr>
	<tr><td>b_school[7]       </td><td> 13.7795324</td><td> 13.4024500</td><td> 4.18863892</td><td> 4.18923456</td><td>  7.75234100</td><td> 21.2982450</td><td>1.0029906</td><td>5496.540</td><td>2827.717</td></tr>
	<tr><td>b_school[8]       </td><td> 14.6323653</td><td> 14.2183500</td><td> 4.51502754</td><td> 4.48894215</td><td>  8.09328700</td><td> 22.7103800</td><td>1.0009363</td><td>5022.422</td><td>2875.640</td></tr>
	<tr><td>b_school[9]       </td><td> 10.7113761</td><td> 10.3030500</td><td> 3.34226299</td><td> 3.20847983</td><td>  5.89056500</td><td> 16.8123450</td><td>1.0002922</td><td>4603.464</td><td>2897.899</td></tr>
	<tr><td>a_district[1]     </td><td> 33.8885185</td><td> 33.7491500</td><td> 4.27652399</td><td> 4.24512858</td><td> 26.98027000</td><td> 41.1086200</td><td>1.0008670</td><td>4638.184</td><td>2703.454</td></tr>
	<tr><td>a_district[2]     </td><td> 28.5749109</td><td> 28.5183500</td><td> 3.79763607</td><td> 3.87714726</td><td> 22.42455500</td><td> 34.9334950</td><td>1.0012701</td><td>4119.979</td><td>2951.821</td></tr>
	<tr><td>a_district[3]     </td><td> 29.0074459</td><td> 28.9348000</td><td> 3.83058313</td><td> 3.87269946</td><td> 22.74620500</td><td> 35.4181750</td><td>1.0012603</td><td>4829.572</td><td>2462.030</td></tr>
	<tr><td>b_district[1]     </td><td>  7.8981206</td><td>  7.8087650</td><td> 1.67861747</td><td> 1.71713249</td><td>  5.30965150</td><td> 10.8158550</td><td>1.0027108</td><td>4998.256</td><td>2774.579</td></tr>
	<tr><td>b_district[2]     </td><td> 13.1974426</td><td> 13.1079500</td><td> 2.35517319</td><td> 2.32227051</td><td>  9.38773450</td><td> 17.2396250</td><td>1.0000954</td><td>4930.257</td><td>2554.079</td></tr>
	<tr><td>b_district[3]     </td><td> 12.7824112</td><td> 12.7071500</td><td> 2.30107724</td><td> 2.34206322</td><td>  9.12928300</td><td> 16.7330850</td><td>1.0004643</td><td>4764.235</td><td>2811.945</td></tr>
	<tr><td>nu_district[1]    </td><td> 41.7866384</td><td> 41.6816000</td><td> 4.91358096</td><td> 4.98472359</td><td> 33.71537000</td><td> 50.0308250</td><td>1.0008337</td><td>4875.105</td><td>2815.289</td></tr>
	<tr><td>nu_district[2]    </td><td> 41.7723534</td><td> 41.7305500</td><td> 4.91772353</td><td> 4.92860718</td><td> 33.74658000</td><td> 49.8716450</td><td>1.0002981</td><td>4693.667</td><td>2654.541</td></tr>
	<tr><td>nu_district[3]    </td><td> 41.7898568</td><td> 41.7380500</td><td> 4.91824700</td><td> 4.95959352</td><td> 33.68915500</td><td> 49.8668050</td><td>1.0008588</td><td>4769.346</td><td>2773.605</td></tr>
</tbody>
</table>

```r
student_school_district_draws <- as_draws_matrix(student_school_district_fit)
```

```r
# Extract district means
district_means_draws <- student_school_district_draws[, grep('mu_district', colnames(student_school_district_draws))]

# Calculate the mean, lower, and upper quantiles for each district
district_mean_means <- apply(district_means_draws, 2, mean)
district_mean_lower <- apply(district_means_draws, 2, function(col) quantile(col, 0.025))
district_mean_upper <- apply(district_means_draws, 2, function(col) quantile(col, 0.975))

# Calculate the mean for the districts
prior_district_mean <- mean(student_school_district_draws[, 'alpha_bar'] / (student_school_district_draws[, 'alpha_bar'] + student_school_district_draws[, 'beta_bar']))

# Create a data frame to store the results
district_means_df <- data.frame(
    district = 1:NUM_DISTRICTS,
    mean = district_mean_means,
    lower = district_mean_lower,
    upper = district_mean_upper
)
# Plot the district means along with the true means
ggplot(district_means_df, aes(district, mean)) +
    geom_point(aes(colour = "Estimated Mean")) +
    geom_errorbar(aes(ymin = lower, ymax = upper)) +
    geom_point(data = data.frame(district = 1:NUM_DISTRICTS, mean = district_means), aes(district, mean, colour = "True Mean")) +
    geom_hline(yintercept = prior_district_mean, linetype = 'dashed') +
    labs(x = "District", y = "Mean Score", colour = "Mean Type") +
    scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_54_0.png)

```r
# Extract school means
school_means_draws <- student_school_district_draws[, grep('mu_school', colnames(student_school_district_draws))]

# Calculate the mean, lower, and upper quantiles for each school
school_mean_means <- apply(school_means_draws, 2, mean)
school_mean_lower <- apply(school_means_draws, 2, function(col) quantile(col, 0.025))
school_mean_upper <- apply(school_means_draws, 2, function(col) quantile(col, 0.975))

district_mean_draws <- student_school_district_draws[, grep('mu_district', colnames(student_school_district_draws))]
district_mean_means <- apply(district_means_draws, 2, mean)

# Create a data frame to store the results
school_means_df <- data.frame(
    school = as.factor(1:TOTAL_SCHOOLS),
    mean = school_mean_means,
    lower = school_mean_lower,
    upper = school_mean_upper
)

# Plot the school means along with the true means
plot <- ggplot(school_means_df, aes(school, mean)) +
    geom_point(aes(colour = "Estimated Mean")) +
    geom_errorbar(aes(ymin = lower, ymax = upper)) +
    geom_point(data = data.frame(school = 1:TOTAL_SCHOOLS, mean = school_params$school_mu), aes(school, mean, colour = "True Mean")) +
    labs(x = "School", y = "Mean Score", colour = "Mean Type") +
    scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
    theme_bw() +
    theme(
        panel.grid.major = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
    )

for (district in 1:NUM_DISTRICTS) {
    print(district)
    plot <- plot +
        geom_segment(x = (district - 1) * SCHOOLS_PER_DISTRICT + 0.5, xend = district * SCHOOLS_PER_DISTRICT + 0.5, y = district_mean_means[district], yend = district_mean_means[district], linetype = "dashed")
}

print(plot)
```

    [1] 1
    [1] 2
    [1] 3

![png](/2024-12-02-hierarchical-bayesian-models/output_55_1.png)

Great! So that worked out pretty well - we're getting good estimates for both our district-level and school-level values.

So now that we've taken a look at a couple of simulated examples, let's look at some real data: provincial achievement test scores for Alberta!

## Example - Alberta Diploma Exam Scores, 2016

Each year, students in Grade 12 in Alberta write diploma exams. These are standardized exams designed to assess the students' knowledge of different courses. Not every course has a diploma exam, but for those that do, it counts for 30% of their final grade.

Luckily for us, the results of the diploma exam are released publicly, broken up by school, school authority, year, and subject! We're going to apply the same idea as above to some real data.

The first thing that we need to do is to load in the data. It can be found publicly at [the Canada Open Government site](https://open.canada.ca/data/en/dataset/4a922ec0-11e8-4ec8-be91-ae3dcda08d86/resource/53636ea9-045a-4df8-a4a8-ee79a7c186ac). For this, we'll be looking at the data for the 2015 / 2016 school year.

```r
school_df <- read_excel('data/diploma-multiyear-sch-list-annual.xlsx')
colnames(school_df)
```

<style>
.list-inline {list-style: none; margin:0; padding: 0}
.list-inline>li {display: inline-block}
.list-inline>li:not(:last-child)::after {content: "\00b7"; padding: 0 .5ex}
</style>
<ol class=list-inline><li>'Diploma Course'</li><li>'Authority Type'</li><li>'Authority Code'</li><li>'Authority Name'</li><li>'School Code'</li><li>'School Name'</li><li>'2012SchStudents Writing'</li><li>'2012Sch School Mark % Exc'</li><li>'2012Sch School Mark % Acc'</li><li>'2012Sch School Average %'</li><li>'2012Sch School Standard Deviation %'</li><li>'2012Sch Exam Mark % Exc'</li><li>'2012Sch Exam Mark Exc Sig'</li><li>'2012Sch Exam Mark % Acc'</li><li>'2012Sch Exam Mark Acc Sig'</li><li>'2012Sch Exam Average %'</li><li>'2012Sch Exam Standard Deviation %'</li><li>'2013Sch Students Writing'</li><li>'2013Sch School Mark % Exc'</li><li>'2013Sch School Mark % Acc'</li><li>'2013Sch School Average %'</li><li>'2013Sch School Standard Deviation %'</li><li>'2013Sch Exam Mark % Exc'</li><li>'2013Sch Exam Mark Exc Sig'</li><li>'2013Sch Exam Mark % Acc'</li><li>'2013Sch Exam Mark Acc Sig'</li><li>'2013Sch Exam Average %'</li><li>'2013Sch Exam Standard Deviation %'</li><li>'2014Sch Students Writing'</li><li>'2014Sch School Mark % Exc'</li><li>'2014Sch School Mark % Acc'</li><li>'2014Sch School Average %'</li><li>'2014Sch School Standard Deviation %'</li><li>'2014Sch Exam Mark % Exc'</li><li>'2014Sch Exam Mark Exc Sig'</li><li>'2014Sch Exam Mark % Acc'</li><li>'2014Sch Exam Mark Acc Sig'</li><li>'2014Sch Exam Average %'</li><li>'2014Sch Exam Standard Deviation %'</li><li>'2015Sch Students Writing'</li><li>'2015Sch School Mark % Exc'</li><li>'2015Sch School Mark % Acc'</li><li>'2015Sch School Average %'</li><li>'2015Sch School Standard Deviation %'</li><li>'2015Sch Exam Mark % Exc'</li><li>'2015Sch Exam Mark Exc Sig'</li><li>'2015Sch Exam Mark % Acc'</li><li>'2015Sch Exam Mark Acc Sig'</li><li>'2015Sch Exam Average %'</li><li>'2015Sch Exam Standard Deviation %'</li><li>'2016Sch Students Writing'</li><li>'2016Sch School Mark % Exc'</li><li>'2016Sch School Mark % Acc'</li><li>'2016Sch School Average %'</li><li>'2016Sch School Standard Deviation %'</li><li>'2016Sch Exam Mark % Exc'</li><li>'2016Sch Exam Mark Exc Sig'</li><li>'2016Sch Exam Mark % Acc'</li><li>'2016Sch Exam Mark Acc Sig'</li><li>'2016Sch Exam Average %'</li><li>'2016Sch Exam Standard Deviation %'</li></ol>

```r
unique(school_df$`Diploma Course`)
```

<style>
.list-inline {list-style: none; margin:0; padding: 0}
.list-inline>li {display: inline-block}
.list-inline>li:not(:last-child)::after {content: "\00b7"; padding: 0 .5ex}
</style>
<ol class=list-inline><li>'Biology 30'</li><li>'Chemistry 30'</li><li>'English Lang Arts 30-1'</li><li>'English Lang Arts 30-2'</li><li>'Mathematics 30-1'</li><li>'Mathematics 30-2'</li><li>'Physics 30'</li><li>'Science 30'</li><li>'Social Studies 30-1'</li><li>'Social Studies 30-2'</li><li>'French Lang Arts 30-1'</li><li>'Français 30-1'</li><li>'1. The 2012/2013 results do not include students who were exempted from writing the examination because of the flooding in Calgary and southern Alberta.2. The 2015/2016 results do not include students who were exempted from writing the exam because of the Fort McMurray wildfires.3. +,=,- The percentage of students meeting the standard is significantly above (+), not significantly different from (=), or significantly below (-) the previous three-year average. A difference is reported as significant when there is a 5% or smaller probability that a difference of that size could occur by chance. The fewer the number of students, the larger the difference must be from the expectation before it is considered significant. Significance is not calculated for fewer than 6 students.'</li></ol>

Unsuprisingly, there's a lot here! Let's focus in - specifically, let's only look at the Mathematics 30-1 course in 2016. I first taught that course in 2017, so the results here are of some personal interest to me.

```r
relevant_schools_df <- school_df[school_df$`Diploma Course` == 'Mathematics 30-1', c("Diploma Course", "Authority Type", "Authority Code", "Authority Name", "School Code", "School Name", "2016Sch Students Writing", "2016Sch Exam Average %", "2016Sch Exam Standard Deviation %")]

# remove any where no students wrote
relevant_schools_df <- relevant_schools_df[relevant_schools_df$`2016Sch Students Writing` != 'n/a', ]

# convert to numeric
relevant_schools_df$`2016Sch Students Writing` <- as.integer(relevant_schools_df$`2016Sch Students Writing`)
relevant_schools_df$`2016Sch Exam Average %` <- as.numeric(relevant_schools_df$`2016Sch Exam Average %`)
relevant_schools_df$`2016Sch Exam Standard Deviation %` <- as.numeric(relevant_schools_df$`2016Sch Exam Standard Deviation %`)

# codes should be factors
relevant_schools_df$`Authority Code` <- as.factor(relevant_schools_df$`Authority Code`)
relevant_schools_df$`School Code` <- as.factor(relevant_schools_df$`School Code`)

head(relevant_schools_df)
```

<table class="dataframe">
<caption>A tibble: 6 × 9</caption>
<thead>
	<tr><th scope=col>Diploma Course</th><th scope=col>Authority Type</th><th scope=col>Authority Code</th><th scope=col>Authority Name</th><th scope=col>School Code</th><th scope=col>School Name</th><th scope=col>2016Sch Students Writing</th><th scope=col>2016Sch Exam Average %</th><th scope=col>2016Sch Exam Standard Deviation %</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;fct&gt;</th><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;fct&gt;</th><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;int&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>Mathematics 30-1</td><td>Charter </td><td>0009</td><td>Foundations for the Future Charter Academy Charter School Society  </td><td>0012</td><td>FFCA High School Campus                </td><td>113</td><td>63.9</td><td>20.0</td></tr>
	<tr><td>Mathematics 30-1</td><td>Private </td><td>0015</td><td>Webber Academy Foundation                                          </td><td>0021</td><td>Webber Academy                         </td><td> 59</td><td>84.8</td><td>10.8</td></tr>
	<tr><td>Mathematics 30-1</td><td>Separate</td><td>0019</td><td>Red Deer Catholic Regional Division No. 39                         </td><td>1272</td><td>St. Dominic High School                </td><td> 12</td><td>63.3</td><td>15.5</td></tr>
	<tr><td>Mathematics 30-1</td><td>Separate</td><td>0019</td><td>Red Deer Catholic Regional Division No. 39                         </td><td>4471</td><td>Ecole Secondaire Notre Dame High School</td><td>190</td><td>61.8</td><td>20.0</td></tr>
	<tr><td>Mathematics 30-1</td><td>Separate</td><td>0019</td><td>Red Deer Catholic Regional Division No. 39                         </td><td>4483</td><td>St. Gabriel Cyber School               </td><td> 26</td><td>38.9</td><td>23.0</td></tr>
	<tr><td>Mathematics 30-1</td><td>Separate</td><td>0020</td><td>St. Thomas Aquinas Roman Catholic Separate Regional Division No. 38</td><td>1328</td><td>Holy Trinity Academy                   </td><td> 10</td><td>49.0</td><td>22.4</td></tr>
</tbody>
</table>

Let's graph the school results to get a feel for what the data look like:

```r
plot_df <- data.frame(
    school = relevant_schools_df$`School Code`,
    authority = relevant_schools_df$`Authority Code`,
    mean = relevant_schools_df$`2016Sch Exam Average %`,
    lower = relevant_schools_df$`2016Sch Exam Average %` - relevant_schools_df$`2016Sch Exam Standard Deviation %`,
    upper = relevant_schools_df$`2016Sch Exam Average %` + relevant_schools_df$`2016Sch Exam Standard Deviation %`
)
# sort by mean, ascending
plot_df <- plot_df[order(plot_df$mean), ]

# should be plotted in the order of the mean
plot_df$school <- factor(plot_df$school, levels = plot_df$school)

ggplot(plot_df, aes(school, mean)) +
    geom_point() +
    geom_errorbar(aes(ymin = lower, ymax = upper)) +
    labs(x = "School", y = "Mean Score (%)") +
    theme_bw() +
    theme(
        panel.grid.major = element_blank(),
        axis.text.x = element_blank(), axis.ticks.x = element_blank()
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_63_0.png)

There's definitely an interesting shape to the data! I am a bit shocked by the number of schools with extremely low averages, but such is life I suppose. Let's see if colouring by the school authority reveals anything.

```r
ggplot(plot_df, aes(school, mean, colour = authority)) +
    geom_point() +
    geom_errorbar(aes(ymin = lower, ymax = upper)) +
    labs(x = "School", y = "Mean Score", colour = "Authority") +
    theme_bw() +
    theme(
        panel.grid.major = element_blank(),
        axis.text.x = element_blank(), axis.ticks.x = element_blank()
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_65_0.png)

This is some glorious nonsense! Let's try creating a crude average for the different authorities and plotting that.

```r
authorities_df <- data.frame(authority = unique(relevant_schools_df$`Authority Code`))
authority_means <- sapply(authorities_df$authority, function(authority) {
    authority_schools <- relevant_schools_df[relevant_schools_df$`Authority Code` == authority, ]
    authority_mean <- sum(authority_schools$`2016Sch Exam Average %` * authority_schools$`2016Sch Students Writing`) / sum(authority_schools$`2016Sch Students Writing`)
    authority_mean
})
authority_num_schools <- sapply(authorities_df$authority, function(authority) {
    nrow(relevant_schools_df[relevant_schools_df$`Authority Code` == authority, ])
})

authorities_df$mean <- authority_means
authorities_df$num_schools <- authority_num_schools
# # plot these, ascending
authorities_df <- authorities_df[order(authorities_df$mean), ]
authorities_df$authority <- factor(authorities_df$authority, levels = authorities_df$authority)
ggplot(authorities_df, aes(authority, mean)) +
    geom_point(aes(size = num_schools)) +
    labs(x = "Authority", y = "Mean Score") +
    theme(axis.text.x = element_blank(), axis.ticks.x = element_blank()) +
    theme_bw() +  # Set background to white
    theme(
        panel.grid.major.x = element_blank(),
        panel.grid.minor.x = element_blank(),
        panel.grid.major.y = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
        axis.ticks.x = element_blank(),
        axis.text.x = element_blank(),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_67_0.png)

So this looks roughly the same as the earlier graph of the per-school average, except now we're plotting the per-authority average.

Great! So now let's try to create a hierarchical model for the results based on the school and the school based on the authority. There is one wrinkle here, which is that for the data that we have, we don't get the individual student data (unfortunately), which is different from what we've considered before. Instead, we're going to have to create a likelihood from the data which we do have, which is the final mean, standard deviation, and number of students for each school. We'll also remove any schools where fewer than 30 students wrote the exam.

So here's our new approach:

-   Filter out all of the schools where less than 30 students wrote the exam
-   Recalculate the relevant schools and authorities
-   Model the likelihood for the sample mean as
    $$
    \begin{align*}
    \bar{x_i} &\sim \text{Normal}(\mu, \sigma / \sqrt{n_i}) \\
    \end{align*}
    $$

Great! So now let's filter the data.

```r
MIN_STUDENTS <- 30
filtered_schools_df <- relevant_schools_df[relevant_schools_df['2016Sch Students Writing'] >= MIN_STUDENTS, ]
print(paste('Original number of schools:', nrow(relevant_schools_df), 'Filtered number of schools:', nrow(filtered_schools_df)))
```

    [1] "Original number of schools: 317 Filtered number of schools: 140"

```r
# plot the schools, ascending
plot_df <- data.frame(
    school = filtered_schools_df$`School Code`,
    authority = filtered_schools_df$`Authority Code`,
    students = filtered_schools_df$`2016Sch Students Writing`,
    mean = filtered_schools_df$`2016Sch Exam Average %`,
    lower = filtered_schools_df$`2016Sch Exam Average %` - filtered_schools_df$`2016Sch Exam Standard Deviation %`,
    upper = filtered_schools_df$`2016Sch Exam Average %` + filtered_schools_df$`2016Sch Exam Standard Deviation %`
)
# sort by mean, ascending
plot_df <- plot_df[order(plot_df$mean), ]

# should be plotted in the order of the mean
plot_df$school <- factor(plot_df$school, levels = plot_df$school)

ggplot(plot_df, aes(school, mean)) +
    geom_point(aes(size = students)) +
    geom_errorbar(aes(ymin = lower, ymax = upper)) +
    labs(x = "School", y = "Mean Score") +
    theme_bw() +
    theme(
        panel.grid.major.x = element_blank(),
        panel.grid.minor.x = element_blank(),
        panel.grid.major.y = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
        axis.ticks.x = element_blank(),
        axis.text.x = element_blank(),
    )

# now handle the authorities
authorities_df <- data.frame(authority = unique(filtered_schools_df$`Authority Code`))
authority_means <- sapply(authorities_df$authority, function(authority) {
    authority_schools <- filtered_schools_df[filtered_schools_df$`Authority Code` == authority, ]
    authority_mean <- sum(authority_schools$`2016Sch Exam Average %` * authority_schools$`2016Sch Students Writing`) / sum(authority_schools$`2016Sch Students Writing`)
    authority_mean
})
authority_num_schools <- sapply(authorities_df$authority, function(authority) {
    nrow(filtered_schools_df[filtered_schools_df$`Authority Code` == authority, ])
})


authorities_df$mean <- authority_means
authorities_df$num_schools <- authority_num_schools
# # plot the authorities, ascending
authorities_df <- authorities_df[order(authorities_df$mean), ]
authorities_df$authority <- factor(authorities_df$authority, levels = authorities_df$authority)
ggplot(authorities_df, aes(authority, mean)) +
    geom_point(aes(size = num_schools)) +
    labs(x = "Authority", y = "Mean Score", size = "Number of Schools") +
    theme_bw() +
    theme(
        panel.grid.major.x = element_blank(),
        panel.grid.minor.x = element_blank(),
        panel.grid.major.y = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
        axis.ticks.x = element_blank(),
        axis.text.x = element_blank(),
    )
```

![png](/2024-12-02-hierarchical-bayesian-models/output_70_0.png)

![png](/2024-12-02-hierarchical-bayesian-models/output_70_1.png)

By looking at the graphs, we see that the underlying shape hasn't changed too much by removing the schools with fewer students; we've just trimmed it down a bit. Now let's build the model! As before, we'll start with the unpooled model, then pool all of the schools together, then finally pooly by district.

```r
# convert the authorities to indices
authority_df <- data.frame(
    authority = unique(filtered_schools_df$`Authority Code`),
    index = seq_along(1:length(unique(filtered_schools_df$`Authority Code`)))
)
authority_index <- authority_df$index[match(filtered_schools_df$`Authority Code`, authority_df$authority)]
alberta_schools_data <- list(
    N_schools = nrow(filtered_schools_df),
    N_authorities = length(unique(filtered_schools_df$`Authority Code`)),
    authority_index = authority_index,
    school_mean = filtered_schools_df$`2016Sch Exam Average %` / 100,
    school_s_squared = (filtered_schools_df$`2016Sch Exam Standard Deviation %` / 100)^2,
    school_n = filtered_schools_df$`2016Sch Students Writing`
)

run_schools_model <- function(model_code_string) {
    model_file <- write_stan_file(model_code_string)
    model <- cmdstan_model(model_file)
    model_fit <- model$sample(
        data = alberta_schools_data,
        chains = 4,
        iter_warmup = 1000,
        adapt_delta = 0.99
    )
    model_fit
}

alberta_schools_unpooled_code <- "
data {
    int<lower = 0> N_schools;
    array[N_schools] real<lower = 0, upper = 1> school_mean;
    array[N_schools] int<lower = 0> school_n;
}
parameters {
    array[N_schools] real<lower = 0, upper = 1> school_mu;
    array[N_schools] real<lower = 0> school_nu;
}
transformed parameters {
    array[N_schools] real<lower = 0> school_alpha;
    array[N_schools] real<lower = 0> school_beta;
    array[N_schools] real<lower = 0> school_sigma_squared;
    for (i in 1:N_schools) {
        school_alpha[i] = school_mu[i] * school_nu[i];
        school_beta[i] = (1 - school_mu[i]) * school_nu[i];
        school_sigma_squared[i] = (school_alpha[i] * school_beta[i]) / (( school_alpha[i] + school_beta[i])^2 * (school_alpha[i] + school_beta[i] + 1));
    }
}
model {
    for (i in 1:N_schools) {
        school_mean[i] ~ normal(school_mu[i], sqrt(school_sigma_squared[i] / school_n[i]));
    }
    school_mu ~ beta(3, 1);
    school_nu ~ normal(30, 4);
}
"

alberta_schools_unpooled_fit <- run_schools_model(alberta_schools_unpooled_code)
alberta_schools_unpooled_fit$summary()
```

    Running MCMC with 4 sequential chains...

    All 4 chains finished successfully.
    Mean chain execution time: 3.5 seconds.
    Total execution time: 14.4 seconds.

<table class="dataframe">
<caption>A draws_summary: 701 × 10</caption>
<thead>
	<tr><th scope=col>variable</th><th scope=col>mean</th><th scope=col>median</th><th scope=col>sd</th><th scope=col>mad</th><th scope=col>q5</th><th scope=col>q95</th><th scope=col>rhat</th><th scope=col>ess_bulk</th><th scope=col>ess_tail</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>lp__         </td><td>649.5773287</td><td>649.7755000</td><td>12.201033065</td><td>12.312993000</td><td>629.2904000</td><td>669.0576000</td><td>1.0029001</td><td> 1430.923</td><td>2053.862</td></tr>
	<tr><td>school_mu[1] </td><td>  0.6392039</td><td>  0.6393735</td><td> 0.008405132</td><td> 0.008324058</td><td>  0.6248339</td><td>  0.6527770</td><td>1.0023608</td><td> 9861.831</td><td>3085.230</td></tr>
	<tr><td>school_mu[2] </td><td>  0.8478341</td><td>  0.8478955</td><td> 0.008545827</td><td> 0.008547189</td><td>  0.8338857</td><td>  0.8613602</td><td>1.0026531</td><td>10923.645</td><td>2489.053</td></tr>
	<tr><td>school_mu[3] </td><td>  0.6181320</td><td>  0.6181990</td><td> 0.006292014</td><td> 0.006273622</td><td>  0.6079128</td><td>  0.6282794</td><td>1.0005929</td><td> 9275.417</td><td>2710.679</td></tr>
	<tr><td>school_mu[4] </td><td>  0.6221342</td><td>  0.6222265</td><td> 0.008266059</td><td> 0.008361123</td><td>  0.6085825</td><td>  0.6353736</td><td>1.0003571</td><td> 8557.712</td><td>2885.691</td></tr>
	<tr><td>school_mu[5] </td><td>  0.6091299</td><td>  0.6094770</td><td> 0.010714624</td><td> 0.010414524</td><td>  0.5915248</td><td>  0.6270132</td><td>1.0001241</td><td> 9395.256</td><td>2746.722</td></tr>
	<tr><td>school_mu[6] </td><td>  0.5643965</td><td>  0.5645085</td><td> 0.012238623</td><td> 0.012046125</td><td>  0.5443312</td><td>  0.5843314</td><td>1.0013317</td><td>10665.311</td><td>2956.641</td></tr>
	<tr><td>school_mu[7] </td><td>  0.7579158</td><td>  0.7584285</td><td> 0.013581550</td><td> 0.013060965</td><td>  0.7342792</td><td>  0.7798935</td><td>1.0003750</td><td>11019.426</td><td>2544.310</td></tr>
	<tr><td>school_mu[8] </td><td>  0.6613427</td><td>  0.6616730</td><td> 0.015752203</td><td> 0.015415333</td><td>  0.6350851</td><td>  0.6866007</td><td>1.0003204</td><td> 9957.812</td><td>3062.898</td></tr>
	<tr><td>school_mu[9] </td><td>  0.5039022</td><td>  0.5035950</td><td> 0.015266937</td><td> 0.015177376</td><td>  0.4785290</td><td>  0.5287871</td><td>1.0001035</td><td> 9218.511</td><td>2836.723</td></tr>
	<tr><td>school_mu[10]</td><td>  0.5495140</td><td>  0.5494805</td><td> 0.010088190</td><td> 0.010011998</td><td>  0.5330208</td><td>  0.5663486</td><td>1.0020066</td><td> 9635.417</td><td>2255.971</td></tr>
	<tr><td>school_mu[11]</td><td>  0.6074124</td><td>  0.6077090</td><td> 0.013410985</td><td> 0.013212931</td><td>  0.5844894</td><td>  0.6287470</td><td>1.0013039</td><td>10233.535</td><td>2432.842</td></tr>
	<tr><td>school_mu[12]</td><td>  0.6794369</td><td>  0.6794635</td><td> 0.014992119</td><td> 0.014513913</td><td>  0.6545396</td><td>  0.7037216</td><td>1.0017366</td><td> 9346.925</td><td>2523.928</td></tr>
	<tr><td>school_mu[13]</td><td>  0.7769397</td><td>  0.7770205</td><td> 0.008391946</td><td> 0.008506418</td><td>  0.7629991</td><td>  0.7904530</td><td>1.0006798</td><td>10609.349</td><td>3094.103</td></tr>
	<tr><td>school_mu[14]</td><td>  0.5941705</td><td>  0.5941310</td><td> 0.009878963</td><td> 0.009741423</td><td>  0.5780519</td><td>  0.6106447</td><td>0.9999009</td><td> 9063.377</td><td>2557.421</td></tr>
	<tr><td>school_mu[15]</td><td>  0.5822358</td><td>  0.5823065</td><td> 0.010688901</td><td> 0.010906747</td><td>  0.5647210</td><td>  0.5995771</td><td>0.9998798</td><td> 8514.371</td><td>2849.397</td></tr>
	<tr><td>school_mu[16]</td><td>  0.5612107</td><td>  0.5611500</td><td> 0.009223588</td><td> 0.008926735</td><td>  0.5459749</td><td>  0.5764008</td><td>1.0015537</td><td> 9275.307</td><td>2389.068</td></tr>
	<tr><td>school_mu[17]</td><td>  0.6562535</td><td>  0.6564125</td><td> 0.009768611</td><td> 0.009671000</td><td>  0.6395904</td><td>  0.6720952</td><td>1.0010295</td><td> 8951.184</td><td>2822.084</td></tr>
	<tr><td>school_mu[18]</td><td>  0.7020372</td><td>  0.7021400</td><td> 0.005097796</td><td> 0.005126831</td><td>  0.6936178</td><td>  0.7103156</td><td>1.0021930</td><td> 8503.081</td><td>3030.269</td></tr>
	<tr><td>school_mu[19]</td><td>  0.5692039</td><td>  0.5691785</td><td> 0.007228040</td><td> 0.007006026</td><td>  0.5572946</td><td>  0.5811564</td><td>1.0009770</td><td> 9479.563</td><td>2602.059</td></tr>
	<tr><td>school_mu[20]</td><td>  0.6291591</td><td>  0.6291845</td><td> 0.007741292</td><td> 0.007446359</td><td>  0.6163890</td><td>  0.6421733</td><td>1.0009216</td><td> 9699.631</td><td>2890.812</td></tr>
	<tr><td>school_mu[21]</td><td>  0.5291810</td><td>  0.5291255</td><td> 0.009326573</td><td> 0.009361878</td><td>  0.5138633</td><td>  0.5444111</td><td>1.0025134</td><td> 9776.379</td><td>2905.082</td></tr>
	<tr><td>school_mu[22]</td><td>  0.6482721</td><td>  0.6483485</td><td> 0.010462342</td><td> 0.010331498</td><td>  0.6312333</td><td>  0.6653092</td><td>1.0003151</td><td> 8538.696</td><td>2790.360</td></tr>
	<tr><td>school_mu[23]</td><td>  0.5894198</td><td>  0.5894010</td><td> 0.010529789</td><td> 0.010301846</td><td>  0.5720068</td><td>  0.6064943</td><td>1.0013085</td><td> 9797.334</td><td>2746.159</td></tr>
	<tr><td>school_mu[24]</td><td>  0.5411187</td><td>  0.5410025</td><td> 0.007940582</td><td> 0.007633166</td><td>  0.5281375</td><td>  0.5540133</td><td>1.0017240</td><td>11054.748</td><td>2125.300</td></tr>
	<tr><td>school_mu[25]</td><td>  0.5883560</td><td>  0.5882275</td><td> 0.010369037</td><td> 0.010146173</td><td>  0.5711747</td><td>  0.6053831</td><td>1.0002894</td><td> 9185.769</td><td>2727.709</td></tr>
	<tr><td>school_mu[26]</td><td>  0.5070336</td><td>  0.5072020</td><td> 0.015308408</td><td> 0.014958693</td><td>  0.4821989</td><td>  0.5320383</td><td>1.0011184</td><td> 9601.298</td><td>2389.797</td></tr>
	<tr><td>school_mu[27]</td><td>  0.6153622</td><td>  0.6153640</td><td> 0.015527387</td><td> 0.015326377</td><td>  0.5900032</td><td>  0.6408760</td><td>1.0014148</td><td> 9793.679</td><td>2783.556</td></tr>
	<tr><td>school_mu[28]</td><td>  0.6994129</td><td>  0.6996925</td><td> 0.014865654</td><td> 0.014537634</td><td>  0.6749133</td><td>  0.7232319</td><td>1.0053603</td><td> 9952.072</td><td>2730.345</td></tr>
	<tr><td>school_mu[29]</td><td>  0.6951703</td><td>  0.6954805</td><td> 0.014038333</td><td> 0.014172915</td><td>  0.6723685</td><td>  0.7179155</td><td>1.0009009</td><td> 9118.153</td><td>2701.306</td></tr>
	<tr><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td></tr>
	<tr><td>school_sigma_squared[111]</td><td>0.007893264</td><td>0.007768190</td><td>0.0010697738</td><td>0.0010081383</td><td>0.006439076</td><td>0.009800432</td><td>1.0004525</td><td> 7428.400</td><td>2527.758</td></tr>
	<tr><td>school_sigma_squared[112]</td><td>0.007969189</td><td>0.007832225</td><td>0.0010926129</td><td>0.0010291023</td><td>0.006428079</td><td>0.009930932</td><td>1.0020825</td><td>10505.973</td><td>2602.756</td></tr>
	<tr><td>school_sigma_squared[113]</td><td>0.007618596</td><td>0.007507175</td><td>0.0010481282</td><td>0.0010130680</td><td>0.006157625</td><td>0.009520502</td><td>1.0014516</td><td> 8158.273</td><td>2472.058</td></tr>
	<tr><td>school_sigma_squared[114]</td><td>0.007964497</td><td>0.007842500</td><td>0.0010674834</td><td>0.0010013036</td><td>0.006464247</td><td>0.009853104</td><td>1.0000604</td><td> 8319.391</td><td>2477.557</td></tr>
	<tr><td>school_sigma_squared[115]</td><td>0.007830389</td><td>0.007684080</td><td>0.0010859503</td><td>0.0010140984</td><td>0.006311180</td><td>0.009815478</td><td>1.0037708</td><td> 8275.381</td><td>2041.495</td></tr>
	<tr><td>school_sigma_squared[116]</td><td>0.007643599</td><td>0.007525235</td><td>0.0010180235</td><td>0.0009446608</td><td>0.006205853</td><td>0.009519544</td><td>1.0012818</td><td> 9034.527</td><td>3076.640</td></tr>
	<tr><td>school_sigma_squared[117]</td><td>0.007079024</td><td>0.006956720</td><td>0.0009694878</td><td>0.0008953644</td><td>0.005748352</td><td>0.008871571</td><td>1.0016213</td><td> 9660.773</td><td>2506.069</td></tr>
	<tr><td>school_sigma_squared[118]</td><td>0.007978155</td><td>0.007838450</td><td>0.0010765993</td><td>0.0010081087</td><td>0.006465149</td><td>0.009911454</td><td>1.0020249</td><td> 8893.435</td><td>2733.333</td></tr>
	<tr><td>school_sigma_squared[119]</td><td>0.007435998</td><td>0.007330955</td><td>0.0009979564</td><td>0.0009291677</td><td>0.005993480</td><td>0.009225692</td><td>1.0004015</td><td> 8705.208</td><td>2244.065</td></tr>
	<tr><td>school_sigma_squared[120]</td><td>0.007003157</td><td>0.006878335</td><td>0.0009683727</td><td>0.0008945860</td><td>0.005693553</td><td>0.008771605</td><td>1.0006612</td><td>10321.591</td><td>2666.727</td></tr>
	<tr><td>school_sigma_squared[121]</td><td>0.007845839</td><td>0.007733620</td><td>0.0010310463</td><td>0.0009563511</td><td>0.006429796</td><td>0.009630830</td><td>1.0029224</td><td> 9922.761</td><td>2363.052</td></tr>
	<tr><td>school_sigma_squared[122]</td><td>0.007879970</td><td>0.007717540</td><td>0.0011086189</td><td>0.0009984718</td><td>0.006355423</td><td>0.009884213</td><td>1.0027917</td><td> 9441.005</td><td>2877.827</td></tr>
	<tr><td>school_sigma_squared[123]</td><td>0.007090519</td><td>0.006984445</td><td>0.0009657778</td><td>0.0009240230</td><td>0.005747343</td><td>0.008932001</td><td>1.0010618</td><td>10143.593</td><td>2668.185</td></tr>
	<tr><td>school_sigma_squared[124]</td><td>0.008151195</td><td>0.008004090</td><td>0.0011242317</td><td>0.0010409186</td><td>0.006603203</td><td>0.010195930</td><td>0.9999701</td><td> 9655.258</td><td>2639.273</td></tr>
	<tr><td>school_sigma_squared[125]</td><td>0.008142819</td><td>0.008005325</td><td>0.0010949668</td><td>0.0010205032</td><td>0.006658687</td><td>0.010109410</td><td>1.0020682</td><td>10818.940</td><td>2288.183</td></tr>
	<tr><td>school_sigma_squared[126]</td><td>0.007719722</td><td>0.007619380</td><td>0.0010202034</td><td>0.0009789830</td><td>0.006292084</td><td>0.009589083</td><td>1.0026693</td><td> 7682.836</td><td>2778.122</td></tr>
	<tr><td>school_sigma_squared[127]</td><td>0.008047316</td><td>0.007917465</td><td>0.0010627631</td><td>0.0010092132</td><td>0.006559594</td><td>0.009984389</td><td>1.0030703</td><td>10158.718</td><td>2560.377</td></tr>
	<tr><td>school_sigma_squared[128]</td><td>0.007639193</td><td>0.007519170</td><td>0.0010104833</td><td>0.0009244826</td><td>0.006201755</td><td>0.009444058</td><td>1.0009677</td><td> 9342.876</td><td>2821.260</td></tr>
	<tr><td>school_sigma_squared[129]</td><td>0.008200299</td><td>0.008042745</td><td>0.0011332436</td><td>0.0010339059</td><td>0.006623680</td><td>0.010261805</td><td>0.9997888</td><td> 9525.584</td><td>2875.477</td></tr>
	<tr><td>school_sigma_squared[130]</td><td>0.007805796</td><td>0.007658680</td><td>0.0010914395</td><td>0.0009610139</td><td>0.006333933</td><td>0.009777402</td><td>1.0011799</td><td> 6632.328</td><td>2140.112</td></tr>
	<tr><td>school_sigma_squared[131]</td><td>0.007209483</td><td>0.007093005</td><td>0.0010073930</td><td>0.0009162839</td><td>0.005841421</td><td>0.009100803</td><td>1.0009968</td><td> 8307.831</td><td>2324.168</td></tr>
	<tr><td>school_sigma_squared[132]</td><td>0.007963293</td><td>0.007820475</td><td>0.0010980682</td><td>0.0009929862</td><td>0.006425254</td><td>0.009945242</td><td>1.0013978</td><td> 9306.196</td><td>2473.790</td></tr>
	<tr><td>school_sigma_squared[133]</td><td>0.008199732</td><td>0.008062010</td><td>0.0011416851</td><td>0.0010541953</td><td>0.006616617</td><td>0.010259080</td><td>1.0001760</td><td> 8278.864</td><td>2319.211</td></tr>
	<tr><td>school_sigma_squared[134]</td><td>0.007685228</td><td>0.007556640</td><td>0.0010438796</td><td>0.0009747502</td><td>0.006244291</td><td>0.009554043</td><td>1.0022049</td><td> 7625.178</td><td>2862.585</td></tr>
	<tr><td>school_sigma_squared[135]</td><td>0.007994192</td><td>0.007853765</td><td>0.0010924612</td><td>0.0010112296</td><td>0.006505752</td><td>0.010028570</td><td>1.0015995</td><td> 7389.714</td><td>2102.009</td></tr>
	<tr><td>school_sigma_squared[136]</td><td>0.008093561</td><td>0.007955880</td><td>0.0011403109</td><td>0.0010455888</td><td>0.006541122</td><td>0.010090635</td><td>1.0010682</td><td> 9287.799</td><td>2156.026</td></tr>
	<tr><td>school_sigma_squared[137]</td><td>0.005750439</td><td>0.005664375</td><td>0.0007842457</td><td>0.0007583647</td><td>0.004663566</td><td>0.007139022</td><td>0.9996415</td><td> 9412.067</td><td>2355.305</td></tr>
	<tr><td>school_sigma_squared[138]</td><td>0.006652218</td><td>0.006531960</td><td>0.0008836756</td><td>0.0008276392</td><td>0.005436707</td><td>0.008254424</td><td>1.0006992</td><td> 8224.799</td><td>2692.735</td></tr>
	<tr><td>school_sigma_squared[139]</td><td>0.005245804</td><td>0.005143150</td><td>0.0007534517</td><td>0.0007090460</td><td>0.004210688</td><td>0.006630924</td><td>1.0002898</td><td> 9417.638</td><td>2560.559</td></tr>
	<tr><td>school_sigma_squared[140]</td><td>0.007339370</td><td>0.007229320</td><td>0.0009939939</td><td>0.0009337711</td><td>0.005963415</td><td>0.009117067</td><td>0.9999096</td><td> 9246.506</td><td>2855.895</td></tr>
</tbody>
</table>

```r
generate_school_plot <- function(fit) {
    draws <- as_draws_matrix(fit)

    plot_df <- data.frame(
        school = filtered_schools_df$`School Code`,
        students = filtered_schools_df$`2016Sch Students Writing`,
        observed_mean = filtered_schools_df$`2016Sch Exam Average %` / 100,
        observed_lower = filtered_schools_df$`2016Sch Exam Average %` / 100 - filtered_schools_df$`2016Sch Exam Standard Deviation %` / 100,
        observed_upper = filtered_schools_df$`2016Sch Exam Average %` / 100 + filtered_schools_df$`2016Sch Exam Standard Deviation %` / 100,
        model_mean = colMeans(draws[, grep('school_mu', colnames(draws))]),
        model_lower = apply(draws[, grep('school_mu', colnames(draws))], 2, function(col) quantile(col, 0.025)),
        model_upper = apply(draws[, grep('school_mu', colnames(draws))], 2, function(col) quantile(col, 0.975))
    )
    plot_df <- plot_df[order(plot_df$observed_mean), ]
    plot_df$school <- factor(plot_df$school, levels = plot_df$school)
    # plot the empirical data against the estimated means
    p <- ggplot(plot_df) +
        geom_point(aes(school, observed_mean, size = students, colour = "Observed")) +
        geom_point(aes(school, model_mean, colour = 'Model')) +
        geom_errorbar(aes(x = school, y = model_mean, ymin = model_lower, ymax = model_upper, colour = "Model")) +
        labs(x = "School", y = "Mean Score", size = "Number of Students", colour = "") +
        scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
        theme_bw() +  # Set background to white
        theme(
            panel.grid.major.x = element_blank(),
            panel.grid.minor.x = element_blank(),
            panel.grid.major.y = element_line(size = 0.5, linetype = 'dashed', colour = "grey"),
            axis.ticks.x = element_blank(),
            axis.text.x = element_blank(),
        )
    p
}

unpooled_school_means_plot <- generate_school_plot(alberta_schools_unpooled_fit)
print(unpooled_school_means_plot)
```

![png](/2024-12-02-hierarchical-bayesian-models/output_73_0.png)

That looks pretty good! Now let's pool all of the schools together using a shared prior.

```r
alberta_schools_pooled_code <- "
data {
    int<lower = 0> N_schools;
    array[N_schools] real<lower = 0, upper = 1> school_mean;
    array[N_schools] int<lower = 0> school_n;
}
parameters {
    array[N_schools] real<lower = 0, upper = 1> school_mu;
    array[N_schools] real<lower = 0> school_nu_raw; // non-centred - implies school_nu ~ normal(school_prior_nu_mean, school_prior_nu_sd)

    real <lower = 0> school_prior_alpha;
    real <lower = 0> school_prior_beta;
    real <lower = 0> school_prior_nu_mean;
    real <lower = 0> school_prior_nu_sd;
}
transformed parameters {
    array[N_schools] real<lower = 0> school_alpha;
    array[N_schools] real<lower = 0> school_beta;
    array[N_schools] real<lower = 0> school_sigma_squared;
    array[N_schools] real<lower = 0> school_nu;
    for (i in 1:N_schools) {
        school_nu[i] = school_prior_nu_mean + school_prior_nu_sd * school_nu_raw[i];
        school_alpha[i] = school_mu[i] * school_nu[i];
        school_beta[i] = (1 - school_mu[i]) * school_nu[i];
        school_sigma_squared[i] = (school_alpha[i] * school_beta[i]) / (( school_alpha[i] + school_beta[i])^2 * (school_alpha[i] + school_beta[i] + 1));
    }
}
model {
    for (i in 1:N_schools) {
        school_mean[i] ~ normal(school_mu[i], sqrt(school_sigma_squared[i] / school_n[i]));
    }
    school_mu ~ beta(school_prior_alpha, school_prior_beta);
    school_nu_raw ~ std_normal();

    school_prior_alpha ~ normal(3, 0.5);
    school_prior_beta ~ normal(1, 0.3);
    school_prior_nu_mean ~ normal(30, 4);
    school_prior_nu_sd ~ exponential(1);
}
"

alberta_schools_pooled_fit <- run_schools_model(alberta_schools_pooled_code)
alberta_schools_pooled_fit$summary()
```

    Running MCMC with 4 sequential chains...

    All 4 chains finished successfully.
    Mean chain execution time: 7.3 seconds.
    Total execution time: 29.3 seconds.

<table class="dataframe">
<caption>A draws_summary: 845 × 10</caption>
<thead>
	<tr><th scope=col>variable</th><th scope=col>mean</th><th scope=col>median</th><th scope=col>sd</th><th scope=col>mad</th><th scope=col>q5</th><th scope=col>q95</th><th scope=col>rhat</th><th scope=col>ess_bulk</th><th scope=col>ess_tail</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>lp__         </td><td>303.3768817</td><td>303.9490000</td><td>16.010609953</td><td>15.280416900</td><td>276.3478500</td><td>328.5250000</td><td>1.0015113</td><td> 893.8268</td><td>1506.195</td></tr>
	<tr><td>school_mu[1] </td><td>  0.6390792</td><td>  0.6389565</td><td> 0.008087173</td><td> 0.008065344</td><td>  0.6256816</td><td>  0.6524580</td><td>1.0024593</td><td>4588.5802</td><td>3114.740</td></tr>
	<tr><td>school_mu[2] </td><td>  0.8472796</td><td>  0.8473785</td><td> 0.008252892</td><td> 0.008267719</td><td>  0.8334421</td><td>  0.8606413</td><td>1.0009509</td><td>4664.1656</td><td>2717.473</td></tr>
	<tr><td>school_mu[3] </td><td>  0.6180220</td><td>  0.6181105</td><td> 0.006271633</td><td> 0.006166133</td><td>  0.6076868</td><td>  0.6283191</td><td>1.0017390</td><td>4661.0568</td><td>3093.812</td></tr>
	<tr><td>school_mu[4] </td><td>  0.6220444</td><td>  0.6221355</td><td> 0.008126488</td><td> 0.008079429</td><td>  0.6084968</td><td>  0.6352612</td><td>1.0018828</td><td>4967.9453</td><td>3136.635</td></tr>
	<tr><td>school_mu[5] </td><td>  0.6090356</td><td>  0.6091480</td><td> 0.010636975</td><td> 0.010635431</td><td>  0.5912527</td><td>  0.6262207</td><td>1.0002508</td><td>4984.4110</td><td>2805.612</td></tr>
	<tr><td>school_mu[6] </td><td>  0.5643344</td><td>  0.5645605</td><td> 0.011741694</td><td> 0.011797048</td><td>  0.5449506</td><td>  0.5838678</td><td>1.0006932</td><td>4318.7214</td><td>2945.927</td></tr>
	<tr><td>school_mu[7] </td><td>  0.7572024</td><td>  0.7575620</td><td> 0.013173178</td><td> 0.013160299</td><td>  0.7349491</td><td>  0.7783756</td><td>0.9999079</td><td>4704.4222</td><td>2625.790</td></tr>
	<tr><td>school_mu[8] </td><td>  0.6605515</td><td>  0.6607250</td><td> 0.015465255</td><td> 0.015314517</td><td>  0.6343163</td><td>  0.6858114</td><td>1.0002815</td><td>4391.0870</td><td>2871.989</td></tr>
	<tr><td>school_mu[9] </td><td>  0.5038833</td><td>  0.5039180</td><td> 0.015056639</td><td> 0.015186272</td><td>  0.4792564</td><td>  0.5281737</td><td>1.0010799</td><td>5395.6317</td><td>2740.259</td></tr>
	<tr><td>school_mu[10]</td><td>  0.5492591</td><td>  0.5494235</td><td> 0.010111278</td><td> 0.010022376</td><td>  0.5324129</td><td>  0.5659195</td><td>1.0012927</td><td>4671.2267</td><td>2758.982</td></tr>
	<tr><td>school_mu[11]</td><td>  0.6073463</td><td>  0.6074625</td><td> 0.013313283</td><td> 0.013341917</td><td>  0.5854852</td><td>  0.6290895</td><td>1.0020000</td><td>4909.1898</td><td>2668.409</td></tr>
	<tr><td>school_mu[12]</td><td>  0.6782184</td><td>  0.6787230</td><td> 0.014706708</td><td> 0.015006136</td><td>  0.6538240</td><td>  0.7014432</td><td>1.0012839</td><td>4657.2681</td><td>2982.858</td></tr>
	<tr><td>school_mu[13]</td><td>  0.7765780</td><td>  0.7767805</td><td> 0.008369508</td><td> 0.008294406</td><td>  0.7624945</td><td>  0.7903953</td><td>1.0022197</td><td>4809.6645</td><td>2783.120</td></tr>
	<tr><td>school_mu[14]</td><td>  0.5941792</td><td>  0.5943005</td><td> 0.009515127</td><td> 0.009766628</td><td>  0.5786709</td><td>  0.6097708</td><td>1.0023599</td><td>5141.7190</td><td>2850.491</td></tr>
	<tr><td>school_mu[15]</td><td>  0.5822526</td><td>  0.5823935</td><td> 0.010862116</td><td> 0.010788880</td><td>  0.5644139</td><td>  0.6000414</td><td>0.9997710</td><td>5552.0371</td><td>3009.097</td></tr>
	<tr><td>school_mu[16]</td><td>  0.5612144</td><td>  0.5611465</td><td> 0.009131184</td><td> 0.009202498</td><td>  0.5463539</td><td>  0.5758237</td><td>1.0022781</td><td>4576.8798</td><td>2877.150</td></tr>
	<tr><td>school_mu[17]</td><td>  0.6560447</td><td>  0.6561910</td><td> 0.010477979</td><td> 0.010462708</td><td>  0.6388660</td><td>  0.6728194</td><td>1.0020644</td><td>4727.2855</td><td>2872.770</td></tr>
	<tr><td>school_mu[18]</td><td>  0.7019719</td><td>  0.7019980</td><td> 0.004950784</td><td> 0.004878495</td><td>  0.6937125</td><td>  0.7101738</td><td>1.0000035</td><td>4318.3077</td><td>3191.356</td></tr>
	<tr><td>school_mu[19]</td><td>  0.5690055</td><td>  0.5690850</td><td> 0.007141884</td><td> 0.007216556</td><td>  0.5573088</td><td>  0.5803989</td><td>0.9995899</td><td>4456.1963</td><td>3119.883</td></tr>
	<tr><td>school_mu[20]</td><td>  0.6287745</td><td>  0.6287395</td><td> 0.007553180</td><td> 0.007547175</td><td>  0.6164030</td><td>  0.6412437</td><td>0.9994805</td><td>4260.8254</td><td>3093.037</td></tr>
	<tr><td>school_mu[21]</td><td>  0.5293484</td><td>  0.5295380</td><td> 0.009045090</td><td> 0.009111318</td><td>  0.5146197</td><td>  0.5441755</td><td>1.0006101</td><td>5183.6144</td><td>3166.340</td></tr>
	<tr><td>school_mu[22]</td><td>  0.6478409</td><td>  0.6479130</td><td> 0.010385516</td><td> 0.010494584</td><td>  0.6308290</td><td>  0.6643548</td><td>1.0005523</td><td>4699.0893</td><td>3190.544</td></tr>
	<tr><td>school_mu[23]</td><td>  0.5893679</td><td>  0.5892725</td><td> 0.010550171</td><td> 0.010570197</td><td>  0.5720445</td><td>  0.6067484</td><td>1.0017835</td><td>5601.2755</td><td>3042.860</td></tr>
	<tr><td>school_mu[24]</td><td>  0.5410172</td><td>  0.5408530</td><td> 0.008148151</td><td> 0.008352227</td><td>  0.5278048</td><td>  0.5544735</td><td>0.9993166</td><td>4670.5756</td><td>2990.563</td></tr>
	<tr><td>school_mu[25]</td><td>  0.5877308</td><td>  0.5877460</td><td> 0.009933401</td><td> 0.009825932</td><td>  0.5711710</td><td>  0.6040176</td><td>1.0008139</td><td>4943.8628</td><td>2533.125</td></tr>
	<tr><td>school_mu[26]</td><td>  0.5065683</td><td>  0.5063280</td><td> 0.015377681</td><td> 0.015707406</td><td>  0.4820062</td><td>  0.5320932</td><td>1.0022437</td><td>5312.7353</td><td>2943.792</td></tr>
	<tr><td>school_mu[27]</td><td>  0.6150520</td><td>  0.6149875</td><td> 0.015574998</td><td> 0.015925348</td><td>  0.5894119</td><td>  0.6402502</td><td>1.0002420</td><td>4431.5376</td><td>2993.436</td></tr>
	<tr><td>school_mu[28]</td><td>  0.6987703</td><td>  0.6987035</td><td> 0.014475063</td><td> 0.014868254</td><td>  0.6752261</td><td>  0.7222509</td><td>1.0011157</td><td>4728.1448</td><td>2926.576</td></tr>
	<tr><td>school_mu[29]</td><td>  0.6943627</td><td>  0.6943935</td><td> 0.013998895</td><td> 0.013949783</td><td>  0.6707471</td><td>  0.7169856</td><td>1.0006656</td><td>4834.9427</td><td>2654.505</td></tr>
	<tr><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td></tr>
	<tr><td>school_nu[111]</td><td>30.78090</td><td>30.82385</td><td>4.101406</td><td>4.041642</td><td>24.03228</td><td>37.58628</td><td>1.0005771</td><td>1472.580</td><td>1875.910</td></tr>
	<tr><td>school_nu[112]</td><td>30.80212</td><td>30.71015</td><td>4.155457</td><td>4.101242</td><td>23.99994</td><td>37.52887</td><td>1.0003763</td><td>1475.403</td><td>1967.981</td></tr>
	<tr><td>school_nu[113]</td><td>30.78881</td><td>30.76595</td><td>4.128469</td><td>4.117773</td><td>24.13262</td><td>37.50174</td><td>0.9999277</td><td>1471.802</td><td>1808.811</td></tr>
	<tr><td>school_nu[114]</td><td>30.80189</td><td>30.78960</td><td>4.130428</td><td>4.069737</td><td>24.06187</td><td>37.53622</td><td>1.0002736</td><td>1472.135</td><td>1782.622</td></tr>
	<tr><td>school_nu[115]</td><td>30.78738</td><td>30.75695</td><td>4.115737</td><td>4.065586</td><td>24.05419</td><td>37.54105</td><td>1.0001634</td><td>1463.730</td><td>1951.738</td></tr>
	<tr><td>school_nu[116]</td><td>30.76124</td><td>30.75665</td><td>4.130047</td><td>4.096424</td><td>24.02190</td><td>37.54741</td><td>1.0001140</td><td>1467.214</td><td>1807.532</td></tr>
	<tr><td>school_nu[117]</td><td>30.78732</td><td>30.77025</td><td>4.105511</td><td>4.035860</td><td>24.06202</td><td>37.46641</td><td>0.9998391</td><td>1457.559</td><td>1697.574</td></tr>
	<tr><td>school_nu[118]</td><td>30.77963</td><td>30.77405</td><td>4.118421</td><td>4.077076</td><td>24.03529</td><td>37.62413</td><td>1.0000245</td><td>1453.870</td><td>1776.225</td></tr>
	<tr><td>school_nu[119]</td><td>30.78651</td><td>30.78055</td><td>4.138759</td><td>4.055356</td><td>24.06464</td><td>37.46353</td><td>1.0001119</td><td>1451.447</td><td>1861.304</td></tr>
	<tr><td>school_nu[120]</td><td>30.80518</td><td>30.83210</td><td>4.136719</td><td>4.043866</td><td>24.02471</td><td>37.53602</td><td>1.0003245</td><td>1428.196</td><td>1799.062</td></tr>
	<tr><td>school_nu[121]</td><td>30.79084</td><td>30.74740</td><td>4.132359</td><td>4.059729</td><td>24.09940</td><td>37.46145</td><td>1.0002736</td><td>1447.110</td><td>1900.183</td></tr>
	<tr><td>school_nu[122]</td><td>30.76768</td><td>30.79925</td><td>4.095244</td><td>4.018810</td><td>24.09209</td><td>37.46993</td><td>1.0000350</td><td>1452.188</td><td>1818.884</td></tr>
	<tr><td>school_nu[123]</td><td>30.79588</td><td>30.80065</td><td>4.115233</td><td>4.056764</td><td>24.06658</td><td>37.54259</td><td>0.9998784</td><td>1483.732</td><td>1780.509</td></tr>
	<tr><td>school_nu[124]</td><td>30.78983</td><td>30.80970</td><td>4.140070</td><td>4.113325</td><td>24.04521</td><td>37.54612</td><td>1.0003622</td><td>1448.044</td><td>1807.375</td></tr>
	<tr><td>school_nu[125]</td><td>30.79457</td><td>30.79990</td><td>4.119491</td><td>4.058766</td><td>24.09196</td><td>37.57005</td><td>1.0003071</td><td>1460.175</td><td>1883.421</td></tr>
	<tr><td>school_nu[126]</td><td>30.78053</td><td>30.81370</td><td>4.110078</td><td>4.089307</td><td>24.12297</td><td>37.50183</td><td>1.0004938</td><td>1418.450</td><td>1938.605</td></tr>
	<tr><td>school_nu[127]</td><td>30.79112</td><td>30.80010</td><td>4.137164</td><td>4.091902</td><td>24.13109</td><td>37.51491</td><td>1.0001893</td><td>1456.566</td><td>1874.482</td></tr>
	<tr><td>school_nu[128]</td><td>30.78242</td><td>30.79370</td><td>4.099799</td><td>4.035415</td><td>24.08486</td><td>37.60762</td><td>1.0001670</td><td>1452.210</td><td>1833.954</td></tr>
	<tr><td>school_nu[129]</td><td>30.77612</td><td>30.77305</td><td>4.095918</td><td>4.020292</td><td>24.08069</td><td>37.46192</td><td>1.0002709</td><td>1454.949</td><td>1808.966</td></tr>
	<tr><td>school_nu[130]</td><td>30.79206</td><td>30.78095</td><td>4.135395</td><td>4.103392</td><td>24.04835</td><td>37.42886</td><td>0.9998866</td><td>1433.656</td><td>1889.972</td></tr>
	<tr><td>school_nu[131]</td><td>30.79639</td><td>30.81580</td><td>4.106577</td><td>4.074111</td><td>24.04705</td><td>37.46138</td><td>0.9998806</td><td>1474.317</td><td>1819.319</td></tr>
	<tr><td>school_nu[132]</td><td>30.78464</td><td>30.79790</td><td>4.111246</td><td>4.040826</td><td>24.02001</td><td>37.51579</td><td>0.9998444</td><td>1496.896</td><td>1940.522</td></tr>
	<tr><td>school_nu[133]</td><td>30.79749</td><td>30.78565</td><td>4.114845</td><td>4.090864</td><td>24.09493</td><td>37.53969</td><td>1.0000261</td><td>1491.218</td><td>1883.304</td></tr>
	<tr><td>school_nu[134]</td><td>30.78970</td><td>30.75950</td><td>4.146862</td><td>4.154319</td><td>24.02222</td><td>37.48786</td><td>1.0003382</td><td>1421.417</td><td>1925.859</td></tr>
	<tr><td>school_nu[135]</td><td>30.77191</td><td>30.77215</td><td>4.163201</td><td>4.090197</td><td>24.00241</td><td>37.47392</td><td>1.0007963</td><td>1412.177</td><td>1826.859</td></tr>
	<tr><td>school_nu[136]</td><td>30.80711</td><td>30.77620</td><td>4.134148</td><td>4.106061</td><td>24.03661</td><td>37.54306</td><td>0.9999799</td><td>1442.295</td><td>1972.031</td></tr>
	<tr><td>school_nu[137]</td><td>30.81039</td><td>30.78280</td><td>4.113771</td><td>4.062472</td><td>24.05631</td><td>37.48475</td><td>0.9999788</td><td>1464.940</td><td>1851.897</td></tr>
	<tr><td>school_nu[138]</td><td>30.77849</td><td>30.77695</td><td>4.106998</td><td>4.029484</td><td>24.10759</td><td>37.62079</td><td>1.0007396</td><td>1448.066</td><td>1733.536</td></tr>
	<tr><td>school_nu[139]</td><td>30.75703</td><td>30.80815</td><td>4.117619</td><td>4.071442</td><td>24.02906</td><td>37.45361</td><td>0.9999884</td><td>1477.264</td><td>1725.516</td></tr>
	<tr><td>school_nu[140]</td><td>30.77726</td><td>30.80615</td><td>4.108771</td><td>4.063658</td><td>24.04887</td><td>37.55635</td><td>1.0000692</td><td>1453.901</td><td>1852.164</td></tr>
</tbody>
</table>

```r
draws <- as_draws_matrix(alberta_schools_pooled_fit)
prior_mean <- mean(draws[, 'school_prior_alpha'] / (draws[, 'school_prior_alpha'] + draws[, 'school_prior_beta']))
pooled_school_means_plot <- generate_school_plot(alberta_schools_pooled_fit)
pooled_school_means_plot <- pooled_school_means_plot +
    geom_hline(yintercept = prior_mean, linetype = 'dashed')
print(pooled_school_means_plot)
```

![png](/2024-12-02-hierarchical-bayesian-models/output_76_0.png)

Great! So again we're doing a good job of capturing the data. This data is very similar to the unpooled estimate, probably because there's not a lot of variation explained by the different schools. Now let's pool all of the schools by district!

```r

alberta_schools_authority_pooled_code <- "
data {
    int<lower = 0> N_schools;
    int<lower = 0> N_authorities;
    array[N_schools] real<lower = 0, upper = 1> school_mean;
    array[N_schools] int<lower = 0> school_n;
    array[N_schools] int<lower = 1, upper = N_authorities> authority_index;
}
parameters {
    array[N_schools] real<lower = 0, upper = 1> school_mu;
    array[N_schools] real<lower = 0> school_nu_raw;

    real<lower = 0> authority_prior_alpha_mean;
    real<lower = 0> authority_prior_alpha_sd;
    array[N_authorities] real<lower = 0> school_prior_alpha_raw;

    real<lower = 0> authority_prior_beta_mean;
    real<lower = 0> authority_prior_beta_sd;
    array[N_authorities] real<lower = 0> school_prior_beta_raw;

    real <lower = 0> school_prior_nu_mean;
    real <lower = 0> school_prior_nu_sd;
}
transformed parameters {
    array[N_schools] real<lower = 0> school_alpha;
    array[N_schools] real<lower = 0> school_beta;
    array[N_schools] real<lower = 0> school_sigma_squared;
    array[N_schools] real<lower = 0> school_nu;
    array[N_authorities] real<lower = 0> school_prior_alpha;
    array[N_authorities] real<lower = 0> school_prior_beta;

    for (i in 1:N_authorities) {
        school_prior_alpha[i] = authority_prior_beta_mean + authority_prior_beta_sd * school_prior_beta_raw[i];
        school_prior_beta[i] = authority_prior_alpha_mean + authority_prior_alpha_sd * school_prior_alpha_raw[i];
    }
    for (i in 1:N_schools) {
        school_nu[i] = school_prior_nu_mean + school_prior_nu_sd * school_nu_raw[i];
        school_alpha[i] = school_mu[i] * school_nu[i];
        school_beta[i] = (1 - school_mu[i]) * school_nu[i];
        school_sigma_squared[i] = (school_alpha[i] * school_beta[i]) / (( school_alpha[i] + school_beta[i])^2 * (school_alpha[i] + school_beta[i] + 1));
    }
}
model {
    for (i in 1:N_schools) {
        school_mu[i] ~ beta(school_prior_alpha[authority_index[i]], school_prior_beta[authority_index[i]]);
        school_mean[i] ~ normal(school_mu[i], sqrt(school_sigma_squared[i] / school_n[i]));
    }
    school_nu_raw ~ std_normal(); // non-centred - implies school_nu ~ normal(school_prior_nu_mean, school_prior_nu_sd)

    // TODO create a shared prior for the hyperparameters alpha and beta
    authority_prior_alpha_mean ~ normal(3, 0.5);
    authority_prior_alpha_sd ~ exponential(1);
    authority_prior_beta_mean ~ normal(1, 0.3);
    authority_prior_beta_sd ~ exponential(1);

    school_prior_alpha_raw ~ std_normal();
    school_prior_beta_raw ~ std_normal();

    school_prior_nu_mean ~ normal(30, 4);
    school_prior_nu_sd ~ exponential(1);
}
"
alberta_schools_authority_fit <- run_schools_model(alberta_schools_authority_pooled_code)
alberta_schools_authority_fit$summary()
```

    Running MCMC with 4 sequential chains...

    All 4 chains finished successfully.
    Mean chain execution time: 14.9 seconds.
    Total execution time: 60.0 seconds.

<table class="dataframe">
<caption>A draws_summary: 1067 × 10</caption>
<thead>
	<tr><th scope=col>variable</th><th scope=col>mean</th><th scope=col>median</th><th scope=col>sd</th><th scope=col>mad</th><th scope=col>q5</th><th scope=col>q95</th><th scope=col>rhat</th><th scope=col>ess_bulk</th><th scope=col>ess_tail</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>lp__         </td><td>242.7581233</td><td>243.4775000</td><td>20.319465354</td><td>19.953572100</td><td>208.5067000</td><td>275.4238000</td><td>1.0037834</td><td> 866.746</td><td>1539.503</td></tr>
	<tr><td>school_mu[1] </td><td>  0.6387844</td><td>  0.6387405</td><td> 0.007867415</td><td> 0.007838506</td><td>  0.6258293</td><td>  0.6516180</td><td>1.0017875</td><td>7730.782</td><td>3023.918</td></tr>
	<tr><td>school_mu[2] </td><td>  0.8468010</td><td>  0.8471110</td><td> 0.008234859</td><td> 0.008496039</td><td>  0.8331503</td><td>  0.8597739</td><td>1.0019272</td><td>8346.506</td><td>2944.039</td></tr>
	<tr><td>school_mu[3] </td><td>  0.6178737</td><td>  0.6180900</td><td> 0.006078236</td><td> 0.006126845</td><td>  0.6077802</td><td>  0.6278174</td><td>1.0005921</td><td>7897.363</td><td>3082.192</td></tr>
	<tr><td>school_mu[4] </td><td>  0.6220775</td><td>  0.6221365</td><td> 0.008252685</td><td> 0.008003816</td><td>  0.6084058</td><td>  0.6355993</td><td>1.0035225</td><td>9066.323</td><td>2903.928</td></tr>
	<tr><td>school_mu[5] </td><td>  0.6089325</td><td>  0.6090580</td><td> 0.010396388</td><td> 0.010213631</td><td>  0.5917600</td><td>  0.6258283</td><td>1.0004491</td><td>8822.524</td><td>2701.826</td></tr>
	<tr><td>school_mu[6] </td><td>  0.5651614</td><td>  0.5651690</td><td> 0.012056050</td><td> 0.012080966</td><td>  0.5459932</td><td>  0.5843686</td><td>1.0016742</td><td>8920.377</td><td>2358.078</td></tr>
	<tr><td>school_mu[7] </td><td>  0.7564602</td><td>  0.7566715</td><td> 0.013304278</td><td> 0.013247031</td><td>  0.7337154</td><td>  0.7776436</td><td>1.0003112</td><td>8465.891</td><td>2869.356</td></tr>
	<tr><td>school_mu[8] </td><td>  0.6607885</td><td>  0.6612545</td><td> 0.015222589</td><td> 0.015111400</td><td>  0.6355575</td><td>  0.6852125</td><td>1.0003871</td><td>7745.071</td><td>3102.663</td></tr>
	<tr><td>school_mu[9] </td><td>  0.5033227</td><td>  0.5035615</td><td> 0.014959102</td><td> 0.014415320</td><td>  0.4786364</td><td>  0.5275542</td><td>1.0018842</td><td>7362.804</td><td>2435.936</td></tr>
	<tr><td>school_mu[10]</td><td>  0.5489648</td><td>  0.5489295</td><td> 0.009962331</td><td> 0.010085386</td><td>  0.5327384</td><td>  0.5654756</td><td>1.0009309</td><td>7858.609</td><td>2480.194</td></tr>
	<tr><td>school_mu[11]</td><td>  0.6069848</td><td>  0.6070440</td><td> 0.013525705</td><td> 0.012806699</td><td>  0.5846459</td><td>  0.6296254</td><td>1.0003953</td><td>7109.660</td><td>2533.558</td></tr>
	<tr><td>school_mu[12]</td><td>  0.6785647</td><td>  0.6788500</td><td> 0.014326434</td><td> 0.014209238</td><td>  0.6543459</td><td>  0.7016713</td><td>1.0013475</td><td>8032.309</td><td>2550.878</td></tr>
	<tr><td>school_mu[13]</td><td>  0.7764559</td><td>  0.7766735</td><td> 0.008665420</td><td> 0.008676916</td><td>  0.7621878</td><td>  0.7902724</td><td>1.0022818</td><td>8470.686</td><td>2569.698</td></tr>
	<tr><td>school_mu[14]</td><td>  0.5940918</td><td>  0.5941210</td><td> 0.009433348</td><td> 0.009140970</td><td>  0.5780491</td><td>  0.6095894</td><td>0.9994629</td><td>7222.579</td><td>2868.847</td></tr>
	<tr><td>school_mu[15]</td><td>  0.5822622</td><td>  0.5822365</td><td> 0.010469228</td><td> 0.010771089</td><td>  0.5654695</td><td>  0.5993273</td><td>1.0011668</td><td>8890.172</td><td>2870.622</td></tr>
	<tr><td>school_mu[16]</td><td>  0.5611338</td><td>  0.5611185</td><td> 0.008928162</td><td> 0.008979367</td><td>  0.5461858</td><td>  0.5759718</td><td>0.9999743</td><td>8275.079</td><td>2942.549</td></tr>
	<tr><td>school_mu[17]</td><td>  0.6552331</td><td>  0.6551580</td><td> 0.010271325</td><td> 0.010408593</td><td>  0.6387280</td><td>  0.6719518</td><td>1.0008111</td><td>8512.814</td><td>2635.261</td></tr>
	<tr><td>school_mu[18]</td><td>  0.7017329</td><td>  0.7018120</td><td> 0.005121847</td><td> 0.005091248</td><td>  0.6931912</td><td>  0.7099870</td><td>1.0011110</td><td>7544.982</td><td>2962.647</td></tr>
	<tr><td>school_mu[19]</td><td>  0.5692686</td><td>  0.5692310</td><td> 0.007138546</td><td> 0.007034937</td><td>  0.5576670</td><td>  0.5809718</td><td>1.0041092</td><td>6968.875</td><td>2653.758</td></tr>
	<tr><td>school_mu[20]</td><td>  0.6290081</td><td>  0.6291435</td><td> 0.007791504</td><td> 0.007737689</td><td>  0.6161220</td><td>  0.6418232</td><td>1.0018235</td><td>7827.995</td><td>2969.588</td></tr>
	<tr><td>school_mu[21]</td><td>  0.5297266</td><td>  0.5297355</td><td> 0.009124199</td><td> 0.009122438</td><td>  0.5144827</td><td>  0.5445661</td><td>1.0005499</td><td>7307.825</td><td>2901.814</td></tr>
	<tr><td>school_mu[22]</td><td>  0.6477019</td><td>  0.6477230</td><td> 0.010225237</td><td> 0.010181756</td><td>  0.6304554</td><td>  0.6646334</td><td>1.0012374</td><td>7897.992</td><td>2363.115</td></tr>
	<tr><td>school_mu[23]</td><td>  0.5891082</td><td>  0.5892005</td><td> 0.010622697</td><td> 0.010529425</td><td>  0.5712892</td><td>  0.6062800</td><td>1.0007224</td><td>7841.715</td><td>2924.020</td></tr>
	<tr><td>school_mu[24]</td><td>  0.5413668</td><td>  0.5413110</td><td> 0.007999754</td><td> 0.007971199</td><td>  0.5283126</td><td>  0.5546806</td><td>1.0014882</td><td>8305.301</td><td>2780.133</td></tr>
	<tr><td>school_mu[25]</td><td>  0.5880985</td><td>  0.5882500</td><td> 0.010154796</td><td> 0.009871151</td><td>  0.5715252</td><td>  0.6044875</td><td>1.0009068</td><td>7350.320</td><td>2446.588</td></tr>
	<tr><td>school_mu[26]</td><td>  0.5064102</td><td>  0.5062810</td><td> 0.015608235</td><td> 0.015106953</td><td>  0.4805963</td><td>  0.5324869</td><td>1.0005418</td><td>6929.813</td><td>2712.310</td></tr>
	<tr><td>school_mu[27]</td><td>  0.6151159</td><td>  0.6152560</td><td> 0.015493198</td><td> 0.015774864</td><td>  0.5897355</td><td>  0.6402394</td><td>1.0003265</td><td>7670.134</td><td>2554.444</td></tr>
	<tr><td>school_mu[28]</td><td>  0.6982921</td><td>  0.6985970</td><td> 0.014558349</td><td> 0.015005395</td><td>  0.6741918</td><td>  0.7219588</td><td>1.0000773</td><td>8525.254</td><td>3075.386</td></tr>
	<tr><td>school_mu[29]</td><td>  0.6944085</td><td>  0.6943485</td><td> 0.013937068</td><td> 0.013428649</td><td>  0.6708920</td><td>  0.7171905</td><td>1.0034761</td><td>9790.319</td><td>2710.654</td></tr>
	<tr><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td><td>⋮</td></tr>
	<tr><td>school_prior_beta[26]</td><td>6.444429</td><td>5.945595</td><td>2.176390</td><td>1.812382</td><td>3.942815</td><td>10.682965</td><td>1.000358</td><td>2368.802</td><td>2829.265</td></tr>
	<tr><td>school_prior_beta[27]</td><td>6.228340</td><td>5.690555</td><td>2.115253</td><td>1.673648</td><td>3.876286</td><td>10.295395</td><td>1.000566</td><td>2573.989</td><td>2812.977</td></tr>
	<tr><td>school_prior_beta[28]</td><td>6.564124</td><td>6.159870</td><td>2.046347</td><td>1.858002</td><td>4.032383</td><td>10.587910</td><td>1.002567</td><td>1435.181</td><td>1861.186</td></tr>
	<tr><td>school_prior_beta[29]</td><td>6.679653</td><td>6.131620</td><td>2.304941</td><td>1.909085</td><td>4.031681</td><td>11.070340</td><td>1.001554</td><td>2155.847</td><td>2806.314</td></tr>
	<tr><td>school_prior_beta[30]</td><td>6.215432</td><td>5.779615</td><td>1.949213</td><td>1.717718</td><td>3.897775</td><td> 9.921474</td><td>1.000991</td><td>2442.833</td><td>2637.715</td></tr>
	<tr><td>school_prior_beta[31]</td><td>6.405481</td><td>5.840280</td><td>2.213723</td><td>1.831693</td><td>3.904279</td><td>10.745250</td><td>1.002140</td><td>2487.839</td><td>2745.415</td></tr>
	<tr><td>school_prior_beta[32]</td><td>6.358579</td><td>5.781295</td><td>2.259589</td><td>1.772270</td><td>3.870992</td><td>10.748180</td><td>1.000821</td><td>2536.184</td><td>2771.503</td></tr>
	<tr><td>school_prior_beta[33]</td><td>6.104454</td><td>5.684775</td><td>1.897604</td><td>1.599785</td><td>3.863385</td><td> 9.878326</td><td>1.000618</td><td>2249.636</td><td>2085.735</td></tr>
	<tr><td>school_prior_beta[34]</td><td>7.458583</td><td>7.225070</td><td>2.004222</td><td>1.917728</td><td>4.653268</td><td>11.136860</td><td>1.003457</td><td>1731.328</td><td>1917.717</td></tr>
	<tr><td>school_prior_beta[35]</td><td>6.945114</td><td>6.741595</td><td>1.839731</td><td>1.845919</td><td>4.452932</td><td>10.384055</td><td>1.000970</td><td>1898.579</td><td>2357.969</td></tr>
	<tr><td>school_prior_beta[36]</td><td>6.902518</td><td>6.354700</td><td>2.391516</td><td>2.096960</td><td>4.101835</td><td>11.606285</td><td>1.002352</td><td>1846.991</td><td>2092.054</td></tr>
	<tr><td>school_prior_beta[37]</td><td>6.405285</td><td>5.885545</td><td>2.142651</td><td>1.836156</td><td>3.931134</td><td>10.559210</td><td>1.001356</td><td>2221.362</td><td>2639.116</td></tr>
	<tr><td>school_prior_beta[38]</td><td>5.961819</td><td>5.485965</td><td>1.881591</td><td>1.508886</td><td>3.827024</td><td> 9.690220</td><td>1.001043</td><td>2653.897</td><td>2563.266</td></tr>
	<tr><td>school_prior_beta[39]</td><td>6.511898</td><td>6.020150</td><td>2.161627</td><td>1.885289</td><td>3.964761</td><td>10.635820</td><td>1.001996</td><td>1721.177</td><td>2229.240</td></tr>
	<tr><td>school_prior_beta[40]</td><td>6.412868</td><td>5.955380</td><td>2.122335</td><td>1.871167</td><td>3.949675</td><td>10.369350</td><td>1.000598</td><td>2339.874</td><td>2541.280</td></tr>
	<tr><td>school_prior_beta[41]</td><td>6.277202</td><td>5.778590</td><td>2.065970</td><td>1.698911</td><td>3.910159</td><td>10.228230</td><td>1.001257</td><td>2913.960</td><td>2810.728</td></tr>
	<tr><td>school_prior_beta[42]</td><td>7.714267</td><td>7.296960</td><td>2.467924</td><td>2.333805</td><td>4.517787</td><td>12.305235</td><td>1.002625</td><td>1542.396</td><td>1778.872</td></tr>
	<tr><td>school_prior_beta[43]</td><td>6.491070</td><td>6.000300</td><td>2.182913</td><td>1.873065</td><td>3.941435</td><td>10.762400</td><td>1.001407</td><td>1999.256</td><td>2222.189</td></tr>
	<tr><td>school_prior_beta[44]</td><td>6.169196</td><td>5.666335</td><td>2.053389</td><td>1.671631</td><td>3.866603</td><td>10.055040</td><td>1.000085</td><td>2892.004</td><td>2505.539</td></tr>
	<tr><td>school_prior_beta[45]</td><td>6.446915</td><td>5.880865</td><td>2.254919</td><td>1.863843</td><td>3.879132</td><td>10.766230</td><td>1.000337</td><td>2587.126</td><td>2728.151</td></tr>
	<tr><td>school_prior_beta[46]</td><td>6.232384</td><td>5.723025</td><td>2.047502</td><td>1.684271</td><td>3.902608</td><td>10.333235</td><td>1.001648</td><td>2626.035</td><td>3080.817</td></tr>
	<tr><td>school_prior_beta[47]</td><td>5.964638</td><td>5.512750</td><td>1.883736</td><td>1.532445</td><td>3.801014</td><td> 9.786658</td><td>1.000639</td><td>3195.178</td><td>2958.786</td></tr>
	<tr><td>school_prior_beta[48]</td><td>6.243338</td><td>5.748345</td><td>2.088923</td><td>1.725405</td><td>3.836314</td><td>10.384930</td><td>1.001729</td><td>1967.245</td><td>2267.657</td></tr>
	<tr><td>school_prior_beta[49]</td><td>6.452798</td><td>5.940115</td><td>2.247994</td><td>1.836385</td><td>3.953984</td><td>10.753980</td><td>1.001421</td><td>2044.521</td><td>2594.231</td></tr>
	<tr><td>school_prior_beta[50]</td><td>6.408177</td><td>5.942285</td><td>2.159334</td><td>1.873065</td><td>3.922172</td><td>10.577890</td><td>1.002382</td><td>1653.991</td><td>2504.470</td></tr>
	<tr><td>school_prior_beta[51]</td><td>6.361528</td><td>5.835470</td><td>2.142953</td><td>1.770892</td><td>3.926255</td><td>10.548125</td><td>1.003125</td><td>2515.924</td><td>2882.958</td></tr>
	<tr><td>school_prior_beta[52]</td><td>5.537106</td><td>5.180855</td><td>1.563088</td><td>1.253642</td><td>3.698441</td><td> 8.543566</td><td>1.000231</td><td>3139.606</td><td>2477.011</td></tr>
	<tr><td>school_prior_beta[53]</td><td>5.809495</td><td>5.407495</td><td>1.759563</td><td>1.462993</td><td>3.788838</td><td> 9.244379</td><td>1.000570</td><td>2770.758</td><td>2997.078</td></tr>
	<tr><td>school_prior_beta[54]</td><td>5.381683</td><td>5.021960</td><td>1.492077</td><td>1.180565</td><td>3.664767</td><td> 8.278310</td><td>1.000186</td><td>3755.497</td><td>2987.081</td></tr>
	<tr><td>school_prior_beta[55]</td><td>6.031982</td><td>5.552770</td><td>1.968935</td><td>1.581526</td><td>3.816465</td><td> 9.846426</td><td>1.001208</td><td>2709.514</td><td>2989.905</td></tr>
</tbody>
</table>

```r
authority_pooled_school_means_plot <- generate_school_plot(alberta_schools_authority_fit)
print(authority_pooled_school_means_plot)
```

![png](/2024-12-02-hierarchical-bayesian-models/output_79_0.png)

Again, it looks like this is working basically as expected!

## Final Comments

And there we have it! Solving the same problem with various levels of pooling.

One thing that you probably noticed is that all of the results for the last problem were essentially identical! That is absolutely the case, and is perhaps an illustrative example of why you should test out examples before applying these methods. But why did the level of pooling we did seem to have so little effect? Essentially, we had too much data! Pooling works by affecting the prior, and since all of our schools had a large number of students, their data overwhelmed the prior, regardless of whether that prior was unique to the school, pooled among all of the schools, or pooled by authority. As a result, we didn't see the same changes that we did in the earlier examples, where had had fewer data points. This is unsurprising in retrospect, but it also highlights that pooling has the greatest effect when you do not have an abundance of data.

You might also have noticed that the shape of the models changed as we added levels. That is because I had to reparameterize the models from centred to a non-centred for several parameters in order to avoid issues with the sampler (divergent transitions, &c.). I didn't go into details here because the focus was on other parts of the process, but I wrote all of the pooled models several times, non-centring a single parameter, then running it to see if it fixed the process, and repeating until everything worked. Apparently it's very common to have to do this with hierarchical models!

Hopefully this helps with understanding how to build hierarchical models! This is definitely something that I need to work through every time, starting from the unpooled version and then gradually adding in pooling. Despite the added level of complexity, the additional out-of-sampling accuracy and the additional confidence that that engenders in the model is worth it!

```r
sessionInfo()
```

    R version 4.4.1 (2024-06-14)
    Platform: aarch64-apple-darwin23.4.0
    Running under: macOS 15.0.1

    Matrix products: default
    BLAS:   /opt/homebrew/Cellar/openblas/0.3.28/lib/libopenblasp-r0.3.28.dylib
    LAPACK: /opt/homebrew/Cellar/r/4.4.1/lib/R/lib/libRlapack.dylib;  LAPACK version 3.12.0

    locale:
    [1] en_CA/en_CA/en_CA/C/en_CA/en_CA

    time zone: America/Edmonton
    tzcode source: internal

    attached base packages:
    [1] stats     graphics  grDevices utils     datasets  methods   base

    other attached packages:
    [1] readxl_1.4.3    posterior_1.6.0 cmdstanr_0.8.1  ggplot2_3.5.1
