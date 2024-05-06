---
title: Hypothesis Tests Involving Means
description: Looking at various hypothesis tests involving the mean or difference of means
pubDate: 2024-05-06
---

So far, I've looked at various ways that we can find the confidence interval for a difference of means, using both the frequentist ([here](/blog/2023-12-04-ci-means-large-sample-size) and [here](/blog/2024-02-05-ci-means-small-n)) and Bayesian ([here](/blog/2024-03-04-ci-means-bayesian) and [here](/blog/2024-04-01-mean-differences-r)) frameworks. In this post, I'll be looking at hypothesis tests which involve the mean.

## Quick Recap of Hypothesis Testing

Before we begin, let's remind ourselves of what the idea of hypothesis testing is. Essentially, we are going to start with our _null hypothesis_: our idea that we initially believe to be true, or the status quo. We are going to assume that this is true, and then look at the probability of the data that we collected, given the null hypothesis. If the data is very unlikely (again, given the null), we _reject_ the null hypothesis. If the data is roughly congruent with the null hypothesis (at whatever significance level we've decided on), then we _fail to reject_ the null hypothesis.

In this way, hypothesis testing is much like a trial where the null hypothesis would be innocence. If the evidence is overwhelmingly unlikely given that they are innocent, then we reject the hypothesis of innocence, finding them guilty. However, if the evidence is congruent with them being innocent, then we fail to reject their innocence, finding them not guilty instead.

Let's look at an example to help explain this.

## Testing $\mu = \mu_0$ (large samples)

Let's start by testing the null hypothesis that our population mean, $\mu$, is equal to some predetermined value, $\mu_0$. In this case, our null hypothesis (our starting point) is that the population mean $\mu = \mu_0$, and we will then look at the data to see if that is likely.

It seems reasonable to start with our sample mean, $\bar{x}$. We know that under some reasonable assumptions,

$$
\bar{X} \sim \text{Normal}\left(\mu, \frac{\sigma}{\sqrt{n}}\right)
$$

assuming that the underlying population has mean $\mu$ and standard deviation $\sigma$. In our case, since we start with the assumption that the null hypothesis is correct, we have

$$
\bar{X} \sim \text{Normal}\left(\mu_0, \frac{\sigma}{\sqrt{n}}\right)
$$

or more commonly,

$$
z = \frac{\bar{x} - \mu_0}{\sigma / \sqrt{n}} \sim \text{Normal}(0, 1)
$$

If the sample size is large, we can safely substitute the sample standard deviation, $s$, for the true population standard deviation, $\sigma$.

$$
z = \frac{\bar{x} - \mu_0}{s / \sqrt{n}} \sim \text{Normal}(0, 1)
$$

If we want to test our hypothesis at a significance level of $\alpha$ against the alternative hypothesis that $\mu \neq \mu_0$, then we know that the region $[-z_{\alpha / 2}, z_{\alpha / 2}]$ contains $1 - \alpha$ of the probability, and so if our null hypothesis is true, then with probability $1-\alpha$ our sample mean $\bar{x}$ will be in this region. Conversely, with probability $\alpha$ it will _not_ be in this region, and so we will reject the null hypothesis.

Again, this is exactly the process of creating a confidence interval and then determining whether our sample statistic is within the confidence interval.

```r
library(ggplot2)
options(repr.plot.width=15, repr.plot.height=8)

x <- seq(-3, 3, by=0.01)
y <- dnorm(x, mean=0, sd=1)
alpha <- 0.1
z_alpha2 <- qnorm(alpha/2, mean=0, sd=1, lower.tail=FALSE)
plot_df <- data.frame(x=x, y=y)

personal_theme <- theme(
    plot.title = element_text(hjust=0.5, size=18),
    panel.background = element_rect(fill = "white", colour = "white", linewidth=0),
    axis.title.x = element_text(size = 12),
    axis.title.y = element_text(size = 12),
    panel.grid.major = element_line(color = alpha("black", 0.2), linetype = "dashed")
)

ggplot(plot_df, aes(x, y)) +
    geom_line() +
    geom_area(data=plot_df[plot_df$x > z_alpha2,], aes(fill="Rejection Region"), alpha=0.2) +
    geom_area(data=plot_df[plot_df$x < -z_alpha2,], aes(fill="Rejection Region"), alpha=0.2) +
    annotate('label', x=0, y=0.2, label=expression(1-alpha), fill="white", label.size=NA) +
    annotate('text', x=-2, y=0.03, label=expression(frac(alpha, 2))) +
    annotate('text', x=2, y=0.03, label=expression(frac(alpha, 2))) +
    annotate('label', x=0, y=0.25, label="Acceptance Region\n(Confidence Interval)", fill="white", label.size=NA) +
    scale_x_continuous(
        breaks=c(-z_alpha2, 0, z_alpha2),
        labels=c(expression(-z[alpha/2]), 0, expression(z[alpha / 2]))) +
    scale_fill_manual(values="blue") +
    labs(x='x', y='Density', title="Hypothesis Testing for the Mean", fill="Fill") +
    personal_theme
```

![A plot of a normal distribution showing the acceptance and rejection regions](/2024-05-06/acceptanceRejection.png)

Let's look at an example to illustrate this point.

### Example

> A random sample of 100 deaths during the last year in the United States showed an average life span of 71.8 years with a standard deviation of 8.9 years. Does this indicate that the average life span today is greater than 70 years? Use a 0.05 significance level.

(Adapted from Walpole & Myers (1985), ex. 8.3, p. 275)

Our null hypothesis is $H_0$: $\mu = 70$, against the one-sided alternative hypothesis $H_1$: $\mu > 70$. This is slightly different from the case discussed earlier, since this is a one-sided test rather than a two-sided one, but the same process still applies.

```r
mu <- 70
x_bar <- 71.8
s <- 8.9
n <- 100

z <- (x_bar - mu) / (s / sqrt(n))
z
```

2.02247191011236

Our $z$ value is 2.02, and so now we want to see if that is in the $1 - \alpha$ confidence interval. Since this is a 1-sided test, we need $z_\alpha$ at the appropriate level.

```r
alpha <- 0.05
z_alpha <- qnorm(alpha, lower.tail=FALSE)
z_alpha
```

1.64485362695147

Since our test statistic $z > z_\alpha$, we are outside the confidence interval (acceptance regions) and so _reject_ the null hypothesis, concluding that the lifespan is greater than 70 years. We can also be more precise:

```r
p <- pnorm(z, lower.tail = FALSE)
p
```

0.0215638113390889

Since $p < \alpha$, we reject $H_0$. We can also interpret this graphically.

```r
x <- seq(-3, 3, by=0.01)
y <- dnorm(x, mean=0, sd=1)
plot_df <- data.frame(x=x, y=y)

ggplot(plot_df, aes(x, y)) +
    geom_line() +
    annotate('text', x=z+0.2, y=0.02, label=expression(P)) +
    geom_area(data=plot_df[plot_df$x > z,], fill='blue', alpha=0.2) +
    geom_vline(aes(xintercept=0), linetype='dotted') +
    scale_x_continuous(
        breaks=c(0, z_alpha, z),
        labels=c(0, expression(z[alpha]), expression(z))) +
    scale_fill_manual(values="blue") +
    labs(x='x', y='Density', title="Hypothesis Testing for the Mean") +
    personal_theme
```

![A plot of a normal distribution showing the $P$ value in comparison to the acceptance / rejection region](/2024-05-06/pValue.png)

## Testing $\mu = \mu_0$ (small samples)

This process was fine because we assumed that we had a large sample size, and specifically one that was large enough for us to credibly substitute $s$ for $\sigma$. If we have a small sample size, then the quantity

$$
t = \frac{\bar{x} - \mu_0}{s / \sqrt{n}} \sim t(n-1)
$$

that is, it has a Student-$t$ distribution with $n-1$ degrees of freedom. Otherwise, however, the process remains the same: set our significance level, calculate the $p$ value of our test statistic, and see whether it is less than our significance level.

### Example

> The _Edison Electric Institute_ publishes figures on the annual energy needs of difference appliances, claiming in particular that a certain vacuum cleaner brand expends 46 kilowatt-hours a year. A random sample of 12 homes found an average of 42 kWh with a standard deviation of 11.9 kWh. At a significance level of 0.05, can we conclude that the spend less than 46 kWh annually?

(Adapted from Walpole & Myers (1985) ex. 8.5, p. 278)

Our null hypothesis is $H_0$: $\mu = 46$ against the alternate hypothesis $H_1$: $\mu < 46$. Since the number of homes is small, we use the $t$ statistic.

```r
alpha <- 0.05
mu_0 <- 46
n = 12
x_bar <- 42
s <- 11.9

t_alpha <- qt(alpha, n-1, lower.tail=TRUE) # -1.7958...; negative because we are testing the left tail
t <- (x_bar - mu_0) / (s / sqrt(n)) # -1.16...
paste('t_alpha=', t_alpha, ' t=', t)
```

<span style=white-space:pre-wrap>'t_alpha= -1.79588481870404 t= -1.16440390424798'</span>

Since our test statistic $t=-1.16...$ is greater than our critical value ($t_\alpha = -1.7958...$), we _fail_ to reject the null hypothesis and can therefore _not_ conclude that the annual power usage is less than 46 kWh.

Using $p$ values,

```r
pt(t, df=n-1, lower.tail=TRUE)
```

0.134446412758992

Since this value is larger than the desired level of significance $\alpha=0.05$, we fail to reject the null hypothesis.

## Testing $\mu_1 - \mu_2 = d_0$, $\sigma_1$ and $\sigma_2$ Unknown but Equal

### Example

> Two different kinds of laminated material are being tested by putting them through a machine and then seeing how worn they become. Twelve pieces of material 1 were tested and found to have an average wear of 85 units with a standard deviation of 4, while for material 2 10 pieces were tested and found to have a mean wear of 81 units with a standard deviation of 5. At the 0.05 level, can we conclude that the wear of material 1 exceeds that of material 2 by more than 2 units? Assume the populations to be normal with equal variances.

(Adapted from Walpole & Myers (1985) ex. 8.6, p. 279)

We are testing the null hypothesis $H_0$: $\mu_1 = \mu_2$ against the alternate hypothesis $H_1$: $\mu_1 - \mu_2 > 2$. Since we assume that the populations have the same variance, we find an expression for the pooled variance from that of the different samples and use that in our calculation, and so our sample statistic is

$$
t = \frac{(\bar{x_1} - \bar{x_2}) - d}{s_p \sqrt{1 / n_1 + 1 / n_2}} \sim t(n_1 + n_2 - 2)
$$

where

$$
s_p = \sqrt{\frac{(n_1 - 1)s_1^2 + (n_2 - 1)s_2^2}{n_1 + n_2 - 2}}
$$

Since we are testing at the $\alpha = 0.05$ level, we want our test statistic $t$ to be greater than $t_\alpha = 1.7$.

```r
alpha <- 0.05

n_1 <- 12
x_bar_1 <- 85
s_1 <- 4

n_2 <- 10
x_bar_2 <- 81
s_2 <- 5

d <- 2 # difference we are testing against

df <- n_1 + n_2 - 2 # 20

t_alpha <- qt(alpha, df=df, lower.tail = FALSE) # 1.7247...
s_p <- sqrt(((n_1 - 1)*s_1^2 + (n_2 - 1)*s_2^2) / df) # 4.47...
t <- (( x_bar_1 - x_bar_2 ) - d) / (s_p * sqrt(1 / n_1 + 1 / n_2)) # 1.04
```

Since our $t$ statistic did not exceed $t_\alpha$ at our desired significance level, we fail to reject the null hypothesis and cannot then conclude that the difference is greater than 2.

Using $p$ values,

```r
pt(t, df=df, lower.tail=FALSE)
```

0.154659409955889

By the same logic, since this is greater than 0.05 (the desired significance level), we fail to reject the null.

## Testing $\mu_d = d_0$ with Paired Observations

### Example

> In "Influence of physical restraint and restraint-facilitating drugs on blood measurements of white-tailed deer and other selected mammals", the author examined the effect of succinyl-choline on deer. They were captured (using a dart gun) and the levels of androgen in their blood were checked, and then checked again after 30 minutes, after which point the deer were released. At the 0.05 level of significance, can we conclude that the androgen levels were altered by the drug injection?

| Deer | Time of Injection | 30 minutes after |
| ---- | ----------------- | ---------------- |
| 1    | 2.76              | 7.02             |
| 2    | 5.18              | 3.10             |
| 3    | 2.68              | 5.44             |
| 4    | 3.05              | 3.99             |
| 5    | 4.10              | 5.21             |
| 6    | 7.05              | 10.26            |
| 7    | 6.60              | 13.91            |
| 8    | 4.79              | 18.53            |
| 9    | 7.39              | 7.91             |
| 10   | 7.30              | 4.85             |
| 11   | 11.78             | 11.10            |
| 12   | 3.90              | 3.74             |
| 13   | 26.00             | 94.03            |
| 14   | 67.48             | 94.03            |
| 15   | 17.04             | 41.70            |

(Modified from Walpole & Myers (1985), ex. 8.7, p. 280)

Here we want to test not the individual values, but instead their differences. We can use the $t$ statistics, since

$$
t= \frac{\bar{d} - d_0}{s_d / \sqrt{n}} \sim t(n - 1)
$$

We are testing the null hypothesis $H_0$: $\mu_d = \mu_1 - \mu_2 = 0$ against the alternate hypothesis $\mu_d \neq 0$. Since this is a two-tailed test (we are testing if the subsequent to the injection the levels rose _or_ fell), we will reject the null if $t < -t_{\alpha / 2}$ or $t > t_{\alpha / 2}$. Since we are testing at the 0.05 significance level, $t_{\alpha / 2} = 2.14$.

```r
deer_df <- data.frame(
    before=c(
        2.76,
        5.18,
        2.68,
        3.05,
        4.10,
        7.05,
        6.60,
        4.79,
        7.39,
        7.30,
        11.78,
        3.90,
        26.00,
        67.48,
        17.04
    ),
    after=c(
        7.02,
        3.10,
        5.44,
        3.99,
        5.21,
        10.26,
        13.91,
        18.53,
        7.91,
        4.85,
        11.10,
        3.74,
        94.03,
        94.03,
        41.70
    )
)

deer_df$d <- deer_df$after - deer_df$before
deer_df
```

<table class="dataframe">
<caption>A data.frame: 15 × 3</caption>
<thead>
	<tr><th scope=col>before</th><th scope=col>after</th><th scope=col>d</th></tr>
	<tr><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td> 2.76</td><td> 7.02</td><td> 4.26</td></tr>
	<tr><td> 5.18</td><td> 3.10</td><td>-2.08</td></tr>
	<tr><td> 2.68</td><td> 5.44</td><td> 2.76</td></tr>
	<tr><td> 3.05</td><td> 3.99</td><td> 0.94</td></tr>
	<tr><td> 4.10</td><td> 5.21</td><td> 1.11</td></tr>
	<tr><td> 7.05</td><td>10.26</td><td> 3.21</td></tr>
	<tr><td> 6.60</td><td>13.91</td><td> 7.31</td></tr>
	<tr><td> 4.79</td><td>18.53</td><td>13.74</td></tr>
	<tr><td> 7.39</td><td> 7.91</td><td> 0.52</td></tr>
	<tr><td> 7.30</td><td> 4.85</td><td>-2.45</td></tr>
	<tr><td>11.78</td><td>11.10</td><td>-0.68</td></tr>
	<tr><td> 3.90</td><td> 3.74</td><td>-0.16</td></tr>
	<tr><td>26.00</td><td>94.03</td><td>68.03</td></tr>
	<tr><td>67.48</td><td>94.03</td><td>26.55</td></tr>
	<tr><td>17.04</td><td>41.70</td><td>24.66</td></tr>
</tbody>
</table>

```r
alpha <- 0.05

n <- nrow(deer_df) # 15
df <- n - 1 # 14
d_bar <- mean(deer_df$d) # 9.848
s_d <- sd(deer_df$d) # 18.47

t_alpha_2 <- qt(alpha / 2, df=df, lower.tail = FALSE) # 2.14478... critical value

d <- 0 # null hypothesis difference

t <- (d_bar - d) / (s_d / sqrt(n)) # 2.06
```

Since our test statistics $t=2.06$ was not in the rejection region ($>2.14$ or $<-2.14$), we fail to reject the null hypothesis and cannot therefore conclude at the 0.05 significance level that there was a difference in androgen levels before and after the injection.

Alternatively, we could check against the $p$ level:

```r
pt(t, df, lower.tail = FALSE)
```

0.0289991646967756

Since this is greater than $\alpha / 2$, we again fail to reject the null.

## Conclusion

Although this post was largely going through a series of examples of hypothesis tests which somehow involved either the mean or the difference of means, hopefully the commonalities are starting to become clear. In all cases, we start with our null hypothesis and alternate hypothesis, and then create a confidence interval for the desired quantity (mean or difference of means) at the desired confidence level. We then test to see if our test statistic is within the confidence interval (in which case we _fail_ to reject the null) or outside of it (in which case we reject the null).

Alternatively, this process is exactly equivalent to calculating a $P$ value - that is, the probability that we would see data _at least as extreme_ as what we actually witnessed if the null hypothesis were true - and rejecting the null if the data is more extreme than our level of significance or failing to reject it if not.

## Bibliography

-   Walpole, R. E., & Myers, R. H. (1985). Probability and Statistics for Engineers and Scientists. Macmillan USA.
-   Wesson, J. A. (1976). Influence of physical restraint and restraint-facilitating drugs on blood measurements of white-tailed deer and other selected mammals [Virginia Tech]. https://vtechworks.lib.vt.edu/items/bb63de27-3f60-4d17-bff8-2a5a38e1b2b0
