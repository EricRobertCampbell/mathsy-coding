const sortByLastName = (a, b) => a.lastName < b.lastName;
const sortByFirstName = (a, b) => a.firstName < b.firstName;

const classList = [
	{ firstName: "Stephanie", lastName: "Chen" },
	{ firstName: "Brandon", lastName: "Chen" },
	{ firstName: "Phillip", lastName: "Chen" },
	{ firstname: "Eve", lastName: "Bower" },
];
classList.sort((a, b) => {
	const resultOfLastNameSort = sortByLastName(a, b);
	if (resultOfLastNameSort !== 0) {
		return resultOfLastNameSort; // has given us a clear answer
	}
	// otherwise, sort these two by first name
	return sortByFirstName(a, b);
});
// -> [Eve, Brandon, Phillip, Stephanie]
