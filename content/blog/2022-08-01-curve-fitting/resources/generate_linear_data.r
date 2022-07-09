# Generate random data fitting a linear equation y = 2x + 3 + N(0, 1)

xs <- seq(-3, 3, 0.5)
sigma <- 1
errors <- rnorm(length(xs), 0, sigma)
ys <- 2 * xs + 3 + errors
data <- data.frame(x=xs, y=ys)
write.csv(data, "linear_data.csv", row.names=F)

png(file="linear_data.png")
	plot(ys ~ xs)
	curve(2*x+3, add=T)
dev.off()
