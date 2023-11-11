const fs = require("fs");

// Read the data in
const condensedData = [];
try {
	const data = fs.readFileSync("./lga-coverage.csv", "utf-8");
	data.split("\n").forEach((row) => {
		const entries = row.split(",");
		const [
			local_code,
			age_group,
			population,
			numWithAtLeastOneDose,
			percentWithAtLeastOneDose,
			numberFullyImmunized,
			percentFullyImmunized,
			albertaPercentWithAtLeastOneDose,
			albertaPercentFullyImmunized,
			localName,
			zoneName,
		] = entries;
		if (age_group === '"ALL years"') {
			console.log(
				`Adding data: ${localName}: ${population} (${percentFullyImmunized}%)`
			);
			condensedData.push({
				localName: localName.replace(/"/g, ""),
				population: Number(population),
				percentFullyImmunized: Number(percentFullyImmunized),
			});
		}
	});
} catch (e) {
	console.error(e);
}

// and now write it
const filename = "./condensedData.json";
fs.writeFileSync(filename, JSON.stringify(condensedData));
console.log(`Finished writing data to ${filename}`);
