const generateSorter = listOfSorters => (a, b) => {
	for (let sorter of listOfSorters) {
		const result = sorter(a, b)
		if (result !== 0) {
			return result
		}
	}
	return 0
}
