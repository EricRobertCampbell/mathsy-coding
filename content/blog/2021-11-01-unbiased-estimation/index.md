---
title: Unbiased Estimators for Mean and Variance
date: 2021-11-01
description: Unbiased estimators for mean and variance, along with proofs
---

When we are presented with data, we often want to try to get some sort of grasp on how it is shaped. To this end, we would like to be able to estimate the mean and variance (or standard deviation). Let's dive in to these estimators, and look at proofs that they are unbiased!

## Estimators

When we are examining a population, we are often interested in parameters - that is, things that are true about the entire population. For instance, we might care about the average length of a population of snakes or the variance in the lifespan of a population of mice. At least from a frequentist perspectives, both of these are actual quantities which we could, with unlimited time and energy, determine. However, instead of the labourious process of finding population parameters, we use an _estimator_ to get close. An estimator is something which we can calculate as a proxy for the actual parameter of interest.

Of course, we would like our estimators to eventually get close to the actual parameter. Ideally, we would like an _unbiased estimator_. Like the name suggests, an estimator $\hat{\theta}$ of the parameter $\theta$ is unbiased if [ $E[\hat{\theta}] = \theta$ ](https://www.statlect.com/glossary/unbiased-estimator). Remember also that the expected value of a random variable $X$ is $E[X] = \sum_{i=1}^n x_i p_i$, where $x_i$ are the outcomes (values which $X$ could take on) and $p_i$ is the probability that the outcome $x_i$ occurs. Of course, if the distribution from which $X$ is drawn is continuous, then it would be an integral instead, but for the purpose of today's proofs we'll focus on discrete distributions.

## An Estimator for the Mean

Assume that you have drawn a sample $X_1$, $X_2$, $\dots$ $X_n$, all independent, from a distribution with mean $\mu$ and variance $\sigma^2$. Then an unbiased estimator of the mean is the sample mean $\overline{X} = \frac{1}{n} \sum_{i=1}^n X_i$.

Proof:

$$
\begin{align*}
E[\overline{X}] &= E\left[ \frac{ \sum_{i=1}^n X_i }{n} \right] \\
           &= \frac{1}{n} \sum_{i=1}^n E[X_i] \\
		   &= \frac{1}{n}\sum_{i=1}^n \mu \\
		   &= \frac{1}{n} \ast n\mu \\
		   &= \mu
\end{align*}
$$

And so we have it.

## An Estimator for the Variance

Finding an unbiased estimator for the variance is substantially more complicated than for the mean. First, a reminder: the variance of a random variable $X$ is $\text{Var}(X) = \frac{1}{n} \sum_{i=1}^n p_i (x_i - \mu)^2 = E[(x_i - \mu)^2]$, where again the $x_i$ are the possible values which $X$ can take on. Naively, we would imagine that with our same sample $X_1,\ X_2,\ \dots,\ X_n$ drawn from a distribution with mean $\mu$ and variance $\sigma^2$, an unbiased estimator would simply be $\frac{1}{n} \sum_{i=1}^n (X_i - \overline{X})^2$. However, it turns out that is not unbiased! The correct (or at least _a_ correct) unbiased estimator is called the sample variance, $s^2 = \frac{1}{n-1}\sum_{i=1}^n (X_i - \overline{X})^2$. The proof that this is unbiased relies on a few other facts - let's derive these!

$$
\begin{equation}
\text{Var}(X) = E[X^2] - E^2[X]
\tag{1}
\end{equation}
$$

Proof:

$$
\begin{align*}
	\text{Var}(X) &= E[(X - \mu)^2] \\
	              &= E[X^2 - 2X\mu + \mu^2] \\
				  &= E[X^2] - 2\mu E[X] + E[\mu^2] \\
				  &= E[X^2] - 2\mu^2 + \mu^2 \\
				  &= E[X^2] - \mu^2 \\
				  &= E[X^2] - E^2 [X] \\
	\end{align*}
$$

We will also need the following:

$$
\begin{equation}
E\left[\overline{X}^2\right] = \frac{1}{n}E[X^2] + \frac{n-1}{n} E^2[X] \tag{2}
\end{equation}
$$

Proof

$$
\begin{align*}
	E[\overline{X}^2] &= E\left[ \left( \frac{\sum_{i=1}^n X_i}{n} \right)^2 \right] \\
	             &= \frac{1}{n^2} E\left[ \left( \sum_{i=1}^n X_i \right)^2 \right] \\
				 &= \frac{1}{n^2} E\left[ \sum_{i=1}^n \sum_{j=1}^n X_i X_j \right] \\
				 &= \frac{1}{n^2} E\left[ \sum_{i = 1}^n X_i ^2 + \sum_{i \neq j} X_i X_j \right] \\
				 &= \frac{1}{n^2} \left[ \sum_{i=1}^n E[X_i ^2] + \sum_{i \neq j} E[X_i] E[X_j] \right] \\
				 &= \frac{1}{n^2} \left[ \sum_{i=1}^n E[X^2] + \sum_{i \neq j} E[X] E[X] \right] & \text{Because they are all identically distributed and independent}\\
				 &= \frac{1}{n^2} \left[ nE[X^2] + (n^2 - n)E^2[X] \right] \\
				 &= \frac{1}{n} E[X^2] + \frac{n-1}{n} E^2[X]
\end{align*}
$$

Now that we have those two fact all settled, we can prove that the sample variance is an unbiased estimator of the variance! That means that the expected value of the estimator $s^2$ should be the target parameter, $\sigma^2$.

So, assume that you have some distribution with mean $\mu$ and variance $\sigma^2$, and that we draw $n$ observations $X_1,\ X_2, \dots,\ X_n$, all independent, from this distribution, and from it we calculate the sample variance $s^2 = \frac{1}{n-1}\sum_{i=1}^n \left( X_i - \overline{X}\right)^2$. Then:

$$
\begin{align*}
E[s^2] &= E\left[ \frac{1}{n-1} \sum_{i=1}^n \left(X_i - \overline{X} \right)^2  \right] \\
	   &= \frac{1}{n-1} E\left[ \sum_{i=1}^n (X_i^2 -2\overline{X} X_i + \overline{X}^2) \right] \\
	   &= \frac{1}{n-1} E\left[ \sum_{i=1}^n X_i^2 -2\overline{X} \sum_{i=1}^n X_i + \sum_{i=1}^n \overline{X}^2) \right] \\
	   &= \frac{1}{n-1} E\left[ \sum_{i=1}^n X_i^2 -2\overline{X} * n\overline{X} + n \overline{X}^2 \right] \\
	   &= \frac{1}{n-1} E\left[ \sum_{i=1}^n X_i^2 - n\overline{X}^2 \right] \\
	   &= \frac{1}{n-1} \left( E\left[ \sum_{i=1}^n X_i^2 \right] - n E \left[\overline{X}^2 \right] \right) \\
	   &= \frac{1}{n-1} \left(  \sum_{i=1}^n E[X_i^2]  - n E \left[\overline{X}^2 \right] \right) \\
	   &= \frac{1}{n-1} \left( n E[X^2]  - n E \left[\overline{X}^2 \right] \right) && \text{Since the expectation is the same for all $X_i$}\\
	   &= \frac{1}{n-1} \left( n E[X^2]  - n\left( \frac{1}{n}E[X^2] + \frac{n-1}{n} E^2[X] \right) \right) && \text{By (2)}\\
	   &= \frac{1}{n-1} \left( n E[X^2]  - E[X^2] - ( n-1 ) E^2[X] \right)  \\
	   &= \frac{1}{n-1} \left( ( n - 1 ) E[X^2]  - ( n-1 ) E^2[X] \right)  \\
	   &= E[X^2]  - E^2[X] \\
	   &= \text{Var}(X) && \text{By (1)} \\
	   &= \sigma^2
\end{align*}
$$

And there we have it! The sample variance is an unbiased estimator for the variance.

## Implementations for the Sample Variance: JavaScript, Python, R

Now that we've looked at the mathematics behind this, let's look at how we can write a function for the sample variance in JavaScript, Python, and R:

### In JavaScript

`embed:./resources/inJavascript.js`

Output:
`embed:resources/inJavascript-output.txt`

### In Python

`embed:./resources/in_python.py`

Output:
`embed:resources/in_python-output.txt`

### In R

`embed:./resources/inR.R`

Output:
`embed:resources/inR-output.txt`

## Conclusions

Above, I've presented unbiased estimators for the mean $\mu$ and variance $\sigma^2$ of a distribution. With these, given independent samples from a distribution, we can provide point estimates for these parameters. However, there are some questions left to ask and things to note. For instance, we might assume that since the sample variance is an unbiased estimator of the variance, $s = \sqrt{\frac{\sum_{i=1}^n (X_i - \overline{X}) }{n-1}}$ would be an unbiased estimator of the standard deviation. [However, this is not the case.](https://en.wikipedia.org/wiki/Unbiased_estimation_of_standard_deviation)

A more pressing issue is how much we should believe the values that we get. That is, imagine that we take a sample of size 10 and get a sample mean of $m=4$ and sample variance $s^2 = 3$. Then we take a much larger sample of size 100 and get the exact same results! Obviously we expect that the larger sample will be more likely to be correct, but the question is - how much more should we believe the larger sample?

Perhaps these will be ideas for later. For now, have a great day!

## Sources

-   [This StackOverflow thread was particularly helpful.](https://economics.stackexchange.com/questions/4744/prove-the-sample-variance-is-an-unbiased-estimator) In particular, the proof that I've presented is largely a combination of the two most voted-for answers, expressed in a way that made sense to me.
-   [This site confirmed my foggy recollection of the definition of an unbiased estimator.](https://www.statlect.com/glossary/unbiased-estimator)
