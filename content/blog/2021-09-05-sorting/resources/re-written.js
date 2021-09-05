const sortByLastName = (a, b) => a.lastName < b.lastName;
const sortByFirstName = (a, b) => a.firstName < b.firstName;

const classList = [
	{ firstName: "Stephanie", lastName: "Chen" },
	{ firstName: "Brandon", lastName: "Chen" },
	{ firstName: "Phillip", lastName: "Chen" },
	{ firstname: "Eve", lastName: "Bower" },
];

const combinedSorter = generateSorter([sortByLastName, sortByFirstName]);
classList.sort(combinedSorter);
// -> [Eve, Brandon, Phillip, Stephanie]
