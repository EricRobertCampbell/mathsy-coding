function calculateSampleVariance(numbers) {
	const n = numbers.length;
	const xBar = numbers.reduce((sum, current) => sum + current, 0) / n;
	const sampleVariance =
		numbers.reduce((sum, current) => sum + (current - xBar) ** 2, 0) /
		(n - 1);
	return sampleVariance;
}

console.log(
	`Sample variance of [1, 1, 1, 1, 1]: ${calculateSampleVariance([
		1,
		1,
		1,
		1,
		1,
	])}`
);
console.log(
	`Sample variance of [1, 2, 3, 4, 5]: ${calculateSampleVariance([
		1,
		2,
		3,
		4,
		5,
	])}`
);
