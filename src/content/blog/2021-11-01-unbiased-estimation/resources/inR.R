calculateSampleVariance <- function(numbers) {
	n <- length(numbers)
	xBar <- sum(numbers) / n
	sampleVariance <- sum( ( numbers - xBar ) ** 2 ) / (n - 1)
	return(sampleVariance)
}

sprintf("Sample variance of [1, 1, 1, 1, 1]: %.1f", calculateSampleVariance(c(1, 1, 1, 1, 1)))
sprintf("Sample variance of [1, 2, 3, 4, 5]: %.1f", calculateSampleVariance(c(1, 2, 3, 4, 5)))
