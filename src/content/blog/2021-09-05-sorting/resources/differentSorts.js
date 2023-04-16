const classList = [alice, bob, eve];

// for role call
classList.sort((a, b) => a.lastName < b.lastName); // -> [bob, eve, alice]
// for the teacher
classForTeacher = classList.sort((a, b) => a.firstName < b.firstName); // -> [alice, bob, eve]
// to determine valedictorian, &c.
classList.sort((a, b) => b.average - a.average); // -> [bob, eve, alice]
