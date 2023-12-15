---
title: Exploring Population Differences Using Bayesian Analysis
description: This post explores Bayesian analysis techniques for comparing population differences using simulated height and weight data. We explore two different scenarios, one where we have access to the raw data and another where you only have access to the summary data (sample mean and standard deviation).
pubDate: 2024-03-04
---

## Finding a Mean - Raw Data and Summary Statistics (Python)

To start with, let's grab some data. We're going to use a very simple, clean dataset - some simulated heights and weights for males and females from Kaggle (https://www.kaggle.com/datasets/saranpannasuriyaporn/male-female-height-and-weight), based on data from Kumar & Ravikumar (2014). The weights are in kilograms and the heights are in centimetres. To start, let's load the data and take a look at the female weight data.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```

```python
data = pd.read_csv('./genderData/Training set.csv')
data.head()
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
    .dataframe tbody tr th {
        vertical-align: top;
    }
    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Height</th>
      <th>Weight</th>
      <th>Sex</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>165.65</td>
      <td>35.41</td>
      <td>Female</td>
    </tr>
    <tr>
      <th>1</th>
      <td>148.53</td>
      <td>74.45</td>
      <td>Female</td>
    </tr>
    <tr>
      <th>2</th>
      <td>167.04</td>
      <td>81.22</td>
      <td>Male</td>
    </tr>
    <tr>
      <th>3</th>
      <td>161.54</td>
      <td>71.47</td>
      <td>Male</td>
    </tr>
    <tr>
      <th>4</th>
      <td>174.31</td>
      <td>78.18</td>
      <td>Male</td>
    </tr>
  </tbody>
</table>
</div>

```python
# we want only the female data (and only the weights at that)
female_df = data.loc[data.Sex == 'Female']
female_df = female_df.drop("Height", axis=1)
female_df.head()
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
    .dataframe tbody tr th {
        vertical-align: top;
    }
    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Weight</th>
      <th>Sex</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>35.41</td>
      <td>Female</td>
    </tr>
    <tr>
      <th>1</th>
      <td>74.45</td>
      <td>Female</td>
    </tr>
    <tr>
      <th>5</th>
      <td>79.27</td>
      <td>Female</td>
    </tr>
    <tr>
      <th>6</th>
      <td>63.71</td>
      <td>Female</td>
    </tr>
    <tr>
      <th>7</th>
      <td>86.01</td>
      <td>Female</td>
    </tr>
  </tbody>
</table>
</div>

```python
female_df.describe()
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
    .dataframe tbody tr th {
        vertical-align: top;
    }
    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Weight</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>1500.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>62.310860</td>
    </tr>
    <tr>
      <th>std</th>
      <td>16.050301</td>
    </tr>
    <tr>
      <th>min</th>
      <td>24.570000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>53.737500</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>62.045000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>69.882500</td>
    </tr>
    <tr>
      <th>max</th>
      <td>485.000000</td>
    </tr>
  </tbody>
</table>
</div>

```python
# Dropping the infeasible values
female_df = female_df.drop(female_df[female_df.Weight == female_df.Weight.max()].index)
female_df.describe()
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
    .dataframe tbody tr th {
        vertical-align: top;
    }
    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Weight</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>1499.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>62.028879</td>
    </tr>
    <tr>
      <th>std</th>
      <td>11.765832</td>
    </tr>
    <tr>
      <th>min</th>
      <td>24.570000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>53.735000</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>62.020000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>69.850000</td>
    </tr>
    <tr>
      <th>max</th>
      <td>109.830000</td>
    </tr>
  </tbody>
</table>
</div>

```python
fig, ax = plt.subplots()
ax.hist(female_df.Weight, bins=50, alpha=0.7, linewidth=1, edgecolor='b')
ax.set_xlabel("Weight (kg)")
ax.set_ylabel("Count")
ax.set_title("Female Weight Histogram")
```

![A histogram of female weights](/2024-03-04/femaleWeightHistogram.png)

Now that we have our data, we can start asking the real question: given that we are pretending that the data represents a sample from some given population, what do we now believe about the mean weight of that population? To do this, we're going to model the distribution of the weight as a whole, and then examine the mean. Let's start by writing down our model:

$$
\begin{align*}
W &\sim \text{Normal}(\mu, \sigma) \\
\mu &\sim \text{Normal}(65, 20) \\
\sigma&\sim \text{HalfNormal}(10)
\end{align*}
$$

In words, I believe that the weights are normally distributed. I set the mean weight at 65kg with a standard deviation of 20kg, meaning that almost all of the means should fall between $65 \pm 2 * 20$kg, or somewhere between 25 and 105kg. This seems reasonable to me, if perhaps overly wide, but since we have plenty of data I am happy for the prior to be wide. I also set the prior for $\sigma$ to be half-normal with a variance of 10kg, just to keep everything nice and wide.

Now let's use [PyMC](https://www.pymc.io/welcome.html) to create the model and draw samples.

```python
import pymc as pm
import arviz as az

with pm.Model() as model:
    mu = pm.Normal('mu', 65, 20)
    sigma = pm.HalfNormal('sigma', 10)
    w = pm.Normal('w', mu, sigma, observed=female_df.Weight)
    inference_data = pm.sample()
```

    WARNING (pytensor.tensor.blas): Using NumPy C-API based implementation for BLAS functions.
    Auto-assigning NUTS sampler...
    Initializing NUTS using jitter+adapt_diag...
    Multiprocess sampling (4 chains in 4 jobs)
    NUTS: [mu, sigma]

<style>
    /* Turns off some styling */
    progress {
        /* gets rid of default border in Firefox and Opera. */
        border: none;
        /* Needs to be in here for Safari polyfill so background images work as expected. */
        background-size: auto;
    }
    progress:not([value]), progress:not([value])::-webkit-progress-bar {
        background: repeating-linear-gradient(45deg, #7e7e7e, #7e7e7e 10px, #5c5c5c 10px, #5c5c5c 20px);
    }
    .progress-bar-interrupted, .progress-bar-interrupted::-webkit-progress-bar {
        background: #F44336;
    }
</style>

<div>
  <progress value='8000' class='' max='8000' style='width:300px; height:20px; vertical-align: middle;'></progress>
  100.00% [8000/8000 00:01&lt;00:00 Sampling 4 chains, 0 divergences]
</div>

    Sampling 4 chains for 1_000 tune and 1_000 draw iterations (4_000 + 4_000 draws total) took 1 seconds.

```python
# Plotting the samples
az.plot_trace(inference_data, combined=True, figsize=(12, 8))
```

![First trace plot](/2024-03-04/posteriorTracePlot1.png)

```python
# Summary of the data
az.summary(inference_data)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
    .dataframe tbody tr th {
        vertical-align: top;
    }
    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>mean</th>
      <th>sd</th>
      <th>hdi_3%</th>
      <th>hdi_97%</th>
      <th>mcse_mean</th>
      <th>mcse_sd</th>
      <th>ess_bulk</th>
      <th>ess_tail</th>
      <th>r_hat</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>mu</th>
      <td>62.033</td>
      <td>0.306</td>
      <td>61.446</td>
      <td>62.590</td>
      <td>0.004</td>
      <td>0.003</td>
      <td>4725.0</td>
      <td>3230.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>sigma</th>
      <td>11.767</td>
      <td>0.215</td>
      <td>11.367</td>
      <td>12.175</td>
      <td>0.003</td>
      <td>0.002</td>
      <td>4276.0</td>
      <td>2849.0</td>
      <td>1.0</td>
    </tr>
  </tbody>
</table>
</div>

Looking at the data, I am pretty happy with the results. The standard deviation for $\mu$ was way too high in the priors, which we expected, but otherwise the results are largely in line with our reasoning. Also, the `r_hat` value is 1, which is an indication that there were no serious problems with the model / inference.

So, what do we now believe about the mean of the population? From the above, the HDI (highest density interval) falls between 61.5kg and 62.6kg, so we are very sure that the population mean is in that range.

Now we're going to try something a little different. Right now we have the raw data - that is, a large set of individual weights. However, sometimes we have the summary statistics (sample mean and sample standard deviation) instead. Especially with older papers, I've found that it is sometimes impossible to get the raw data and the summary data is that best you can do. If that's the case, can we still perform our inference? Absolutely! We just need to know the distributions of the summary statistics.

By the Central Limit Theorem, as long as our data is relatively well behaved then

$$
\bar{X} \sim \text{N}(\mu, \sigma / \sqrt{n})
$$

The variance is a little trickier, but we know that the quantity

$$
\frac{(n-1)S^2}{\sigma^2} \sim \chi^2(n-1)
$$

We can use both of these facts in constructing our model.

```python
x_bar = female_df.Weight.mean()
s = female_df.Weight.std()
n = len(female_df.Weight)

with pm.Model() as summary_statistics_model:
    mu = pm.Normal('mu', 65, 20)
    sigma = pm.HalfNormal('sigma', 10)
    x_bar = pm.Normal('x_bar', mu, sigma / np.sqrt(n), observed=x_bar)
    pm.Potential('sample_standard_deviation', pm.logp(pm.ChiSquared.dist(n-1), (n-1)*s**2 / sigma**2))
    summary_statistics_inference_data = pm.sample()
```

    Auto-assigning NUTS sampler...
    Initializing NUTS using jitter+adapt_diag...
    Multiprocess sampling (4 chains in 4 jobs)
    NUTS: [mu, sigma]

<style>
    /* Turns off some styling */
    progress {
        /* gets rid of default border in Firefox and Opera. */
        border: none;
        /* Needs to be in here for Safari polyfill so background images work as expected. */
        background-size: auto;
    }
    progress:not([value]), progress:not([value])::-webkit-progress-bar {
        background: repeating-linear-gradient(45deg, #7e7e7e, #7e7e7e 10px, #5c5c5c 10px, #5c5c5c 20px);
    }
    .progress-bar-interrupted, .progress-bar-interrupted::-webkit-progress-bar {
        background: #F44336;
    }
</style>

<div>
  <progress value='8000' class='' max='8000' style='width:300px; height:20px; vertical-align: middle;'></progress>
  100.00% [8000/8000 00:01&lt;00:00 Sampling 4 chains, 0 divergences]
</div>

    Sampling 4 chains for 1_000 tune and 1_000 draw iterations (4_000 + 4_000 draws total) took 1 seconds.

The tricky part of this model was accouning for the distribution of $\frac{(n-1)s^2}{\sigma^2}$. Because we're not setting the distribution for our observed variable, $s$, directly, but are instead modelling a function of that variable which is a mixture of observed and random variable, we weren't able to use a regular PyMC distribution and had to use the `pm.Potential` function instead. This function allows us to add an arbitrary likelihood term into the model. That single line was definitely the trickiest part of the model; for more information, see the [`Potential` docs](https://www.pymc.io/projects/docs/en/latest/api/model/generated/pymc.model.core.Potential.html) and [this thread on using random data as observed](https://discourse.pymc.io/t/using-a-random-variable-as-observed/7184/5).

```python
az.plot_trace(summary_statistics_inference_data, combined=True, figsize=(12, 8))
az.summary(summary_statistics_inference_data)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
    .dataframe tbody tr th {
        vertical-align: top;
    }
    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>mean</th>
      <th>sd</th>
      <th>hdi_3%</th>
      <th>hdi_97%</th>
      <th>mcse_mean</th>
      <th>mcse_sd</th>
      <th>ess_bulk</th>
      <th>ess_tail</th>
      <th>r_hat</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>mu</th>
      <td>62.032</td>
      <td>0.295</td>
      <td>61.466</td>
      <td>62.577</td>
      <td>0.005</td>
      <td>0.003</td>
      <td>3985.0</td>
      <td>2843.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>sigma</th>
      <td>11.777</td>
      <td>0.215</td>
      <td>11.378</td>
      <td>12.189</td>
      <td>0.003</td>
      <td>0.002</td>
      <td>4007.0</td>
      <td>2831.0</td>
      <td>1.0</td>
    </tr>
  </tbody>
</table>
</div>

![Second posterior distribution](/2024-03-04/posteriorTracePlot2.png)

From the graphs and the summary, we can see that the results from this method are very close to the method using the raw data. In fact, since this method requires only two likelihood calculations (one for the observed sample mean and one for the sample variance), it is well within the realm of possibility to eschew [MCMC](https://en.wikipedia.org/wiki/Markov_chain_Monte_Carlo) methods entirely and just use a grid-based approach to get the posterior directly. However, since we are going to be looking at a mix of data sets where sometimes that won't be the case, we'll stick with using MCMC methods for all of them.

## Difference of Means - Raw Data and Summary Statistics (Python)

Now that we've got a handle on constructing the models, let's move on to what we really wanted to do - estimating the difference between means of a population! In contrast with [my earlier approaches](/blog/2024-02-05-ci-means-small-n/) involving $t$ tests and the like, estimating the difference in means between two populations in a Bayesian model is simplicity itself - we just add a difference term into the model! Let's do exactly that by estimating the difference in the mean weight between males and females in the data. First we'll clean the data, then we'll build the model, first using the raw data and then using the summary statistics.

```python
male_df = data[data.Sex == 'Male']
male_df = male_df.drop("Height", axis=1)
male_df.describe()
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
    .dataframe tbody tr th {
        vertical-align: top;
    }
    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Weight</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>1500.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>74.490360</td>
    </tr>
    <tr>
      <th>std</th>
      <td>15.785732</td>
    </tr>
    <tr>
      <th>min</th>
      <td>8.530000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>63.767500</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>74.170000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>85.907500</td>
    </tr>
    <tr>
      <th>max</th>
      <td>121.980000</td>
    </tr>
  </tbody>
</table>
</div>

```python
# that minimum weight seems infeasible, so let's drop it
male_df = male_df.drop(male_df[male_df.Weight == male_df.Weight.min()].index)
male_df.describe()
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
    .dataframe tbody tr th {
        vertical-align: top;
    }
    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Weight</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>1499.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>74.534363</td>
    </tr>
    <tr>
      <th>std</th>
      <td>15.698705</td>
    </tr>
    <tr>
      <th>min</th>
      <td>22.400000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>63.780000</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>74.190000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>85.915000</td>
    </tr>
    <tr>
      <th>max</th>
      <td>121.980000</td>
    </tr>
  </tbody>
</table>
</div>

That minimum weight still seems very low to me, but looking at the histogram below makes it seems like maybe there just is a part of the population with very low (to me) weights. I'll accept it for now, but that seems like something worth digging more into.

```python
fig, ax = plt.subplots()
ax.hist(male_df.Weight, bins=50, alpha=0.7, linewidth=1, edgecolor='b')
ax.set_xlabel("Weight (kg)")
ax.set_ylabel("Count")
ax.set_title("Male Weight Histogram")
```

![Histogram of male weights](/2024-03-04/maleWeightHistogram.png)

Now let's build a model with the difference of means!

```python
with pm.Model() as means_difference_model:
    # model for females
    mu_f = pm.Normal('mu_f', 65, 20)
    sigma_f = pm.HalfNormal('sigma_f', 10)
    w_f = pm.Normal('w_f', mu_f, sigma_f, observed=female_df.Weight)

    # model for males
    mu_m = pm.Normal('mu_m', 65, 20)
    sigma_m = pm.HalfNormal('sigma_m', 10)
    w_m = pm.Normal('w_m', mu_m, sigma_m, observed=male_df.Weight)

    # NB this is Deterministic so that we get the result in the final samples
    difference = pm.Deterministic('difference', mu_m - mu_f)
    means_difference_inference_data = pm.sample()
```

    Auto-assigning NUTS sampler...
    Initializing NUTS using jitter+adapt_diag...
    Multiprocess sampling (4 chains in 4 jobs)
    NUTS: [mu_f, sigma_f, mu_m, sigma_m]

<style>
    /* Turns off some styling */
    progress {
        /* gets rid of default border in Firefox and Opera. */
        border: none;
        /* Needs to be in here for Safari polyfill so background images work as expected. */
        background-size: auto;
    }
    progress:not([value]), progress:not([value])::-webkit-progress-bar {
        background: repeating-linear-gradient(45deg, #7e7e7e, #7e7e7e 10px, #5c5c5c 10px, #5c5c5c 20px);
    }
    .progress-bar-interrupted, .progress-bar-interrupted::-webkit-progress-bar {
        background: #F44336;
    }
</style>

<div>
  <progress value='8000' class='' max='8000' style='width:300px; height:20px; vertical-align: middle;'></progress>
  100.00% [8000/8000 00:01&lt;00:00 Sampling 4 chains, 0 divergences]
</div>

    Sampling 4 chains for 1_000 tune and 1_000 draw iterations (4_000 + 4_000 draws total) took 2 seconds.

```python
az.plot_trace(means_difference_inference_data, var_names=['difference'], combined=True, figsize=(12, 8))
```

![Trace plot of the means difference](/2024-03-04/tracePlotMeansDifference1.png)

```python
az.summary(means_difference_inference_data, var_names=["difference"], hdi_prob=0.95)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
    .dataframe tbody tr th {
        vertical-align: top;
    }
    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>mean</th>
      <th>sd</th>
      <th>hdi_2.5%</th>
      <th>hdi_97.5%</th>
      <th>mcse_mean</th>
      <th>mcse_sd</th>
      <th>ess_bulk</th>
      <th>ess_tail</th>
      <th>r_hat</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>difference</th>
      <td>12.498</td>
      <td>0.5</td>
      <td>11.491</td>
      <td>13.435</td>
      <td>0.006</td>
      <td>0.004</td>
      <td>7569.0</td>
      <td>3504.0</td>
      <td>1.0</td>
    </tr>
  </tbody>
</table>
</div>

Here we see that the difference in means is roughly 11.5 - 13.4kg, with males being heavier. This is almost exactly what we expected, considering that the sample sizes are so large:

```python
male_df.Weight.mean() - female_df.Weight.mean()
```

    12.505483655770512

Of course, there is something slightly strange about this model, and that is the fact the we looked at the difference in means at all. Given that we have all of this data, why not just look directly at the differences in weights directly? In fact, we can do that with the data that we already have. In the inference data, the different draws for our `difference` data is stored, along with the chain that it was part of. We want to combined those chains and get the result as a `numpy` array. Luckily, ArviZ has utility functions to do exactly that. For more information, see the [ArviZ documentation on working with inference data](https://python.arviz.org/en/stable/getting_started/WorkingWithInferenceData.html)

```python
# combining the different chains and geting the result as a numpy array
combined = az.extract(means_difference_inference_data)
combined.difference.values
```

    array([11.6250048 , 11.81032579, 12.67818807, ..., 12.63357918,
           12.39090545, 12.80039761])

Of course, now that we have the samples for the difference, we would also like to get an idea of the distribution. We can use a Gaussian KDE for this and then graph the results.

```python
from scipy.stats import gaussian_kde

hdi = np.quantile(combined.difference, (0.025, 0.975))
posterior_difference = gaussian_kde(combined.difference.values)

difference_basis = np.linspace(10, 15, num=1000)
density = posterior_difference(difference_basis)
# ensure the values sum to one
density = density / density.sum()

difference_fills = ( difference_basis <= hdi[1] ) & (difference_basis > hdi[0])

fig, ax = plt.subplots()
ax.plot(difference_basis, density)
ax.fill_between(difference_basis[difference_fills], density[difference_fills], alpha=0.7)
ax.set_xlabel('Difference')
ax.set_ylabel('Density')
ax.set_title('Distribution of Difference (with 95% HDI)')
```

![Distribution of differences with the 95% HDI highlighted](/2024-03-04/posteriorMeanDifferences95HDI.png)

The result is very similar to what we saw earlier with the difference of means, which is intuitively what we expect.

Of course, if we were only interested in the difference between the weights, and not the difference of the means, we could have just explicitly constructed a model to reflect this.

$$
\begin{align*}
\text{weight difference} &\sim \text{Normal}(\mu_d, \sigma_d) \\
\mu_d &\sim \text{Normal}(12, 5) \\
\sigma_d &\sim \text{HalfNormal}(2.5) \\
\end{align*}
$$

```python
observed_differences = male_df.Weight.values - female_df.Weight.values
with pm.Model() as difference_model:
    mu_d = pm.Normal('mu_d', 12, 5)
    sigma_d = pm.HalfNormal('sigma_d', 2.5)
    w_d = pm.Normal('w_d', mu_d, sigma_d, observed=observed_differences)
    difference_sample = pm.sample()
```

    Auto-assigning NUTS sampler...
    Initializing NUTS using jitter+adapt_diag...
    Multiprocess sampling (4 chains in 4 jobs)
    NUTS: [mu_d, sigma_d]

<style>
    /* Turns off some styling */
    progress {
        /* gets rid of default border in Firefox and Opera. */
        border: none;
        /* Needs to be in here for Safari polyfill so background images work as expected. */
        background-size: auto;
    }
    progress:not([value]), progress:not([value])::-webkit-progress-bar {
        background: repeating-linear-gradient(45deg, #7e7e7e, #7e7e7e 10px, #5c5c5c 10px, #5c5c5c 20px);
    }
    .progress-bar-interrupted, .progress-bar-interrupted::-webkit-progress-bar {
        background: #F44336;
    }
</style>

<div>
  <progress value='8000' class='' max='8000' style='width:300px; height:20px; vertical-align: middle;'></progress>
  100.00% [8000/8000 00:01&lt;00:00 Sampling 4 chains, 0 divergences]
</div>

    Sampling 4 chains for 1_000 tune and 1_000 draw iterations (4_000 + 4_000 draws total) took 1 seconds.

```python
az.plot_trace(difference_sample, combined=True, figsize=(12, 8))
```

![Posterior trace plot of the differences](/2024-03-04/posteriorTracePlot3.png)

Again, by visual inspection you can see that the results of either using the model specifically formulated for the difference or the one formulated for the individual distributions and then getting the difference from that are virtually identical, and both are very close to the distrubution for the difference of the means. Which one you will choose will depend on what exactly you're trying to model!

Of course, we could also perform the same operation if we only knew the summary statistics (sample mean and sample standard deviation) for the differences. In fact, we have already done this in the second example. Since the differences are just a one-dimensional dataset, we can use the exact same method / model as when we were finding the distribution for a single population.

```python
differences = male_df.Weight.values - female_df.Weight.values
x_bar = differences.mean()
s = differences.std()
n = len(differences)

with pm.Model() as summary_statistics_model:
    mu = pm.Normal('mu', 12, 5)
    sigma = pm.HalfNormal('sigma', 2.5)
    x_bar = pm.Normal('x_bar', mu, sigma / np.sqrt(n), observed=x_bar)
    pm.Potential('sample_standard_deviation', pm.logp(pm.ChiSquared.dist(n-1), (n-1)*s**2 / sigma**2))
    summary_statistics_inference_data = pm.sample()

az.summary(summary_statistics_inference_data)
az.plot_trace(summary_statistics_inference_data, combined=True, figsize=(12, 8))
```

    Auto-assigning NUTS sampler...
    Initializing NUTS using jitter+adapt_diag...
    Multiprocess sampling (4 chains in 4 jobs)
    NUTS: [mu, sigma]

<style>
    /* Turns off some styling */
    progress {
        /* gets rid of default border in Firefox and Opera. */
        border: none;
        /* Needs to be in here for Safari polyfill so background images work as expected. */
        background-size: auto;
    }
    progress:not([value]), progress:not([value])::-webkit-progress-bar {
        background: repeating-linear-gradient(45deg, #7e7e7e, #7e7e7e 10px, #5c5c5c 10px, #5c5c5c 20px);
    }
    .progress-bar-interrupted, .progress-bar-interrupted::-webkit-progress-bar {
        background: #F44336;
    }
</style>

<div>
  <progress value='8000' class='' max='8000' style='width:300px; height:20px; vertical-align: middle;'></progress>
  100.00% [8000/8000 00:01&lt;00:00 Sampling 4 chains, 0 divergences]
</div>

    Sampling 4 chains for 1_000 tune and 1_000 draw iterations (4_000 + 4_000 draws total) took 1 seconds.

![Posterior trace plot of the differences](/2024-03-04/posteriorTracePlot4.png)

## Summary

Here we've taken a look at how you can look at the differences in some population measure, both through the difference of the means and through the distribution of the differences themselves. We also looked at this both in the case where you have access to the raw data (the individual measurements) and the case where you have access only to the summary statistics (sample mean and standard deviation). In either case, the models were fairly straightforward and all methods gave roughly equivalent results; the one that you choose will depend on the data available to you and the actual thing you are studying.

## Bibliography

- Male & Female height and weight. (n.d.). Retrieved 11 December 2023, from https://www.kaggle.com/datasets/saranpannasuriyaporn/male-female-height-and-weight
- Prasanna Kumar, S., & Ravikumar, A. (2014). Biometric Study of the Internal Dimensions of Subglottis and Upper Trachea in Adult Indian Population. Indian Journal of Otolaryngology and Head & Neck Surgery, 66(1), 261–266. https://doi.org/10.1007/s12070-012-0477-x
