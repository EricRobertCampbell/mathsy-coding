---
title: Using Bayesian Regression to Quantify Sexual Dimorphism in Dinosaurs
description: The full text of a paper I presented a poster on at the Alberta Palaeontological Society's Paleo 24 conference, examining the use of Bayesian regression to quantify sexual dimorphism in dinosaurs.
pubDate: 2024-08-05
---

- [Introduction](#introduction)
- [Methods](#methods)
- [Results](#results)
- [Discussion](#discussion)

## Introduction

Sexual dimorphism is the difference in size, colour, or presence of a
feature between different sexes in a species. For instance, generally
human males are larger than females, male mallard ducks are colourfully
ornamented while females are drab, and male deer have antlers while
females do not. Sexual dimorphism is very common in extant species, but
detection of sexual dimorphism in extinct taxa, especially vertebrates,
has been more challenging. Essentially, there are two difficulties in
determining sexual dimorphism in extinct taxa: the 'sexual' part and the
'dimorphism' part. Determining the sex of the individual fossil, in the
absence of rare features (such as medullary bone or bacula) is extremely
challenging (Saitta et al. 2020). Similarly, determining
the mass or size of a feature from a fossil (such as those of dinosaurs)
can be difficult (Brusatte 2012 p. 126). When trying to determine the
level of sexual dimorphism, these problems compound each other.

There are several analytical methods which are commonly used. However,
each of these has their weaknesses. The use of $t$ tests (for
differences in the mean) or Hartigans' dip test (for unimodality)
(Hartigan and Hartigan, 1985) can suffer from low statistical power
(Mallon 2017) and in the case of $t$ tests a
further difficulty is the prolonged growth period of most dinosaurs
(Hone and Mallon 2017). As a result, positive results for
dimorphism in dinosaurs are rare.

However, a proposed method in (Saitta et al. 2020)
attempts to sidestep these difficulties by explicitly constructing
growth curves for the different sexes. Herein is proposed a modification
to that method in which Bayesian regression is used to recover a
distribution of possible growth curves for each sex and subsequently
applied to calculate the level of dimorphism.

## Methods

Bayesian regression is quite different from classical regression. To
estimate a parameter, there needs to be a _prior_ representing the
information that you have before seeing the data. You can then calculate
the _likelihood_ of the data that you observed for the different
parameter values. The optimal combination of the prior and the
likelihood is given by Bayes' Theorem and is termed the _posterior_. In
general, the result of a Bayesian analysis will be a probability
distribution, not a single number
(McElreath 2020). An illustration of this
method is shown in Figure 1.

![To estimate human height, we start with what we know before seeing any
data --- the *prior*. Then a sample of heights is collected and the
*likelihood* of that sample for each of the parameter values is
calculated. The combination of those, our final belief about the value
of the parameter, is the *posterior*
distribution.](/2024-08-05/images/bayesianExample.png)
Figure 1

To estimate human height, we start with what we know before seeing any
data - the _prior_. Then a sample of heights is collected and the
_likelihood_ of that sample for each of the parameter values is
calculated. The combination of those, our final belief about the value
of the parameter, is the _posterior_
distribution.

The modification to the method in (Saitta et al. 2020) is
presented below.

| Saitta et al. 2020                                                                                     | Modification                                                                      |
| ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| Gather data: age (or a correlate) and character of interest (e.g. length)                              |
| Fit growth curve to population as a whole                                                              |
| Predict sex by assigning all samples above the population curve to one sex and all below to the other. |
| Fit separate growth curves to each predicted sex                                                       | Create a posterior distribution for sex-specific parameters (Bayesian regression) |
| Calculate maximum likelihood level of dimorphism                                                       | Calculate posterior distribution for dimorphism                                   |

In both methods, the amount of dimorphism is calculated as the
difference in the asymptotes of the growth curves.

### Method Validation

Validating the method began with a simulated population of American
alligators (_Alligator mississippiensis_). The original von Bertalanffy
growth curves were determined in Wilkinson and Rhodes (1997) and
a simplified model using a constant standard deviation (rather than
sex-specific standard deviation of the form
$\alpha \log(\text{mean mass at age}) + \beta$) was used to generate
different samples. The final model was

$$
\begin{aligned}
\text{Length}_{ m / f } &\sim \mathcal{N}\left(\mu_{ m / f }, \sigma_{m/f}\right) \\
\mu_m &= 3.79 * \left(1 - 0.94e^{-0.0695 \ast \text{age}}\right) \\
\mu_f &= 2.78 * \left(1 - 0.91e^{-0.0926 \ast \text{age}}\right) \\
\sigma_{m/f} &= 0.25
\end{aligned}
$$

For the von Bertalanffy equation

$$\text{Length} = L(1 - Ae^{-K \ast \text{age}})$$

the parameter $L$ is the asymptotic length, and so the actual level of
sexual dimorphism is 3.79 m - 2.78 m = 1.01 m.

![Simulated Alligator Populations &
Method](/2024-08-05/images/alligatorMethod.png)
Figure 1: Simulated Alligator Populations & Method

A Bayesian model with wide priors centred around the population-level
curve values was used to recover the values (R Core Team 2023; Stan Development Team 2023).

$$
\begin{aligned}
\text{Length}_{m/f,i} &\sim \mathcal{N}\left(\mu_{m/f, i}, \sigma_{m / f}\right) \\
\mu_{m/f, i} &= \text{von Bertalanffy}(\text{age}_i, L_{ m/f }, A_{ m/f }, K_{ m/f }) \\
L_{ m/f } &\sim \mathcal{N}\left(\text{population L}, 0.5\right) \\
A_{ m/f } &\sim \mathcal{N}\left(\text{population A}, 0.025\right) \\
K_{ m/f } &\sim \mathcal{N}\left(\text{population K}, 0.05\right) \\
\sigma_{m/f} &\sim \mathcal{N}\left(0.25, 0.05\right) \\
\end{aligned}
$$

Since the priors used for the male and female parameters are identical
(and initially have means equal to the population-level parameters), the
results are slightly biased toward a finding of minimal or no sexual
dimorphism.

Both when using only single sex (female) or when including both, the
model was able to recover all of the population parameters with a high
degree of accuracy (in all cases within the 95% credible interval for
the posterior of each parameter).

The sample size also affects the ability of the method to recover the
true values. The model was run with several different sample sizes and
the posterior distribution for the level of dimorphism $L_m - L_f$ is
shown below.

![How different sample sizes affect the estimation of the level of
dimorphism](/2024-08-05/images/alligatorSampleSize.png)
Figure 2: How different sample sizes affect the estimation of the level of dimorphism

This method reliably generates mean levels which are close to the true
value and the 95% credible intervals overlap it as well. The general
pattern of approaching the value from below is due to the influence of
the prior (centred at zero); as the sample size becomes larger they drag
the posterior toward the correct value.

We can also ask about how the magnitude of dimorphism affects our
ability to detect it. For this, the female parameters were kept at their
original value and simulated male populations were created with an
effect size $E$ representing the scaled difference between the actual
male and female parameters. An effect size of $E = 0$ means that the
male and female populations are identical, $E = 1$ is the natural level
of dimorphism, and $E = 2$ is twice the natural level of dimorphism. The
model was then run and the error in the level of dimorphism was
calculated.

![Effect of sample size on estimated dimorphism
level](/2024-08-05/images/alligatorEffectSize.png)
Figure 3: Effect of sample size on estimated dimorphism level

There is a tendency to overestimate dimorphism when it is small, but
converges to the correct value once it reaches a large enough size. Note
that a significant contributor to the error in dimorphism estimation is
the inaccuracy of our naive sex predictor. By plotting the accuracy of
the dimorphism estimation against the computed accuracy in sex
prediction, we can see a clear relationship.

![Relationship between the error in dimorphism estimation and the accuracy of sex prediction](/2024-08-05/images/alligatorSexPredictionAccuracyDimorphismError.png)
Figure 4: Relationship between the error in dimorphism estimation and the accuracy of sex prediction

Overall, the results of the simulation show that this method is
reliable, with caveats that at low sample sizes or levels or dimorphism
we need to be especially skeptical of the results.

## Results

Once the method had been validated, the same method was used to
calculate the posterior distribution for sexual dimorphism for three
species of dinosaur: _Maiasaura peeblesorum_, _Psittacosaurus
lujiatunensis_, and _Tyrannosaurus rex_. The data used were compiled in
(Saitta et al. 2020) and were originally from
Woodward et al. 2015 (_Maiasaura peeblesorum_),
Erickson, Makovicky, Inouye, et al. 2015 (_Psittacosaurus lujiatunensis_),
and Erickson, Makovicky, Currie, et al. 2004,
Horner and Padian 2004, and Lee and Werning 2008
(_Tyrannosaurus rex_).

In each case, a logistic growth curve for mass against age with a
constant standard deviation was used.

$$\text{logistic}(\text{age}, L, q, k) = \frac{L}{1 + e^{q+k \ast \text{age}}}$$

Since $L$ is the asymptotic mass, the level of dimorphism is
$L_l - L_s$, where here $l$ represents the larger sex and $s$ represents
the smaller one. For each species, priors were chosen again centred
around the population level parameters and with a wide enough standard
deviation to cover all of the existing data.

For each species, the prior 95% quantiles for randomly generated
populations, along with the actual data, are displayed, along with a
selection of posterior growth curves.

<figure id="fig:maiasauraPriorPosterior">
<img src="/2024-08-05/images/maiasauraPrior.png" />
<img src="/2024-08-05/images/maiasauraPosterior.png" />
<figcaption><em>Maiasaura peeblesorum</em> Prior and Posterior
Estimates</figcaption>
</figure>

<figure id="fig:psittacosaurusPriorPosterior">
<img src="/2024-08-05/images/psittacosaurusPrior.png" />
<img src="/2024-08-05/images/psittacosaurusPosterior.png" />
<figcaption><em>Psittacosaurus lujiatunensis</em> Prior and Posterior
Estimates</figcaption>
</figure>

<figure id="fig:tyrannosaurPriorPosterior">
<img src="/2024-08-05/images/tyrannosaurPrior.png" />
<img src="/2024-08-05/images/tyrannosaurPosterior.png" />
<figcaption><em>Tyrannosaurus rex</em> Prior and Posterior
Estimates</figcaption>
</figure>
Figure 5: Prior and Posterior Estimates

The posterior curves are biologically plausible and in line with both
the data and our understanding of physiology; none of the values are
immediately out of the realm of possibility.

Of course, we can also compare the levels of dimorphism as the larger
sex's size as a percent of the smaller one (e.g. a dimorphism level of
50% would mean that the larger sex was 50% larger than the smaller).

![Dimorphism Levels](/2024-08-05/images/combinedDimorphism.png)
Figure 6: Dimorphism Levels

From this, we can see strong evidence for the _Maiasaura peeblesorum_
and _Psittacosaurus lujiatunensis_ dimorphism, while the _Tyrannosaurus
rex_ displays either no or a very small amount of dimorphism.

## Discussion

As shown above, the modification of the method in
(Saitta et al. 2020) using Bayesian regression to
calculate the posterior distributions for sex-specific growth curves and
the level of sexual dimorphism is a generally reliable and useful way to
quantify dimorphism in extinct populations. While it shares some
weakness with the original method, it also has several notable
advantages. One is that by carrying uncertainty through all parts of
modelling, the final result contains more information about the process
(McElreath 2020). Another is that by
incorporating prior knowledge, we can constrain our final result to be
biologically plausible.

Despite these advantages, there remain many areas in which this method
could be improved. The most critical, as noted in
(Saitta et al. 2020), is sex determination. As shown by
Figure 4, sex determination accuracy
was a strong predictor of the error in the level of dimorphism. There
are two complementary paths which should be taken towards alleviating
this issue. The first is the incorporation of the uncertainty in sex
determination into the posterior curves generated. At the moment we
behave as though the sex that we predict is correct, with no
uncertainty, when the reality is that this is a significant source of
error. This would result in widening the posterior distributions for the
levels of dimorphism, but would not address the underlying issue. For
that, we should look at alternate means of predicting sex, such as
cluster analysis involving traits other than the one that we are looking
at.

Determining levels of sexual dimorphism when both sex and size
determination are difficult is naturally a difficult problem, and the
method here, while offering an incremental improvement over existing
methods, is certainly no panacea. Further efforts, both on the
statistical and palaeontological side of the equation, will be required
in order to improve our understanding of sexual dimorphism within
extinct taxa.

For all data and code used here, along with additional analyses, see <https://github.com/EricRobertCampbell/aps-2024-poster-sexual-dimorphism>.

## References

- Brusatte, Stephen L (Apr. 2012). Dinosaur Paleobiology. en. TOPA Topics in Paleobiology. Hoboken, NJ: Wiley-Blackwell.
- Erickson, Gregory M., Peter J. Makovicky, Philip J. Currie, et al. (Aug. 2004). “Gigantism and comparative life-history parameters of tyrannosaurid dinosaurs”. In: Nature 430.7001. Number: 7001 Publisher: Nature Publishing Group, pp. 772–775. issn: 1476-4687. doi: 10.1038/nature 02699. url: https://www.nature.com/articles/nature02699 (visited on 07/02/2022).
- Erickson, Gregory M., Peter J. Makovicky, Brian D. Inouye, et al. (Oct. 2015). “Flawed Analysis? A Response to Myhrvold”. In: The Anatomical Record 298.10, pp. 1669–1672. issn: 1932-8486, 1932-8494. doi: 10.1002/ar.23187. url: https://anatomypubs.onlinelibrary.wiley.com/doi/10.1002/ar.23187 (visited on 11/01/2023).
- Hone, David W. E. and Jordan C. Mallon (2017). “Protracted growth impedes the detection of sexual dimorphism in non-avian dinosaurs”. In: Palaeontology 60.4, pp. 535–545. issn: 1475-4983. doi: 10.1111/pala.12298. url: https://onlinelibrary.wiley.com/doi/abs/10.1111/pala.122 98 (visited on 11/03/2022).
- Horner, John R. and Kevin Padian (Sept. 22, 2004). “Age and growth dynamics of Tyrannosaurus rex†”. In: Proceedings of the Royal Society of London. Series B: Biological Sciences 271.1551. Publisher: Royal Society, pp. 1875–1880. doi: 10.1098/rspb.2004.2829. url: https://royal societypublishing.org/doi/abs/10.1098/rspb.2004.2829 (visited on 02/03/2024).
- Lee, Andrew H. and Sarah Werning (Jan. 15, 2008). “Sexual maturity in growing dinosaurs does not fit reptilian growth models”. In: Proceedings of the National Academy of Sciences 105.2. Publisher: Proceedings of the National Academy of Sciences, pp. 582–587. doi: 10.1073/pnas.0708903105. url: https://www.pnas.org/doi/abs/10.1073/pnas.0708903105 (visited on 02/03/2024).
- Mallon, Jordan C. (Aug. 2017). “Recognizing sexual dimorphism in the fossil record: lessons from nonavian dinosaurs”. In: Paleobiology 43.3. Publisher: Cambridge University Press, pp. 495–507. issn: 0094-8373, 1938-5331. doi: 10.1017/pab.2016.51. url: https://www.cambridge.org/core/journals/paleobiology/article/abs/recognizing- sexual- dimorphism- in- the- fossil- record- lessons- from- nonavian- dinosaurs/76D9931163D564D386E86ACF686E586D (visited on 11/30/2022).
- McElreath, Richard (2020). Statistical rethinking: a Bayesian course with examples in R and Stan. Second edition. Texts in statistical science series. Boca Raton London New York: CRC Press, Taylor & Francis Group. 593 pp. isbn: 978-0-429-63914-2 978-0-367-13991-9.
- R Core Team (2023). R: A Language and Environment for Statistical Computing. R Foundation for Statistical Computing. Vienna, Austria. url: https://www.R-project.org/
- Saitta, Evan T et al. (Sept. 22, 2020). “An effect size statistical framework for investigating sexual dimorphism in non-avian dinosaurs and other extinct taxa”. In: Biological Journal of the Linnean Society 131.2, pp. 231–273. issn: 0024-4066. doi: 10.1093/biolinnean/blaa105. url: https://doi.org/10.1093/biolinnean/blaa105 (visited on 07/27/2023).
- Stan Development Team (2023). RStan: the R interface to Stan. R package version 2.32.3. url: https://mc-stan.org/.
- Wilkinson, Philip M. and Walter E. Rhodes (1997). “Growth Rates of American Alligators in Coastal South Carolina”. In: The Journal of Wildlife Management 61.2. Publisher: [Wiley, Wildlife So- ciety], pp. 397–402. issn: 0022-541X. doi: 10.2307/3802596. url: https://www.jstor.org/st able/3802596 (visited on 05/25/2023).
- Woodward, Holly N. et al. (Sept. 2015). “Maiasaura, a model organism for extinct vertebrate pop- ulation biology: a large sample statistical assessment of growth dynamics and survivorship”. In: Paleobiology 41.4. Publisher: Cambridge University Press, pp. 503–527. issn: 0094-8373, 1938- 5331. doi: 10.1017/pab.2015.19. url: https://www.cambridge.org/core/journals/paleob iology/article/maiasaura-a-model-organism-for-extinct-vertebrate-population-bi ology-a-large-sample-statistical-assessment-of-growth-dynamics-and-survivorshi p/288407BA0A91914480A0531529F050EF (visited on 02/03/2024).
