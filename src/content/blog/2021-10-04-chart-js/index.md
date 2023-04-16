---
title: Basics of Chart.js - Covid Vaccination Rates
pubDate: 2021-10-04
description: Learning the basics of Chart.js by analyzing COVID-19 vaccination rates by region in Alberta
updates:
	- {date: 2023-04-16, message: Changing image and file paths}
---

Being able to visually examine data, or present data in an aesthetic manner, is incredibly important! In addition to many people perferring to learn things visually, making your data visible can allow you to spot patterns and test hypotheses more quickly. Although there are many different solutions for creating beautiful charts on the web, today I'm going to use [Chart.js](https://www.chartjs.org/) to examine the COVID-19 vaccination data for different regions in the province of Alberta. The finished project can be found at [this GitHub repository](https://github.com/EricRobertCampbell/learning-chart-js).

## Before We Get Started

The basic idea of this project is to use some very simple data visualization to examine the COVID-19 vaccination rates for different regions in the province of Alberta. We're going to look at the major features of the Chart.js library by examining the data in a few ways:

1. A simple bar graph of the vaccination rate by region
2. A simple scatter plot of the regions by population and vaccination rate
3. An examination of whether the differences that we see can be explained by differing populations using a variation on a [funnel plot](https://en.wikipedia.org/wiki/Funnel_plot) with different confidence intervals.

I'm also going to do this the 'old-fashioned' way - pure HTML, CSS, and JavaScript (and precious little CSS at that). In some cases that is going to lead to some slightly strange choices - I hope that the simplicity and reduced opportunity for errors makes up for that. I will discuss some of these choices and what should (or could) be done at the end.

### Creating the Project

Let's start by setting up the basic structure of the project - creating the index.html file as well as the files and folders for the JavaScript and CSS.

```bash
mkdir learning-chart-js
cd learning-chart-js
touch index.html
mkdir scripts styling
touch scripts/script.js
touch styling/styles.css
```

Once that's done, running `ls -R` (list everything, recursing into directories) should give you the following:

```
.:
index.html
scripts
styling

./scripts:
script.js

./styling:
style.css
```

The next reasonable step would be to create the HTML:

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8" />
		<script type="text/javascript" src="./scripts/script.js"></script>
		<link href="./styling/style.css" rel="stylesheet" />
	</head>
	<body>
		<h1>An Introduction to Chart.js</h1>
		<p>here is some content</p>
	</body>
</html>
```

We'll worry about the JavaScript and CSS later - for now we just want to ensure that the basics work. Opening up the page in your browser should display the following:

![A contender for website of the year?](/src/content/blog/2021-10-04-chart-js/resources/website1.jpg)

### Getting, Massaging, and Incorporting the Data

Now that we have the basics of the site, we should actually get the data that we would like to analyze. The government of Alberta publishes [CSV files with detailed pandemic information](https://www.alberta.ca/stats/covid-19-alberta-statistics.htm#data-export) on a (usually) daily basis. For our purposes, we want the [vaccine data](https://www.alberta.ca/data/stats/lga-coverage.csv), so go ahead and grab that. I downloaded the file containing data up to September 2; if you would like to follow along exactly you can grab [the exact file as a gist](https://gist.github.com/EricRobertCampbell/08b5ed4f73b00a10165193aaeb2bdfcf). I've put the file into a newly created `data` directory. The first few lines of the file should look as follows:

```csv
"Local Code","Age Group","Population","# of population with at least 1 dose","Percent of population who received at least one dose","# of population fully immunized","Percent of population fully immunized","Alberta: percent of population who received at least one dose","Alberta: percent of population fully immunized","Local Name","Zone Name"
"Z1.1.A.01","12-19 years",486,253,52,217,44.6,69.2,59.8,"CROWSNEST PASS","SOUTH"
"Z1.1.A.01","12+ years",5615,3948,70.3,3647,65,78.3,70.2,"CROWSNEST PASS","SOUTH"
"Z1.1.A.01","20-39 years",1304,694,53.2,585,44.9,68,58.3,"CROWSNEST PASS","SOUTH"
"Z1.1.A.01","40-59 years",1622,1108,68.3,1028,63.4,78.5,72.1,"CROWSNEST PASS","SOUTH"
"Z1.1.A.01","60-74 years",1599,1354,84.7,1297,81.1,89.8,86.4,"CROWSNEST PASS","SOUTH"
"Z1.1.A.01","75+ years",604,523,86.6,510,84.5,91.3,89.7,"CROWSNEST PASS","SOUTH"
"Z1.1.A.01","ALL years",6280,3948,62.9,3647,58.1,66.6,59.7,"CROWSNEST PASS","SOUTH"
"Z1.1.A.02","12-19 years",779,475,61,374,48,69.2,59.8,"PINCHER CREEK","SOUTH"
"Z1.1.A.02","12+ years",7177,5341,74.4,4812,67.1,78.3,70.2,"PINCHER CREEK","SOUTH"
```

While this is great, there are a few things that we would like to fix:

1. For our purposes, we really don't care about all the data - we just want the data for the entire population (not segregated by age) of each region, along with the population of that region and the vaccination rate. Even more than that, we only care about the _full_ vaccination rate - that is, the rate for people with both doses.
2. This is not directly accessible in JavaScript.

To fix both of these issues, we're going to create a quick [node.js](https://nodejs.org/en/) script to process the file and output a [JSON](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON) with the relevant data.

```bash
cd data
touch processData.js
```

The newly created `processData.js` file should look as follows:

```js
const fs = require("fs");

// Read the data in
const condensedData = [];
try {
	const data = fs.readFileSync("./lga-coverage.csv", "utf-8");
	data.split("\n").forEach(row => {
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
```

To run it:

```bash
node processData.js
```

If everything went as planned, there should now be a file `condensedData.json` containing the data that we generally care about.

However, there is no really good way (that I am aware of) to make this data natively available to our JavaScript, so we are now going to do something slightly horrific and _manually copy the contents of the JSON file into `scripts/script.js`_. While we're at it, we're going to ensure that it is actually loaded by displaying its contents in a `<pre>` tag that we'll need to create in `index.html`.

```diff
 <!-- index.html -->
 <!doctype html>
 <html>
 	<head>
 		<meta charset="utf-8">
 		<script type="text/javascript" src="./scripts/script.js"></script>
 		<link href="./styling/style.css" rel="stylesheet" />
 	</head>
 	<body>
 		<h1>An Introduction to Chart.js</h1>
-		<p>here is some content</p>
+		<pre id="data-display"></pre>
 	</body>
 </html>
```

```js
// script.js
const condensedData = [
	{
		localName: "CROWSNEST PASS",
		population: 6280,
		percentFullyImmunized: 58.1,
	},
	{
		localName: "PINCHER CREEK",
		population: 8344,
		percentFullyImmunized: 57.7,
	},
	{
		localName: "FORT MACLEOD",
		population: 6753,
		percentFullyImmunized: 44.3,
	},
	{
		localName: "CARDSTON-KAINAI",
		population: 16595,
		percentFullyImmunized: 48.6,
	},
	{
		localName: "COUNTY OF LETHBRIDGE",
		population: 25820,
		percentFullyImmunized: 44,
	},
	{ localName: "TABER MD", population: 19028, percentFullyImmunized: 34.9 },
	{
		localName: "COUNTY OF WARNER",
		population: 11104,
		percentFullyImmunized: 42.9,
	},
	{
		localName: "COUNTY OF FORTY MILE",
		population: 6409,
		percentFullyImmunized: 28.3,
	},
	{ localName: "NEWELL", population: 27753, percentFullyImmunized: 46.9 },
	{ localName: "OYEN", population: 3486, percentFullyImmunized: 45.9 },
	{
		localName: "CYPRESS COUNTY",
		population: 11298,
		percentFullyImmunized: 48.6,
	},
	{
		localName: "MEDICINE HAT",
		population: 68115,
		percentFullyImmunized: 57.4,
	},
	{
		localName: "LETHBRIDGE - WEST",
		population: 38163,
		percentFullyImmunized: 65.7,
	},
	{
		localName: "LETHBRIDGE - NORTH",
		population: 27903,
		percentFullyImmunized: 61.8,
	},
	{
		localName: "LETHBRIDGE - SOUTH",
		population: 34464,
		percentFullyImmunized: 65.3,
	},
	{
		localName: "CALGARY - UPPER NW",
		population: 123679,
		percentFullyImmunized: 69.4,
	},
	{
		localName: "CALGARY - NORTH",
		population: 116945,
		percentFullyImmunized: 67.6,
	},
	{
		localName: "CALGARY - NOSE HILL",
		population: 78021,
		percentFullyImmunized: 65.8,
	},
	{
		localName: "CALGARY - LOWER NW",
		population: 62696,
		percentFullyImmunized: 71.2,
	},
	{
		localName: "CALGARY - WEST BOW",
		population: 21283,
		percentFullyImmunized: 65.7,
	},
	{
		localName: "CALGARY - CENTRE NORTH",
		population: 44910,
		percentFullyImmunized: 68.7,
	},
	{
		localName: "CALGARY - UPPER NE",
		population: 120999,
		percentFullyImmunized: 63.9,
	},
	{
		localName: "CALGARY - LOWER NE",
		population: 96472,
		percentFullyImmunized: 58.3,
	},
	{
		localName: "CALGARY - EAST",
		population: 72509,
		percentFullyImmunized: 56.7,
	},
	{
		localName: "CALGARY - SE",
		population: 134420,
		percentFullyImmunized: 64,
	},
	{
		localName: "CALGARY - WEST",
		population: 92320,
		percentFullyImmunized: 69.3,
	},
	{
		localName: "CALGARY - CENTRE",
		population: 67568,
		percentFullyImmunized: 66.5,
	},
	{
		localName: "CALGARY - CENTRE WEST",
		population: 65845,
		percentFullyImmunized: 67.7,
	},
	{
		localName: "CALGARY - ELBOW",
		population: 40834,
		percentFullyImmunized: 69.8,
	},
	{
		localName: "CALGARY - FISH CREEK",
		population: 111574,
		percentFullyImmunized: 66.5,
	},
	{
		localName: "CALGARY - SW",
		population: 116934,
		percentFullyImmunized: 66.5,
	},
	{
		localName: "OKOTOKS-PRIDDIS",
		population: 46042,
		percentFullyImmunized: 60,
	},
	{
		localName: "BLACK DIAMOND",
		population: 8769,
		percentFullyImmunized: 52.9,
	},
	{ localName: "HIGH RIVER", population: 23739, percentFullyImmunized: 56.1 },
	{ localName: "CLARESHOLM", population: 6246, percentFullyImmunized: 56.9 },
	{ localName: "VULCAN", population: 6775, percentFullyImmunized: 47 },
	{ localName: "AIRDRIE", population: 73698, percentFullyImmunized: 56.8 },
	{ localName: "CHESTERMERE", population: 25015, percentFullyImmunized: 63 },
	{ localName: "STRATHMORE", population: 35685, percentFullyImmunized: 54.8 },
	{ localName: "CROSSFIELD", population: 9164, percentFullyImmunized: 50.4 },
	{ localName: "DIDSBURY", population: 16475, percentFullyImmunized: 50.3 },
	{
		localName: "COCHRANE-SPRINGBANK",
		population: 50816,
		percentFullyImmunized: 63.2,
	},
	{ localName: "CANMORE", population: 27674, percentFullyImmunized: 64.3 },
	{ localName: "BANFF", population: 13451, percentFullyImmunized: 57.7 },
	{
		localName: "ROCKY MOUNTAIN HOUSE",
		population: 20389,
		percentFullyImmunized: 43.3,
	},
	{
		localName: "DRAYTON VALLEY",
		population: 18075,
		percentFullyImmunized: 40.6,
	},
	{ localName: "SUNDRE", population: 6782, percentFullyImmunized: 47.6 },
	{ localName: "OLDS", population: 12597, percentFullyImmunized: 54.9 },
	{ localName: "INNISFAIL", population: 15939, percentFullyImmunized: 57.1 },
	{
		localName: "RED DEER COUNTY",
		population: 29495,
		percentFullyImmunized: 43.6,
	},
	{
		localName: "SYLVAN LAKE",
		population: 18013,
		percentFullyImmunized: 42.9,
	},
	{
		localName: "THREE HILLS/HIGHWAY 21",
		population: 10816,
		percentFullyImmunized: 45.5,
	},
	{
		localName: "STARLAND COUNTY/DRUMHELLER",
		population: 11802,
		percentFullyImmunized: 55.8,
	},
	{
		localName: "PLANNING & SPECIAL AREA 2",
		population: 3648,
		percentFullyImmunized: 48,
	},
	{
		localName: "STETTLER & COUNTY",
		population: 12520,
		percentFullyImmunized: 45.8,
	},
	{
		localName: "CASTOR/CORONATION/CONSORT",
		population: 6160,
		percentFullyImmunized: 44.3,
	},
	{
		localName: "WETASKIWIN COUNTY",
		population: 33715,
		percentFullyImmunized: 46.8,
	},
	{ localName: "PONOKA", population: 12399, percentFullyImmunized: 47.5 },
	{ localName: "RIMBEY", population: 10013, percentFullyImmunized: 44.3 },
	{ localName: "LACOMBE", population: 23417, percentFullyImmunized: 48.1 },
	{
		localName: "CAMROSE & COUNTY",
		population: 30125,
		percentFullyImmunized: 57.8,
	},
	{ localName: "TOFIELD", population: 7797, percentFullyImmunized: 51.5 },
	{ localName: "VIKING", population: 2351, percentFullyImmunized: 55.5 },
	{
		localName: "FLAGSTAFF COUNTY",
		population: 8426,
		percentFullyImmunized: 55.7,
	},
	{
		localName: "MD OF PROVOST",
		population: 4860,
		percentFullyImmunized: 50.1,
	},
	{
		localName: "MD OF WAINWRIGHT",
		population: 11915,
		percentFullyImmunized: 54,
	},
	{
		localName: "LAMONT COUNTY",
		population: 6388,
		percentFullyImmunized: 52.6,
	},
	{
		localName: "TWO HILLS COUNTY",
		population: 5579,
		percentFullyImmunized: 30.5,
	},
	{
		localName: "VEGREVILLE/MINBURN COUNTY",
		population: 10323,
		percentFullyImmunized: 56.5,
	},
	{
		localName: "VERMILION RIVER COUNTY",
		population: 36740,
		percentFullyImmunized: 27.9,
	},
	{
		localName: "RED DEER - NORTH",
		population: 35640,
		percentFullyImmunized: 50,
	},
	{
		localName: "RED DEER - SW",
		population: 15679,
		percentFullyImmunized: 51.1,
	},
	{
		localName: "RED DEER - EAST",
		population: 55069,
		percentFullyImmunized: 57.3,
	},
	{
		localName: "EDMONTON - WOODCROFT EAST",
		population: 60664,
		percentFullyImmunized: 59.9,
	},
	{
		localName: "EDMONTON - WOODCROFT WEST",
		population: 33002,
		percentFullyImmunized: 63.2,
	},
	{
		localName: "EDMONTON - JASPER PLACE",
		population: 46923,
		percentFullyImmunized: 59.6,
	},
	{
		localName: "EDMONTON - WEST JASPER PLACE",
		population: 103462,
		percentFullyImmunized: 69.4,
	},
	{
		localName: "EDMONTON - CASTLE DOWNS",
		population: 71594,
		percentFullyImmunized: 60.5,
	},
	{
		localName: "EDMONTON - NORTHGATE",
		population: 82969,
		percentFullyImmunized: 59.1,
	},
	{
		localName: "EDMONTON - EASTWOOD",
		population: 72156,
		percentFullyImmunized: 55.4,
	},
	{
		localName: "EDMONTON - ABBOTTSFIELD",
		population: 14582,
		percentFullyImmunized: 50.5,
	},
	{
		localName: "EDMONTON - NE",
		population: 90743,
		percentFullyImmunized: 57.6,
	},
	{
		localName: "EDMONTON - BONNIE DOON",
		population: 96621,
		percentFullyImmunized: 67.6,
	},
	{
		localName: "EDMONTON - MILL WOODS WEST",
		population: 51150,
		percentFullyImmunized: 62,
	},
	{
		localName: "EDMONTON - MILL WOODS SOUTH & EAST",
		population: 85232,
		percentFullyImmunized: 65.1,
	},
	{
		localName: "EDMONTON - DUGGAN",
		population: 40132,
		percentFullyImmunized: 66.6,
	},
	{
		localName: "EDMONTON - TWIN BROOKS",
		population: 75969,
		percentFullyImmunized: 72.3,
	},
	{
		localName: "EDMONTON - RUTHERFORD",
		population: 112265,
		percentFullyImmunized: 66.5,
	},
	{
		localName: "STURGEON COUNTY WEST",
		population: 30154,
		percentFullyImmunized: 55.1,
	},
	{
		localName: "STURGEON COUNTY EAST",
		population: 6095,
		percentFullyImmunized: 55.2,
	},
	{
		localName: "FORT SASKATCHEWAN",
		population: 26795,
		percentFullyImmunized: 58.8,
	},
	{
		localName: "SHERWOOD PARK",
		population: 82033,
		percentFullyImmunized: 70.1,
	},
	{
		localName: "STRATHCONA COUNTY EXCLUDING SHERWOOD PARK",
		population: 17420,
		percentFullyImmunized: 63.1,
	},
	{ localName: "BEAUMONT", population: 25785, percentFullyImmunized: 59.6 },
	{
		localName: "LEDUC & DEVON",
		population: 43021,
		percentFullyImmunized: 56.8,
	},
	{ localName: "THORSBY", population: 9090, percentFullyImmunized: 48.6 },
	{
		localName: "STONY PLAIN & SPRUCE GROVE",
		population: 57833,
		percentFullyImmunized: 58,
	},
	{
		localName: "WESTVIEW EXCLUDING STONY PLAIN & SPRUCE GROVE",
		population: 36730,
		percentFullyImmunized: 51.6,
	},
	{ localName: "ST. ALBERT", population: 69588, percentFullyImmunized: 70.5 },
	{ localName: "JASPER", population: 5592, percentFullyImmunized: 68 },
	{ localName: "HINTON", population: 12260, percentFullyImmunized: 53.3 },
	{ localName: "EDSON", population: 16050, percentFullyImmunized: 47.5 },
	{ localName: "WHITECOURT", population: 14719, percentFullyImmunized: 44.7 },
	{
		localName: "MAYERTHORPE",
		population: 16200,
		percentFullyImmunized: 48.8,
	},
	{ localName: "BARRHEAD", population: 10948, percentFullyImmunized: 47.9 },
	{ localName: "WESTLOCK", population: 19168, percentFullyImmunized: 53.8 },
	{ localName: "FROG LAKE", population: 4827, percentFullyImmunized: 34.8 },
	{ localName: "ST. PAUL", population: 15522, percentFullyImmunized: 39.2 },
	{ localName: "SMOKY LAKE", population: 4728, percentFullyImmunized: 51.3 },
	{ localName: "COLD LAKE", population: 20716, percentFullyImmunized: 46.4 },
	{ localName: "BONNYVILLE", population: 16602, percentFullyImmunized: 42.2 },
	{ localName: "BOYLE", population: 3544, percentFullyImmunized: 44.4 },
	{ localName: "ATHABASCA", population: 10686, percentFullyImmunized: 55.1 },
	{
		localName: "LAC LA BICHE",
		population: 10392,
		percentFullyImmunized: 43.6,
	},
	{
		localName: "GRANDE CACHE",
		population: 4168,
		percentFullyImmunized: 44.8,
	},
	{ localName: "FOX CREEK", population: 2241, percentFullyImmunized: 45.7 },
	{ localName: "VALLEYVIEW", population: 7226, percentFullyImmunized: 39.6 },
	{
		localName: "BEAVERLODGE",
		population: 12199,
		percentFullyImmunized: 40.5,
	},
	{
		localName: "GRANDE PRAIRIE COUNTY",
		population: 20862,
		percentFullyImmunized: 42.6,
	},
	{ localName: "SWAN HILLS", population: 1336, percentFullyImmunized: 45.4 },
	{ localName: "SLAVE LAKE", population: 11676, percentFullyImmunized: 41.9 },
	{ localName: "WABASCA", population: 4238, percentFullyImmunized: 34.2 },
	{
		localName: "HIGH PRAIRIE",
		population: 11613,
		percentFullyImmunized: 33.8,
	},
	{ localName: "HIGH LEVEL", population: 25086, percentFullyImmunized: 14.1 },
	{ localName: "MANNING", population: 3290, percentFullyImmunized: 40.2 },
	{
		localName: "PEACE RIVER",
		population: 18611,
		percentFullyImmunized: 42.5,
	},
	{ localName: "FALHER", population: 4427, percentFullyImmunized: 48.1 },
	{
		localName: "SPIRIT RIVER",
		population: 6114,
		percentFullyImmunized: 40.7,
	},
	{ localName: "FAIRVIEW", population: 8131, percentFullyImmunized: 39.9 },
	{
		localName: "WOOD BUFFALO",
		population: 4062,
		percentFullyImmunized: 34.5,
	},
	{
		localName: "FORT MCMURRAY",
		population: 79416,
		percentFullyImmunized: 50,
	},
	{
		localName: "CITY OF GRANDE PRAIRIE",
		population: 74275,
		percentFullyImmunized: 43.3,
	},
];

function setup() {
	document.getElementById("data-display").innerHTML = JSON.stringify(
		condensedData,
		null,
		4
	);
}

window.onload = setup;
```

If you look at the website again, it should now look as follows:

![Display of condensed data on the website](/src/content/blog/2021-10-04-chart-js/resources/website2.jpg)

### Loading in Chart.js

Now that we have access to our data, we need access to Chart.js! Following the [excellent instructions at the Chart.js homepage](https://www.chartjs.org/docs/latest/), we can grab the latest version from the [Chart.js CDN](https://www.jsdelivr.com/package/npm/chart.js). Now we just need to add it to our website. If you want to follow along exactly be sure to grab that same version that I am using! We'll also want to create a new dummy `Chart` to ensure that the library was loaded correctly.

```diff
 <!-- index.html -->
 <!doctype html>
 <html>
 	<head>
 		<meta charset="utf-8">
+		<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/chart.js@3.5.1/dist/chart.min.js"></script>
 		<script type="text/javascript" src="./scripts/script.js"></script>
 		<link href="./styling/style.css" rel="stylesheet" />
 	</head>
 	<body>
 		<h1>An Introduction to Chart.js</h1>
 		<pre id="data-display"></pre>
 	</body>
 </html>
```

```diff
// script.js
const condensedData =
[{"localName":"CROWSNEST PASS","population":6280,"percentFullyImmunized":58.1},{"localName":"PINCHER CREEK","population":8344,"percentFullyImmunized":57.7},{"localName":"FORT MACLEOD","population":6753,"percentFullyImmunized":44.3},{"localName":"CARDSTON-KAINAI","population":16595,"percentFullyImmunized":48.6},{"localName":"COUNTY OF LETHBRIDGE","population":25820,"percentFullyImmunized":44},{"localName":"TABER MD","population":19028,"percentFullyImmunized":34.9},{"localName":"COUNTY OF WARNER","population":11104,"percentFullyImmunized":42.9},{"localName":"COUNTY OF FORTY MILE","population":6409,"percentFullyImmunized":28.3},{"localName":"NEWELL","population":27753,"percentFullyImmunized":46.9},{"localName":"OYEN","population":3486,"percentFullyImmunized":45.9},{"localName":"CYPRESS COUNTY","population":11298,"percentFullyImmunized":48.6},{"localName":"MEDICINE HAT","population":68115,"percentFullyImmunized":57.4},{"localName":"LETHBRIDGE - WEST","population":38163,"percentFullyImmunized":65.7},{"localName":"LETHBRIDGE - NORTH","population":27903,"percentFullyImmunized":61.8},{"localName":"LETHBRIDGE - SOUTH","population":34464,"percentFullyImmunized":65.3},{"localName":"CALGARY - UPPER NW","population":123679,"percentFullyImmunized":69.4},{"localName":"CALGARY - NORTH","population":116945,"percentFullyImmunized":67.6},{"localName":"CALGARY - NOSE HILL","population":78021,"percentFullyImmunized":65.8},{"localName":"CALGARY - LOWER NW","population":62696,"percentFullyImmunized":71.2},{"localName":"CALGARY - WEST BOW","population":21283,"percentFullyImmunized":65.7},{"localName":"CALGARY - CENTRE NORTH","population":44910,"percentFullyImmunized":68.7},{"localName":"CALGARY - UPPER NE","population":120999,"percentFullyImmunized":63.9},{"localName":"CALGARY - LOWER NE","population":96472,"percentFullyImmunized":58.3},{"localName":"CALGARY - EAST","population":72509,"percentFullyImmunized":56.7},{"localName":"CALGARY - SE","population":134420,"percentFullyImmunized":64},{"localName":"CALGARY - WEST","population":92320,"percentFullyImmunized":69.3},{"localName":"CALGARY - CENTRE","population":67568,"percentFullyImmunized":66.5},{"localName":"CALGARY - CENTRE WEST","population":65845,"percentFullyImmunized":67.7},{"localName":"CALGARY - ELBOW","population":40834,"percentFullyImmunized":69.8},{"localName":"CALGARY - FISH CREEK","population":111574,"percentFullyImmunized":66.5},{"localName":"CALGARY - SW","population":116934,"percentFullyImmunized":66.5},{"localName":"OKOTOKS-PRIDDIS","population":46042,"percentFullyImmunized":60},{"localName":"BLACK DIAMOND","population":8769,"percentFullyImmunized":52.9},{"localName":"HIGH RIVER","population":23739,"percentFullyImmunized":56.1},{"localName":"CLARESHOLM","population":6246,"percentFullyImmunized":56.9},{"localName":"VULCAN","population":6775,"percentFullyImmunized":47},{"localName":"AIRDRIE","population":73698,"percentFullyImmunized":56.8},{"localName":"CHESTERMERE","population":25015,"percentFullyImmunized":63},{"localName":"STRATHMORE","population":35685,"percentFullyImmunized":54.8},{"localName":"CROSSFIELD","population":9164,"percentFullyImmunized":50.4},{"localName":"DIDSBURY","population":16475,"percentFullyImmunized":50.3},{"localName":"COCHRANE-SPRINGBANK","population":50816,"percentFullyImmunized":63.2},{"localName":"CANMORE","population":27674,"percentFullyImmunized":64.3},{"localName":"BANFF","population":13451,"percentFullyImmunized":57.7},{"localName":"ROCKY MOUNTAIN HOUSE","population":20389,"percentFullyImmunized":43.3},{"localName":"DRAYTON VALLEY","population":18075,"percentFullyImmunized":40.6},{"localName":"SUNDRE","population":6782,"percentFullyImmunized":47.6},{"localName":"OLDS","population":12597,"percentFullyImmunized":54.9},{"localName":"INNISFAIL","population":15939,"percentFullyImmunized":57.1},{"localName":"RED DEER COUNTY","population":29495,"percentFullyImmunized":43.6},{"localName":"SYLVAN LAKE","population":18013,"percentFullyImmunized":42.9},{"localName":"THREE HILLS/HIGHWAY 21","population":10816,"percentFullyImmunized":45.5},{"localName":"STARLAND COUNTY/DRUMHELLER","population":11802,"percentFullyImmunized":55.8},{"localName":"PLANNING & SPECIAL AREA 2","population":3648,"percentFullyImmunized":48},{"localName":"STETTLER & COUNTY","population":12520,"percentFullyImmunized":45.8},{"localName":"CASTOR/CORONATION/CONSORT","population":6160,"percentFullyImmunized":44.3},{"localName":"WETASKIWIN COUNTY","population":33715,"percentFullyImmunized":46.8},{"localName":"PONOKA","population":12399,"percentFullyImmunized":47.5},{"localName":"RIMBEY","population":10013,"percentFullyImmunized":44.3},{"localName":"LACOMBE","population":23417,"percentFullyImmunized":48.1},{"localName":"CAMROSE & COUNTY","population":30125,"percentFullyImmunized":57.8},{"localName":"TOFIELD","population":7797,"percentFullyImmunized":51.5},{"localName":"VIKING","population":2351,"percentFullyImmunized":55.5},{"localName":"FLAGSTAFF COUNTY","population":8426,"percentFullyImmunized":55.7},{"localName":"MD OF PROVOST","population":4860,"percentFullyImmunized":50.1},{"localName":"MD OF WAINWRIGHT","population":11915,"percentFullyImmunized":54},{"localName":"LAMONT COUNTY","population":6388,"percentFullyImmunized":52.6},{"localName":"TWO HILLS COUNTY","population":5579,"percentFullyImmunized":30.5},{"localName":"VEGREVILLE/MINBURN COUNTY","population":10323,"percentFullyImmunized":56.5},{"localName":"VERMILION RIVER COUNTY","population":36740,"percentFullyImmunized":27.9},{"localName":"RED DEER - NORTH","population":35640,"percentFullyImmunized":50},{"localName":"RED DEER - SW","population":15679,"percentFullyImmunized":51.1},{"localName":"RED DEER - EAST","population":55069,"percentFullyImmunized":57.3},{"localName":"EDMONTON - WOODCROFT EAST","population":60664,"percentFullyImmunized":59.9},{"localName":"EDMONTON - WOODCROFT WEST","population":33002,"percentFullyImmunized":63.2},{"localName":"EDMONTON - JASPER PLACE","population":46923,"percentFullyImmunized":59.6},{"localName":"EDMONTON - WEST JASPER PLACE","population":103462,"percentFullyImmunized":69.4},{"localName":"EDMONTON - CASTLE DOWNS","population":71594,"percentFullyImmunized":60.5},{"localName":"EDMONTON - NORTHGATE","population":82969,"percentFullyImmunized":59.1},{"localName":"EDMONTON - EASTWOOD","population":72156,"percentFullyImmunized":55.4},{"localName":"EDMONTON - ABBOTTSFIELD","population":14582,"percentFullyImmunized":50.5},{"localName":"EDMONTON - NE","population":90743,"percentFullyImmunized":57.6},{"localName":"EDMONTON - BONNIE DOON","population":96621,"percentFullyImmunized":67.6},{"localName":"EDMONTON - MILL WOODS WEST","population":51150,"percentFullyImmunized":62},{"localName":"EDMONTON - MILL WOODS SOUTH & EAST","population":85232,"percentFullyImmunized":65.1},{"localName":"EDMONTON - DUGGAN","population":40132,"percentFullyImmunized":66.6},{"localName":"EDMONTON - TWIN BROOKS","population":75969,"percentFullyImmunized":72.3},{"localName":"EDMONTON - RUTHERFORD","population":112265,"percentFullyImmunized":66.5},{"localName":"STURGEON COUNTY WEST","population":30154,"percentFullyImmunized":55.1},{"localName":"STURGEON COUNTY EAST","population":6095,"percentFullyImmunized":55.2},{"localName":"FORT SASKATCHEWAN","population":26795,"percentFullyImmunized":58.8},{"localName":"SHERWOOD PARK","population":82033,"percentFullyImmunized":70.1},{"localName":"STRATHCONA COUNTY EXCLUDING SHERWOOD PARK","population":17420,"percentFullyImmunized":63.1},{"localName":"BEAUMONT","population":25785,"percentFullyImmunized":59.6},{"localName":"LEDUC & DEVON","population":43021,"percentFullyImmunized":56.8},{"localName":"THORSBY","population":9090,"percentFullyImmunized":48.6},{"localName":"STONY PLAIN & SPRUCE GROVE","population":57833,"percentFullyImmunized":58},{"localName":"WESTVIEW EXCLUDING STONY PLAIN & SPRUCE GROVE","population":36730,"percentFullyImmunized":51.6},{"localName":"ST. ALBERT","population":69588,"percentFullyImmunized":70.5},{"localName":"JASPER","population":5592,"percentFullyImmunized":68},{"localName":"HINTON","population":12260,"percentFullyImmunized":53.3},{"localName":"EDSON","population":16050,"percentFullyImmunized":47.5},{"localName":"WHITECOURT","population":14719,"percentFullyImmunized":44.7},{"localName":"MAYERTHORPE","population":16200,"percentFullyImmunized":48.8},{"localName":"BARRHEAD","population":10948,"percentFullyImmunized":47.9},{"localName":"WESTLOCK","population":19168,"percentFullyImmunized":53.8},{"localName":"FROG LAKE","population":4827,"percentFullyImmunized":34.8},{"localName":"ST. PAUL","population":15522,"percentFullyImmunized":39.2},{"localName":"SMOKY LAKE","population":4728,"percentFullyImmunized":51.3},{"localName":"COLD LAKE","population":20716,"percentFullyImmunized":46.4},{"localName":"BONNYVILLE","population":16602,"percentFullyImmunized":42.2},{"localName":"BOYLE","population":3544,"percentFullyImmunized":44.4},{"localName":"ATHABASCA","population":10686,"percentFullyImmunized":55.1},{"localName":"LAC LA BICHE","population":10392,"percentFullyImmunized":43.6},{"localName":"GRANDE CACHE","population":4168,"percentFullyImmunized":44.8},{"localName":"FOX CREEK","population":2241,"percentFullyImmunized":45.7},{"localName":"VALLEYVIEW","population":7226,"percentFullyImmunized":39.6},{"localName":"BEAVERLODGE","population":12199,"percentFullyImmunized":40.5},{"localName":"GRANDE PRAIRIE COUNTY","population":20862,"percentFullyImmunized":42.6},{"localName":"SWAN HILLS","population":1336,"percentFullyImmunized":45.4},{"localName":"SLAVE LAKE","population":11676,"percentFullyImmunized":41.9},{"localName":"WABASCA","population":4238,"percentFullyImmunized":34.2},{"localName":"HIGH PRAIRIE","population":11613,"percentFullyImmunized":33.8},{"localName":"HIGH LEVEL","population":25086,"percentFullyImmunized":14.1},{"localName":"MANNING","population":3290,"percentFullyImmunized":40.2},{"localName":"PEACE RIVER","population":18611,"percentFullyImmunized":42.5},{"localName":"FALHER","population":4427,"percentFullyImmunized":48.1},{"localName":"SPIRIT RIVER","population":6114,"percentFullyImmunized":40.7},{"localName":"FAIRVIEW","population":8131,"percentFullyImmunized":39.9},{"localName":"WOOD BUFFALO","population":4062,"percentFullyImmunized":34.5},{"localName":"FORT MCMURRAY","population":79416,"percentFullyImmunized":50},{"localName":"CITY OF GRANDE PRAIRIE","population":74275,"percentFullyImmunized":43.3}]

function setup() {
	document.getElementById('data-display').innerHTML = JSON.stringify(condensedData, null, 4)
+
+	//to ensure that the Chart.js library was correctly loaded
+	const chart = new Chart()
}

window.onload = setup
```

Note that although the appearance of the website will not have changed, you should see an error if you open up the developer console:

![Expected error: Failed to Create Chart](/src/content/blog/2021-10-04-chart-js/resources/expectedError.jpg)

This is expected - it is the result of not providing a place to actually render the new chart. We'll take care of that very soon!

## A Simple Bar Graph

(To start right from here, begin from [this commit](https://github.com/EricRobertCampbell/learning-chart-js/commit/14e33086e382c207c1e9135000602641329edfce))

So far we have done a lot of processing and setup, but haven't actually created a chart! Let's rectify that. Our first chart will be a simple bar graph comparing the vaccination percentage for each different region. We'll need to do two things:

1. Create a `<canvas>` element in `index.html`; the actual graph will be plotted here.
2. Update `script.js` to provide the appropriate data to create the graph

```diff
 <!-- index.html -->
 <!doctype html>
 <html>
 	<head>
 		<meta charset="utf-8">
 		<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/chart.js@3.5.1/dist/chart.min.js"></script>
 		<script type="text/javascript" src="./scripts/script.js"></script>
 		<link href="./styling/style.css" rel="stylesheet" />
 	</head>
 	<body>
 		<h1>An Introduction to Chart.js</h1>
-		<pre id="data-display"></pre>
+		<canvas id="graph"></canvas>
 	</body>
 </html>
```

```diff
// script.js
const condensedData =
[{"localName":"CROWSNEST PASS","population":6280,"percentFullyImmunized":58.1},{"localName":"PINCHER CREEK","population":8344,"percentFullyImmunized":57.7},{"localName":"FORT MACLEOD","population":6753,"percentFullyImmunized":44.3},{"localName":"CARDSTON-KAINAI","population":16595,"percentFullyImmunized":48.6},{"localName":"COUNTY OF LETHBRIDGE","population":25820,"percentFullyImmunized":44},{"localName":"TABER MD","population":19028,"percentFullyImmunized":34.9},{"localName":"COUNTY OF WARNER","population":11104,"percentFullyImmunized":42.9},{"localName":"COUNTY OF FORTY MILE","population":6409,"percentFullyImmunized":28.3},{"localName":"NEWELL","population":27753,"percentFullyImmunized":46.9},{"localName":"OYEN","population":3486,"percentFullyImmunized":45.9},{"localName":"CYPRESS COUNTY","population":11298,"percentFullyImmunized":48.6},{"localName":"MEDICINE HAT","population":68115,"percentFullyImmunized":57.4},{"localName":"LETHBRIDGE - WEST","population":38163,"percentFullyImmunized":65.7},{"localName":"LETHBRIDGE - NORTH","population":27903,"percentFullyImmunized":61.8},{"localName":"LETHBRIDGE - SOUTH","population":34464,"percentFullyImmunized":65.3},{"localName":"CALGARY - UPPER NW","population":123679,"percentFullyImmunized":69.4},{"localName":"CALGARY - NORTH","population":116945,"percentFullyImmunized":67.6},{"localName":"CALGARY - NOSE HILL","population":78021,"percentFullyImmunized":65.8},{"localName":"CALGARY - LOWER NW","population":62696,"percentFullyImmunized":71.2},{"localName":"CALGARY - WEST BOW","population":21283,"percentFullyImmunized":65.7},{"localName":"CALGARY - CENTRE NORTH","population":44910,"percentFullyImmunized":68.7},{"localName":"CALGARY - UPPER NE","population":120999,"percentFullyImmunized":63.9},{"localName":"CALGARY - LOWER NE","population":96472,"percentFullyImmunized":58.3},{"localName":"CALGARY - EAST","population":72509,"percentFullyImmunized":56.7},{"localName":"CALGARY - SE","population":134420,"percentFullyImmunized":64},{"localName":"CALGARY - WEST","population":92320,"percentFullyImmunized":69.3},{"localName":"CALGARY - CENTRE","population":67568,"percentFullyImmunized":66.5},{"localName":"CALGARY - CENTRE WEST","population":65845,"percentFullyImmunized":67.7},{"localName":"CALGARY - ELBOW","population":40834,"percentFullyImmunized":69.8},{"localName":"CALGARY - FISH CREEK","population":111574,"percentFullyImmunized":66.5},{"localName":"CALGARY - SW","population":116934,"percentFullyImmunized":66.5},{"localName":"OKOTOKS-PRIDDIS","population":46042,"percentFullyImmunized":60},{"localName":"BLACK DIAMOND","population":8769,"percentFullyImmunized":52.9},{"localName":"HIGH RIVER","population":23739,"percentFullyImmunized":56.1},{"localName":"CLARESHOLM","population":6246,"percentFullyImmunized":56.9},{"localName":"VULCAN","population":6775,"percentFullyImmunized":47},{"localName":"AIRDRIE","population":73698,"percentFullyImmunized":56.8},{"localName":"CHESTERMERE","population":25015,"percentFullyImmunized":63},{"localName":"STRATHMORE","population":35685,"percentFullyImmunized":54.8},{"localName":"CROSSFIELD","population":9164,"percentFullyImmunized":50.4},{"localName":"DIDSBURY","population":16475,"percentFullyImmunized":50.3},{"localName":"COCHRANE-SPRINGBANK","population":50816,"percentFullyImmunized":63.2},{"localName":"CANMORE","population":27674,"percentFullyImmunized":64.3},{"localName":"BANFF","population":13451,"percentFullyImmunized":57.7},{"localName":"ROCKY MOUNTAIN HOUSE","population":20389,"percentFullyImmunized":43.3},{"localName":"DRAYTON VALLEY","population":18075,"percentFullyImmunized":40.6},{"localName":"SUNDRE","population":6782,"percentFullyImmunized":47.6},{"localName":"OLDS","population":12597,"percentFullyImmunized":54.9},{"localName":"INNISFAIL","population":15939,"percentFullyImmunized":57.1},{"localName":"RED DEER COUNTY","population":29495,"percentFullyImmunized":43.6},{"localName":"SYLVAN LAKE","population":18013,"percentFullyImmunized":42.9},{"localName":"THREE HILLS/HIGHWAY 21","population":10816,"percentFullyImmunized":45.5},{"localName":"STARLAND COUNTY/DRUMHELLER","population":11802,"percentFullyImmunized":55.8},{"localName":"PLANNING & SPECIAL AREA 2","population":3648,"percentFullyImmunized":48},{"localName":"STETTLER & COUNTY","population":12520,"percentFullyImmunized":45.8},{"localName":"CASTOR/CORONATION/CONSORT","population":6160,"percentFullyImmunized":44.3},{"localName":"WETASKIWIN COUNTY","population":33715,"percentFullyImmunized":46.8},{"localName":"PONOKA","population":12399,"percentFullyImmunized":47.5},{"localName":"RIMBEY","population":10013,"percentFullyImmunized":44.3},{"localName":"LACOMBE","population":23417,"percentFullyImmunized":48.1},{"localName":"CAMROSE & COUNTY","population":30125,"percentFullyImmunized":57.8},{"localName":"TOFIELD","population":7797,"percentFullyImmunized":51.5},{"localName":"VIKING","population":2351,"percentFullyImmunized":55.5},{"localName":"FLAGSTAFF COUNTY","population":8426,"percentFullyImmunized":55.7},{"localName":"MD OF PROVOST","population":4860,"percentFullyImmunized":50.1},{"localName":"MD OF WAINWRIGHT","population":11915,"percentFullyImmunized":54},{"localName":"LAMONT COUNTY","population":6388,"percentFullyImmunized":52.6},{"localName":"TWO HILLS COUNTY","population":5579,"percentFullyImmunized":30.5},{"localName":"VEGREVILLE/MINBURN COUNTY","population":10323,"percentFullyImmunized":56.5},{"localName":"VERMILION RIVER COUNTY","population":36740,"percentFullyImmunized":27.9},{"localName":"RED DEER - NORTH","population":35640,"percentFullyImmunized":50},{"localName":"RED DEER - SW","population":15679,"percentFullyImmunized":51.1},{"localName":"RED DEER - EAST","population":55069,"percentFullyImmunized":57.3},{"localName":"EDMONTON - WOODCROFT EAST","population":60664,"percentFullyImmunized":59.9},{"localName":"EDMONTON - WOODCROFT WEST","population":33002,"percentFullyImmunized":63.2},{"localName":"EDMONTON - JASPER PLACE","population":46923,"percentFullyImmunized":59.6},{"localName":"EDMONTON - WEST JASPER PLACE","population":103462,"percentFullyImmunized":69.4},{"localName":"EDMONTON - CASTLE DOWNS","population":71594,"percentFullyImmunized":60.5},{"localName":"EDMONTON - NORTHGATE","population":82969,"percentFullyImmunized":59.1},{"localName":"EDMONTON - EASTWOOD","population":72156,"percentFullyImmunized":55.4},{"localName":"EDMONTON - ABBOTTSFIELD","population":14582,"percentFullyImmunized":50.5},{"localName":"EDMONTON - NE","population":90743,"percentFullyImmunized":57.6},{"localName":"EDMONTON - BONNIE DOON","population":96621,"percentFullyImmunized":67.6},{"localName":"EDMONTON - MILL WOODS WEST","population":51150,"percentFullyImmunized":62},{"localName":"EDMONTON - MILL WOODS SOUTH & EAST","population":85232,"percentFullyImmunized":65.1},{"localName":"EDMONTON - DUGGAN","population":40132,"percentFullyImmunized":66.6},{"localName":"EDMONTON - TWIN BROOKS","population":75969,"percentFullyImmunized":72.3},{"localName":"EDMONTON - RUTHERFORD","population":112265,"percentFullyImmunized":66.5},{"localName":"STURGEON COUNTY WEST","population":30154,"percentFullyImmunized":55.1},{"localName":"STURGEON COUNTY EAST","population":6095,"percentFullyImmunized":55.2},{"localName":"FORT SASKATCHEWAN","population":26795,"percentFullyImmunized":58.8},{"localName":"SHERWOOD PARK","population":82033,"percentFullyImmunized":70.1},{"localName":"STRATHCONA COUNTY EXCLUDING SHERWOOD PARK","population":17420,"percentFullyImmunized":63.1},{"localName":"BEAUMONT","population":25785,"percentFullyImmunized":59.6},{"localName":"LEDUC & DEVON","population":43021,"percentFullyImmunized":56.8},{"localName":"THORSBY","population":9090,"percentFullyImmunized":48.6},{"localName":"STONY PLAIN & SPRUCE GROVE","population":57833,"percentFullyImmunized":58},{"localName":"WESTVIEW EXCLUDING STONY PLAIN & SPRUCE GROVE","population":36730,"percentFullyImmunized":51.6},{"localName":"ST. ALBERT","population":69588,"percentFullyImmunized":70.5},{"localName":"JASPER","population":5592,"percentFullyImmunized":68},{"localName":"HINTON","population":12260,"percentFullyImmunized":53.3},{"localName":"EDSON","population":16050,"percentFullyImmunized":47.5},{"localName":"WHITECOURT","population":14719,"percentFullyImmunized":44.7},{"localName":"MAYERTHORPE","population":16200,"percentFullyImmunized":48.8},{"localName":"BARRHEAD","population":10948,"percentFullyImmunized":47.9},{"localName":"WESTLOCK","population":19168,"percentFullyImmunized":53.8},{"localName":"FROG LAKE","population":4827,"percentFullyImmunized":34.8},{"localName":"ST. PAUL","population":15522,"percentFullyImmunized":39.2},{"localName":"SMOKY LAKE","population":4728,"percentFullyImmunized":51.3},{"localName":"COLD LAKE","population":20716,"percentFullyImmunized":46.4},{"localName":"BONNYVILLE","population":16602,"percentFullyImmunized":42.2},{"localName":"BOYLE","population":3544,"percentFullyImmunized":44.4},{"localName":"ATHABASCA","population":10686,"percentFullyImmunized":55.1},{"localName":"LAC LA BICHE","population":10392,"percentFullyImmunized":43.6},{"localName":"GRANDE CACHE","population":4168,"percentFullyImmunized":44.8},{"localName":"FOX CREEK","population":2241,"percentFullyImmunized":45.7},{"localName":"VALLEYVIEW","population":7226,"percentFullyImmunized":39.6},{"localName":"BEAVERLODGE","population":12199,"percentFullyImmunized":40.5},{"localName":"GRANDE PRAIRIE COUNTY","population":20862,"percentFullyImmunized":42.6},{"localName":"SWAN HILLS","population":1336,"percentFullyImmunized":45.4},{"localName":"SLAVE LAKE","population":11676,"percentFullyImmunized":41.9},{"localName":"WABASCA","population":4238,"percentFullyImmunized":34.2},{"localName":"HIGH PRAIRIE","population":11613,"percentFullyImmunized":33.8},{"localName":"HIGH LEVEL","population":25086,"percentFullyImmunized":14.1},{"localName":"MANNING","population":3290,"percentFullyImmunized":40.2},{"localName":"PEACE RIVER","population":18611,"percentFullyImmunized":42.5},{"localName":"FALHER","population":4427,"percentFullyImmunized":48.1},{"localName":"SPIRIT RIVER","population":6114,"percentFullyImmunized":40.7},{"localName":"FAIRVIEW","population":8131,"percentFullyImmunized":39.9},{"localName":"WOOD BUFFALO","population":4062,"percentFullyImmunized":34.5},{"localName":"FORT MCMURRAY","population":79416,"percentFullyImmunized":50},{"localName":"CITY OF GRANDE PRAIRIE","population":74275,"percentFullyImmunized":43.3}]

function setup() {
-	document.getElementById('data-display').innerHTML = JSON.stringify(condensedData, null, 4)
-
-	//to ensure that the Chart.js library was correctly loaded
-	const chart = new Chart()
+	const ctx = document.getElementById('graph').getContext('2d')
+	const options = {
+		type: 'bar',
+		data: {
+			labels: condensedData.map(item => item.localName),
+			datasets: [
+				{
+					label: 'Percent Fully Immunized',
+					data: condensedData.map(item => item.percentFullyImmunized)
+				}
+			]
+		}
+	}
+	const chart = new Chart(ctx, options)
}

window.onload = setup
```

When you open up the website, you should see the following chart greet you:

![Region against percentage fully vaccinated](/src/content/blog/2021-10-04-chart-js/resources/chart-1.png)

In order to create this, we had to create a new `Chart` object. This chart is drawn into a canvas element though a 2D context, which is what we passed into the constructor as the first argument. The second argument specified what the chart should actually look like. In our case, we indicate that it is a bar graph, and that the labels (x axis) should be the local name while the value (y axis) should be the percentage vaccinated. Notice that `datasets` is an array - if we wanted we could specify multiple datasets and have them all displayed on the same set of axes.

While this is pretty nice right off the bat (for instance: hover over one of the bars and it will tell you some information about it!), there are a few things we could do right away to make it nicer. For instance, the regions as not ordered nicely, it lacks a title, and each of the bars is an identical, rather dull colour.

To help us understand the data, we'll order the regions based on their percent vaccinated - from lowest to highest.

The title itself isn't bad to add - we just add the title as a plugin. It turns out that there are [a lot of options for the title](https://www.chartjs.org/docs/next/configuration/title.html), but we'll keep it simple and just have a plain text title.

For the colour we can be a little more creative. To make the graph a little easier to grab information from at a glance, let's colour a bar with a 0% vaccination rate red and one with a 100% vaccination rate green, and ones between those value coloured proportionally.

```diff
 // script.js
 const condensedData =
 [{"localName":"CROWSNEST PASS","population":6280,"percentFullyImmunized":58.1},{"localName":"PINCHER CREEK","population":8344,"percentFullyImmunized":57.7},{"localName":"FORT MACLEOD","population":6753,"percentFullyImmunized":44.3},{"localName":"CARDSTON-KAINAI","population":16595,"percentFullyImmunized":48.6},{"localName":"COUNTY OF LETHBRIDGE","population":25820,"percentFullyImmunized":44},{"localName":"TABER MD","population":19028,"percentFullyImmunized":34.9},{"localName":"COUNTY OF WARNER","population":11104,"percentFullyImmunized":42.9},{"localName":"COUNTY OF FORTY MILE","population":6409,"percentFullyImmunized":28.3},{"localName":"NEWELL","population":27753,"percentFullyImmunized":46.9},{"localName":"OYEN","population":3486,"percentFullyImmunized":45.9},{"localName":"CYPRESS COUNTY","population":11298,"percentFullyImmunized":48.6},{"localName":"MEDICINE HAT","population":68115,"percentFullyImmunized":57.4},{"localName":"LETHBRIDGE - WEST","population":38163,"percentFullyImmunized":65.7},{"localName":"LETHBRIDGE - NORTH","population":27903,"percentFullyImmunized":61.8},{"localName":"LETHBRIDGE - SOUTH","population":34464,"percentFullyImmunized":65.3},{"localName":"CALGARY - UPPER NW","population":123679,"percentFullyImmunized":69.4},{"localName":"CALGARY - NORTH","population":116945,"percentFullyImmunized":67.6},{"localName":"CALGARY - NOSE HILL","population":78021,"percentFullyImmunized":65.8},{"localName":"CALGARY - LOWER NW","population":62696,"percentFullyImmunized":71.2},{"localName":"CALGARY - WEST BOW","population":21283,"percentFullyImmunized":65.7},{"localName":"CALGARY - CENTRE NORTH","population":44910,"percentFullyImmunized":68.7},{"localName":"CALGARY - UPPER NE","population":120999,"percentFullyImmunized":63.9},{"localName":"CALGARY - LOWER NE","population":96472,"percentFullyImmunized":58.3},{"localName":"CALGARY - EAST","population":72509,"percentFullyImmunized":56.7},{"localName":"CALGARY - SE","population":134420,"percentFullyImmunized":64},{"localName":"CALGARY - WEST","population":92320,"percentFullyImmunized":69.3},{"localName":"CALGARY - CENTRE","population":67568,"percentFullyImmunized":66.5},{"localName":"CALGARY - CENTRE WEST","population":65845,"percentFullyImmunized":67.7},{"localName":"CALGARY - ELBOW","population":40834,"percentFullyImmunized":69.8},{"localName":"CALGARY - FISH CREEK","population":111574,"percentFullyImmunized":66.5},{"localName":"CALGARY - SW","population":116934,"percentFullyImmunized":66.5},{"localName":"OKOTOKS-PRIDDIS","population":46042,"percentFullyImmunized":60},{"localName":"BLACK DIAMOND","population":8769,"percentFullyImmunized":52.9},{"localName":"HIGH RIVER","population":23739,"percentFullyImmunized":56.1},{"localName":"CLARESHOLM","population":6246,"percentFullyImmunized":56.9},{"localName":"VULCAN","population":6775,"percentFullyImmunized":47},{"localName":"AIRDRIE","population":73698,"percentFullyImmunized":56.8},{"localName":"CHESTERMERE","population":25015,"percentFullyImmunized":63},{"localName":"STRATHMORE","population":35685,"percentFullyImmunized":54.8},{"localName":"CROSSFIELD","population":9164,"percentFullyImmunized":50.4},{"localName":"DIDSBURY","population":16475,"percentFullyImmunized":50.3},{"localName":"COCHRANE-SPRINGBANK","population":50816,"percentFullyImmunized":63.2},{"localName":"CANMORE","population":27674,"percentFullyImmunized":64.3},{"localName":"BANFF","population":13451,"percentFullyImmunized":57.7},{"localName":"ROCKY MOUNTAIN HOUSE","population":20389,"percentFullyImmunized":43.3},{"localName":"DRAYTON VALLEY","population":18075,"percentFullyImmunized":40.6},{"localName":"SUNDRE","population":6782,"percentFullyImmunized":47.6},{"localName":"OLDS","population":12597,"percentFullyImmunized":54.9},{"localName":"INNISFAIL","population":15939,"percentFullyImmunized":57.1},{"localName":"RED DEER COUNTY","population":29495,"percentFullyImmunized":43.6},{"localName":"SYLVAN LAKE","population":18013,"percentFullyImmunized":42.9},{"localName":"THREE HILLS/HIGHWAY 21","population":10816,"percentFullyImmunized":45.5},{"localName":"STARLAND COUNTY/DRUMHELLER","population":11802,"percentFullyImmunized":55.8},{"localName":"PLANNING & SPECIAL AREA 2","population":3648,"percentFullyImmunized":48},{"localName":"STETTLER & COUNTY","population":12520,"percentFullyImmunized":45.8},{"localName":"CASTOR/CORONATION/CONSORT","population":6160,"percentFullyImmunized":44.3},{"localName":"WETASKIWIN COUNTY","population":33715,"percentFullyImmunized":46.8},{"localName":"PONOKA","population":12399,"percentFullyImmunized":47.5},{"localName":"RIMBEY","population":10013,"percentFullyImmunized":44.3},{"localName":"LACOMBE","population":23417,"percentFullyImmunized":48.1},{"localName":"CAMROSE & COUNTY","population":30125,"percentFullyImmunized":57.8},{"localName":"TOFIELD","population":7797,"percentFullyImmunized":51.5},{"localName":"VIKING","population":2351,"percentFullyImmunized":55.5},{"localName":"FLAGSTAFF COUNTY","population":8426,"percentFullyImmunized":55.7},{"localName":"MD OF PROVOST","population":4860,"percentFullyImmunized":50.1},{"localName":"MD OF WAINWRIGHT","population":11915,"percentFullyImmunized":54},{"localName":"LAMONT COUNTY","population":6388,"percentFullyImmunized":52.6},{"localName":"TWO HILLS COUNTY","population":5579,"percentFullyImmunized":30.5},{"localName":"VEGREVILLE/MINBURN COUNTY","population":10323,"percentFullyImmunized":56.5},{"localName":"VERMILION RIVER COUNTY","population":36740,"percentFullyImmunized":27.9},{"localName":"RED DEER - NORTH","population":35640,"percentFullyImmunized":50},{"localName":"RED DEER - SW","population":15679,"percentFullyImmunized":51.1},{"localName":"RED DEER - EAST","population":55069,"percentFullyImmunized":57.3},{"localName":"EDMONTON - WOODCROFT EAST","population":60664,"percentFullyImmunized":59.9},{"localName":"EDMONTON - WOODCROFT WEST","population":33002,"percentFullyImmunized":63.2},{"localName":"EDMONTON - JASPER PLACE","population":46923,"percentFullyImmunized":59.6},{"localName":"EDMONTON - WEST JASPER PLACE","population":103462,"percentFullyImmunized":69.4},{"localName":"EDMONTON - CASTLE DOWNS","population":71594,"percentFullyImmunized":60.5},{"localName":"EDMONTON - NORTHGATE","population":82969,"percentFullyImmunized":59.1},{"localName":"EDMONTON - EASTWOOD","population":72156,"percentFullyImmunized":55.4},{"localName":"EDMONTON - ABBOTTSFIELD","population":14582,"percentFullyImmunized":50.5},{"localName":"EDMONTON - NE","population":90743,"percentFullyImmunized":57.6},{"localName":"EDMONTON - BONNIE DOON","population":96621,"percentFullyImmunized":67.6},{"localName":"EDMONTON - MILL WOODS WEST","population":51150,"percentFullyImmunized":62},{"localName":"EDMONTON - MILL WOODS SOUTH & EAST","population":85232,"percentFullyImmunized":65.1},{"localName":"EDMONTON - DUGGAN","population":40132,"percentFullyImmunized":66.6},{"localName":"EDMONTON - TWIN BROOKS","population":75969,"percentFullyImmunized":72.3},{"localName":"EDMONTON - RUTHERFORD","population":112265,"percentFullyImmunized":66.5},{"localName":"STURGEON COUNTY WEST","population":30154,"percentFullyImmunized":55.1},{"localName":"STURGEON COUNTY EAST","population":6095,"percentFullyImmunized":55.2},{"localName":"FORT SASKATCHEWAN","population":26795,"percentFullyImmunized":58.8},{"localName":"SHERWOOD PARK","population":82033,"percentFullyImmunized":70.1},{"localName":"STRATHCONA COUNTY EXCLUDING SHERWOOD PARK","population":17420,"percentFullyImmunized":63.1},{"localName":"BEAUMONT","population":25785,"percentFullyImmunized":59.6},{"localName":"LEDUC & DEVON","population":43021,"percentFullyImmunized":56.8},{"localName":"THORSBY","population":9090,"percentFullyImmunized":48.6},{"localName":"STONY PLAIN & SPRUCE GROVE","population":57833,"percentFullyImmunized":58},{"localName":"WESTVIEW EXCLUDING STONY PLAIN & SPRUCE GROVE","population":36730,"percentFullyImmunized":51.6},{"localName":"ST. ALBERT","population":69588,"percentFullyImmunized":70.5},{"localName":"JASPER","population":5592,"percentFullyImmunized":68},{"localName":"HINTON","population":12260,"percentFullyImmunized":53.3},{"localName":"EDSON","population":16050,"percentFullyImmunized":47.5},{"localName":"WHITECOURT","population":14719,"percentFullyImmunized":44.7},{"localName":"MAYERTHORPE","population":16200,"percentFullyImmunized":48.8},{"localName":"BARRHEAD","population":10948,"percentFullyImmunized":47.9},{"localName":"WESTLOCK","population":19168,"percentFullyImmunized":53.8},{"localName":"FROG LAKE","population":4827,"percentFullyImmunized":34.8},{"localName":"ST. PAUL","population":15522,"percentFullyImmunized":39.2},{"localName":"SMOKY LAKE","population":4728,"percentFullyImmunized":51.3},{"localName":"COLD LAKE","population":20716,"percentFullyImmunized":46.4},{"localName":"BONNYVILLE","population":16602,"percentFullyImmunized":42.2},{"localName":"BOYLE","population":3544,"percentFullyImmunized":44.4},{"localName":"ATHABASCA","population":10686,"percentFullyImmunized":55.1},{"localName":"LAC LA BICHE","population":10392,"percentFullyImmunized":43.6},{"localName":"GRANDE CACHE","population":4168,"percentFullyImmunized":44.8},{"localName":"FOX CREEK","population":2241,"percentFullyImmunized":45.7},{"localName":"VALLEYVIEW","population":7226,"percentFullyImmunized":39.6},{"localName":"BEAVERLODGE","population":12199,"percentFullyImmunized":40.5},{"localName":"GRANDE PRAIRIE COUNTY","population":20862,"percentFullyImmunized":42.6},{"localName":"SWAN HILLS","population":1336,"percentFullyImmunized":45.4},{"localName":"SLAVE LAKE","population":11676,"percentFullyImmunized":41.9},{"localName":"WABASCA","population":4238,"percentFullyImmunized":34.2},{"localName":"HIGH PRAIRIE","population":11613,"percentFullyImmunized":33.8},{"localName":"HIGH LEVEL","population":25086,"percentFullyImmunized":14.1},{"localName":"MANNING","population":3290,"percentFullyImmunized":40.2},{"localName":"PEACE RIVER","population":18611,"percentFullyImmunized":42.5},{"localName":"FALHER","population":4427,"percentFullyImmunized":48.1},{"localName":"SPIRIT RIVER","population":6114,"percentFullyImmunized":40.7},{"localName":"FAIRVIEW","population":8131,"percentFullyImmunized":39.9},{"localName":"WOOD BUFFALO","population":4062,"percentFullyImmunized":34.5},{"localName":"FORT MCMURRAY","population":79416,"percentFullyImmunized":50},{"localName":"CITY OF GRANDE PRAIRIE","population":74275,"percentFullyImmunized":43.3}]

+const orderedData = condensedData.sort((a, b) => a.percentFullyImmunized - b.percentFullyImmunized)
+
+function generateColourInRedGreenIntervalByProportion(prop) {
+	return `rgb(255, ${255 * prop}, 0)`;
+}
+
 function setup() {
 	const ctx = document.getElementById('graph').getContext('2d')
 	const options = {
 		type: 'bar',
 		data: {
-			labels: condensedData.map(item => item.localName),
+			labels: orderedData.map(item => item.localName),
 			datasets: [
 				{
 					label: 'Percent Fully Immunized',
-					data: condensedData.map(item => item.percentFullyImmunized),
+					data: orderedData.map(item => item.percentFullyImmunized),
+					backgroundColor: orderedData.map(item => generateColourInRedGreenIntervalByProportion(item.percentFullyImmunized / 100))
 				}
 			]
 		},
+		options: {
+			plugins: {
+				title: {
+					display: true,
+					text: 'Percent Vaccination for Alberta Regions',
+				},
+			},
+		},
 	};
 	const chart = new Chart(ctx, options)
 }

 window.onload = setup
```

And we immediately see a much nicer chart:

![Region against vaccination rate, ordered and coloured](/src/content/blog/2021-10-04-chart-js/resources/chart-2.png)

## Scatter Plot

(To start right from here, begin from [this commit](https://github.com/EricRobertCampbell/learning-chart-js/commit/5ffb8d902b7486a1f4e36fb6eb24ad1ac8e35baf))

Looking at this (beautiful) chart, something that I noticed is that the regions at the far left (with low vaccination rates) are either regions that I know have a small population, or ones that I have not heard of (perhaps because of their small population?). In contrast, the regions in the far right, with (relatively) high vaccination rates, are regions in Calgary and Edmonton, with presumably higher populations. However, I could also be wrong - I don't actually know how the health regions are decided. So, let's find out! We'll create a scatter plot of the data, with population plotted on the x axis and perccent vaccinated on the y axis. While we're at it, let's add labels to the axes to help us with interpreting the data.

```diff
 // script.js
 const condensedData =
 [{"localName":"CROWSNEST PASS","population":6280,"percentFullyImmunized":58.1},{"localName":"PINCHER CREEK","population":8344,"percentFullyImmunized":57.7},{"localName":"FORT MACLEOD","population":6753,"percentFullyImmunized":44.3},{"localName":"CARDSTON-KAINAI","population":16595,"percentFullyImmunized":48.6},{"localName":"COUNTY OF LETHBRIDGE","population":25820,"percentFullyImmunized":44},{"localName":"TABER MD","population":19028,"percentFullyImmunized":34.9},{"localName":"COUNTY OF WARNER","population":11104,"percentFullyImmunized":42.9},{"localName":"COUNTY OF FORTY MILE","population":6409,"percentFullyImmunized":28.3},{"localName":"NEWELL","population":27753,"percentFullyImmunized":46.9},{"localName":"OYEN","population":3486,"percentFullyImmunized":45.9},{"localName":"CYPRESS COUNTY","population":11298,"percentFullyImmunized":48.6},{"localName":"MEDICINE HAT","population":68115,"percentFullyImmunized":57.4},{"localName":"LETHBRIDGE - WEST","population":38163,"percentFullyImmunized":65.7},{"localName":"LETHBRIDGE - NORTH","population":27903,"percentFullyImmunized":61.8},{"localName":"LETHBRIDGE - SOUTH","population":34464,"percentFullyImmunized":65.3},{"localName":"CALGARY - UPPER NW","population":123679,"percentFullyImmunized":69.4},{"localName":"CALGARY - NORTH","population":116945,"percentFullyImmunized":67.6},{"localName":"CALGARY - NOSE HILL","population":78021,"percentFullyImmunized":65.8},{"localName":"CALGARY - LOWER NW","population":62696,"percentFullyImmunized":71.2},{"localName":"CALGARY - WEST BOW","population":21283,"percentFullyImmunized":65.7},{"localName":"CALGARY - CENTRE NORTH","population":44910,"percentFullyImmunized":68.7},{"localName":"CALGARY - UPPER NE","population":120999,"percentFullyImmunized":63.9},{"localName":"CALGARY - LOWER NE","population":96472,"percentFullyImmunized":58.3},{"localName":"CALGARY - EAST","population":72509,"percentFullyImmunized":56.7},{"localName":"CALGARY - SE","population":134420,"percentFullyImmunized":64},{"localName":"CALGARY - WEST","population":92320,"percentFullyImmunized":69.3},{"localName":"CALGARY - CENTRE","population":67568,"percentFullyImmunized":66.5},{"localName":"CALGARY - CENTRE WEST","population":65845,"percentFullyImmunized":67.7},{"localName":"CALGARY - ELBOW","population":40834,"percentFullyImmunized":69.8},{"localName":"CALGARY - FISH CREEK","population":111574,"percentFullyImmunized":66.5},{"localName":"CALGARY - SW","population":116934,"percentFullyImmunized":66.5},{"localName":"OKOTOKS-PRIDDIS","population":46042,"percentFullyImmunized":60},{"localName":"BLACK DIAMOND","population":8769,"percentFullyImmunized":52.9},{"localName":"HIGH RIVER","population":23739,"percentFullyImmunized":56.1},{"localName":"CLARESHOLM","population":6246,"percentFullyImmunized":56.9},{"localName":"VULCAN","population":6775,"percentFullyImmunized":47},{"localName":"AIRDRIE","population":73698,"percentFullyImmunized":56.8},{"localName":"CHESTERMERE","population":25015,"percentFullyImmunized":63},{"localName":"STRATHMORE","population":35685,"percentFullyImmunized":54.8},{"localName":"CROSSFIELD","population":9164,"percentFullyImmunized":50.4},{"localName":"DIDSBURY","population":16475,"percentFullyImmunized":50.3},{"localName":"COCHRANE-SPRINGBANK","population":50816,"percentFullyImmunized":63.2},{"localName":"CANMORE","population":27674,"percentFullyImmunized":64.3},{"localName":"BANFF","population":13451,"percentFullyImmunized":57.7},{"localName":"ROCKY MOUNTAIN HOUSE","population":20389,"percentFullyImmunized":43.3},{"localName":"DRAYTON VALLEY","population":18075,"percentFullyImmunized":40.6},{"localName":"SUNDRE","population":6782,"percentFullyImmunized":47.6},{"localName":"OLDS","population":12597,"percentFullyImmunized":54.9},{"localName":"INNISFAIL","population":15939,"percentFullyImmunized":57.1},{"localName":"RED DEER COUNTY","population":29495,"percentFullyImmunized":43.6},{"localName":"SYLVAN LAKE","population":18013,"percentFullyImmunized":42.9},{"localName":"THREE HILLS/HIGHWAY 21","population":10816,"percentFullyImmunized":45.5},{"localName":"STARLAND COUNTY/DRUMHELLER","population":11802,"percentFullyImmunized":55.8},{"localName":"PLANNING & SPECIAL AREA 2","population":3648,"percentFullyImmunized":48},{"localName":"STETTLER & COUNTY","population":12520,"percentFullyImmunized":45.8},{"localName":"CASTOR/CORONATION/CONSORT","population":6160,"percentFullyImmunized":44.3},{"localName":"WETASKIWIN COUNTY","population":33715,"percentFullyImmunized":46.8},{"localName":"PONOKA","population":12399,"percentFullyImmunized":47.5},{"localName":"RIMBEY","population":10013,"percentFullyImmunized":44.3},{"localName":"LACOMBE","population":23417,"percentFullyImmunized":48.1},{"localName":"CAMROSE & COUNTY","population":30125,"percentFullyImmunized":57.8},{"localName":"TOFIELD","population":7797,"percentFullyImmunized":51.5},{"localName":"VIKING","population":2351,"percentFullyImmunized":55.5},{"localName":"FLAGSTAFF COUNTY","population":8426,"percentFullyImmunized":55.7},{"localName":"MD OF PROVOST","population":4860,"percentFullyImmunized":50.1},{"localName":"MD OF WAINWRIGHT","population":11915,"percentFullyImmunized":54},{"localName":"LAMONT COUNTY","population":6388,"percentFullyImmunized":52.6},{"localName":"TWO HILLS COUNTY","population":5579,"percentFullyImmunized":30.5},{"localName":"VEGREVILLE/MINBURN COUNTY","population":10323,"percentFullyImmunized":56.5},{"localName":"VERMILION RIVER COUNTY","population":36740,"percentFullyImmunized":27.9},{"localName":"RED DEER - NORTH","population":35640,"percentFullyImmunized":50},{"localName":"RED DEER - SW","population":15679,"percentFullyImmunized":51.1},{"localName":"RED DEER - EAST","population":55069,"percentFullyImmunized":57.3},{"localName":"EDMONTON - WOODCROFT EAST","population":60664,"percentFullyImmunized":59.9},{"localName":"EDMONTON - WOODCROFT WEST","population":33002,"percentFullyImmunized":63.2},{"localName":"EDMONTON - JASPER PLACE","population":46923,"percentFullyImmunized":59.6},{"localName":"EDMONTON - WEST JASPER PLACE","population":103462,"percentFullyImmunized":69.4},{"localName":"EDMONTON - CASTLE DOWNS","population":71594,"percentFullyImmunized":60.5},{"localName":"EDMONTON - NORTHGATE","population":82969,"percentFullyImmunized":59.1},{"localName":"EDMONTON - EASTWOOD","population":72156,"percentFullyImmunized":55.4},{"localName":"EDMONTON - ABBOTTSFIELD","population":14582,"percentFullyImmunized":50.5},{"localName":"EDMONTON - NE","population":90743,"percentFullyImmunized":57.6},{"localName":"EDMONTON - BONNIE DOON","population":96621,"percentFullyImmunized":67.6},{"localName":"EDMONTON - MILL WOODS WEST","population":51150,"percentFullyImmunized":62},{"localName":"EDMONTON - MILL WOODS SOUTH & EAST","population":85232,"percentFullyImmunized":65.1},{"localName":"EDMONTON - DUGGAN","population":40132,"percentFullyImmunized":66.6},{"localName":"EDMONTON - TWIN BROOKS","population":75969,"percentFullyImmunized":72.3},{"localName":"EDMONTON - RUTHERFORD","population":112265,"percentFullyImmunized":66.5},{"localName":"STURGEON COUNTY WEST","population":30154,"percentFullyImmunized":55.1},{"localName":"STURGEON COUNTY EAST","population":6095,"percentFullyImmunized":55.2},{"localName":"FORT SASKATCHEWAN","population":26795,"percentFullyImmunized":58.8},{"localName":"SHERWOOD PARK","population":82033,"percentFullyImmunized":70.1},{"localName":"STRATHCONA COUNTY EXCLUDING SHERWOOD PARK","population":17420,"percentFullyImmunized":63.1},{"localName":"BEAUMONT","population":25785,"percentFullyImmunized":59.6},{"localName":"LEDUC & DEVON","population":43021,"percentFullyImmunized":56.8},{"localName":"THORSBY","population":9090,"percentFullyImmunized":48.6},{"localName":"STONY PLAIN & SPRUCE GROVE","population":57833,"percentFullyImmunized":58},{"localName":"WESTVIEW EXCLUDING STONY PLAIN & SPRUCE GROVE","population":36730,"percentFullyImmunized":51.6},{"localName":"ST. ALBERT","population":69588,"percentFullyImmunized":70.5},{"localName":"JASPER","population":5592,"percentFullyImmunized":68},{"localName":"HINTON","population":12260,"percentFullyImmunized":53.3},{"localName":"EDSON","population":16050,"percentFullyImmunized":47.5},{"localName":"WHITECOURT","population":14719,"percentFullyImmunized":44.7},{"localName":"MAYERTHORPE","population":16200,"percentFullyImmunized":48.8},{"localName":"BARRHEAD","population":10948,"percentFullyImmunized":47.9},{"localName":"WESTLOCK","population":19168,"percentFullyImmunized":53.8},{"localName":"FROG LAKE","population":4827,"percentFullyImmunized":34.8},{"localName":"ST. PAUL","population":15522,"percentFullyImmunized":39.2},{"localName":"SMOKY LAKE","population":4728,"percentFullyImmunized":51.3},{"localName":"COLD LAKE","population":20716,"percentFullyImmunized":46.4},{"localName":"BONNYVILLE","population":16602,"percentFullyImmunized":42.2},{"localName":"BOYLE","population":3544,"percentFullyImmunized":44.4},{"localName":"ATHABASCA","population":10686,"percentFullyImmunized":55.1},{"localName":"LAC LA BICHE","population":10392,"percentFullyImmunized":43.6},{"localName":"GRANDE CACHE","population":4168,"percentFullyImmunized":44.8},{"localName":"FOX CREEK","population":2241,"percentFullyImmunized":45.7},{"localName":"VALLEYVIEW","population":7226,"percentFullyImmunized":39.6},{"localName":"BEAVERLODGE","population":12199,"percentFullyImmunized":40.5},{"localName":"GRANDE PRAIRIE COUNTY","population":20862,"percentFullyImmunized":42.6},{"localName":"SWAN HILLS","population":1336,"percentFullyImmunized":45.4},{"localName":"SLAVE LAKE","population":11676,"percentFullyImmunized":41.9},{"localName":"WABASCA","population":4238,"percentFullyImmunized":34.2},{"localName":"HIGH PRAIRIE","population":11613,"percentFullyImmunized":33.8},{"localName":"HIGH LEVEL","population":25086,"percentFullyImmunized":14.1},{"localName":"MANNING","population":3290,"percentFullyImmunized":40.2},{"localName":"PEACE RIVER","population":18611,"percentFullyImmunized":42.5},{"localName":"FALHER","population":4427,"percentFullyImmunized":48.1},{"localName":"SPIRIT RIVER","population":6114,"percentFullyImmunized":40.7},{"localName":"FAIRVIEW","population":8131,"percentFullyImmunized":39.9},{"localName":"WOOD BUFFALO","population":4062,"percentFullyImmunized":34.5},{"localName":"FORT MCMURRAY","population":79416,"percentFullyImmunized":50},{"localName":"CITY OF GRANDE PRAIRIE","population":74275,"percentFullyImmunized":43.3}]

 const orderedData = condensedData.sort((a, b) => a.percentFullyImmunized - b.percentFullyImmunized)

 function generateColourInRedGreenIntervalByProportion(prop) {
 	return `rgb(255, ${255 * prop}, 0)`;
 }

 function setup() {
 	const ctx = document.getElementById('graph').getContext('2d')
 	const options = {
-		type: 'bar',
+		type: 'scatter',
 		data: {
-			labels: orderedData.map(item => item.localName),
 			datasets: [
 				{
-					label: 'Percent Fully Immunized',
-					data: orderedData.map(item => item.percentFullyImmunized),
+					label: 'Health Regions',
+					data: orderedData.map(item => ({x: item.population,  y: item.percentFullyImmunized } )),
 					backgroundColor: orderedData.map(item => generateColourInRedGreenIntervalByProportion(item.percentFullyImmunized / 100))
 				}
 			]
 		},
 		options: {
+			scales: {
+				x: {
+					type: 'linear',
+					title: {
+						display: true,
+						text: 'Population',
+					}
+				},
+				y: {
+					type: 'linear',
+					title: {
+						display: true,
+						text: 'Percentage Fully Vaccinated',
+					}
+				}
+			},
 			plugins: {
 				title: {
 					display: true,
 					text: 'Percent Vaccination for Alberta Regions',
 				},
 			},
 		},
 	};
 	const chart = new Chart(ctx, options)
 }

 window.onload = setup
```

And again, a beautiful chart is the result:

![Scatter plot of healh regions by population against vaccination percentage](/src/content/blog/2021-10-04-chart-js/resources/chart-3.png)

Notice that the format for the data has changed - instead of just being a list of values (to match against the labels, as with the bar graph), we create a new object with its own $x$ and $y$ coordinates representing each point. This is the only data format which the scatter plot accepts.

Again, while this is lovely, there is one problem that we'd like to solve: when you hover over a point, it just displays the coordinates! Ideally, we'd like to display the name of the region instead.

![Pictured: a label which is not very helpful](/src/content/blog/2021-10-04-chart-js/resources/tooltip-bad.png)

In order to control the displayed tooltip, we need to provide a callback function which will generate the label for each point. Unfortunately, at the moment the points don't have any information about which health region they come from - we'll have to add that into the data!

```diff
 // script.js
 const condensedData =
 [{"localName":"CROWSNEST PASS","population":6280,"percentFullyImmunized":58.1},{"localName":"PINCHER CREEK","population":8344,"percentFullyImmunized":57.7},{"localName":"FORT MACLEOD","population":6753,"percentFullyImmunized":44.3},{"localName":"CARDSTON-KAINAI","population":16595,"percentFullyImmunized":48.6},{"localName":"COUNTY OF LETHBRIDGE","population":25820,"percentFullyImmunized":44},{"localName":"TABER MD","population":19028,"percentFullyImmunized":34.9},{"localName":"COUNTY OF WARNER","population":11104,"percentFullyImmunized":42.9},{"localName":"COUNTY OF FORTY MILE","population":6409,"percentFullyImmunized":28.3},{"localName":"NEWELL","population":27753,"percentFullyImmunized":46.9},{"localName":"OYEN","population":3486,"percentFullyImmunized":45.9},{"localName":"CYPRESS COUNTY","population":11298,"percentFullyImmunized":48.6},{"localName":"MEDICINE HAT","population":68115,"percentFullyImmunized":57.4},{"localName":"LETHBRIDGE - WEST","population":38163,"percentFullyImmunized":65.7},{"localName":"LETHBRIDGE - NORTH","population":27903,"percentFullyImmunized":61.8},{"localName":"LETHBRIDGE - SOUTH","population":34464,"percentFullyImmunized":65.3},{"localName":"CALGARY - UPPER NW","population":123679,"percentFullyImmunized":69.4},{"localName":"CALGARY - NORTH","population":116945,"percentFullyImmunized":67.6},{"localName":"CALGARY - NOSE HILL","population":78021,"percentFullyImmunized":65.8},{"localName":"CALGARY - LOWER NW","population":62696,"percentFullyImmunized":71.2},{"localName":"CALGARY - WEST BOW","population":21283,"percentFullyImmunized":65.7},{"localName":"CALGARY - CENTRE NORTH","population":44910,"percentFullyImmunized":68.7},{"localName":"CALGARY - UPPER NE","population":120999,"percentFullyImmunized":63.9},{"localName":"CALGARY - LOWER NE","population":96472,"percentFullyImmunized":58.3},{"localName":"CALGARY - EAST","population":72509,"percentFullyImmunized":56.7},{"localName":"CALGARY - SE","population":134420,"percentFullyImmunized":64},{"localName":"CALGARY - WEST","population":92320,"percentFullyImmunized":69.3},{"localName":"CALGARY - CENTRE","population":67568,"percentFullyImmunized":66.5},{"localName":"CALGARY - CENTRE WEST","population":65845,"percentFullyImmunized":67.7},{"localName":"CALGARY - ELBOW","population":40834,"percentFullyImmunized":69.8},{"localName":"CALGARY - FISH CREEK","population":111574,"percentFullyImmunized":66.5},{"localName":"CALGARY - SW","population":116934,"percentFullyImmunized":66.5},{"localName":"OKOTOKS-PRIDDIS","population":46042,"percentFullyImmunized":60},{"localName":"BLACK DIAMOND","population":8769,"percentFullyImmunized":52.9},{"localName":"HIGH RIVER","population":23739,"percentFullyImmunized":56.1},{"localName":"CLARESHOLM","population":6246,"percentFullyImmunized":56.9},{"localName":"VULCAN","population":6775,"percentFullyImmunized":47},{"localName":"AIRDRIE","population":73698,"percentFullyImmunized":56.8},{"localName":"CHESTERMERE","population":25015,"percentFullyImmunized":63},{"localName":"STRATHMORE","population":35685,"percentFullyImmunized":54.8},{"localName":"CROSSFIELD","population":9164,"percentFullyImmunized":50.4},{"localName":"DIDSBURY","population":16475,"percentFullyImmunized":50.3},{"localName":"COCHRANE-SPRINGBANK","population":50816,"percentFullyImmunized":63.2},{"localName":"CANMORE","population":27674,"percentFullyImmunized":64.3},{"localName":"BANFF","population":13451,"percentFullyImmunized":57.7},{"localName":"ROCKY MOUNTAIN HOUSE","population":20389,"percentFullyImmunized":43.3},{"localName":"DRAYTON VALLEY","population":18075,"percentFullyImmunized":40.6},{"localName":"SUNDRE","population":6782,"percentFullyImmunized":47.6},{"localName":"OLDS","population":12597,"percentFullyImmunized":54.9},{"localName":"INNISFAIL","population":15939,"percentFullyImmunized":57.1},{"localName":"RED DEER COUNTY","population":29495,"percentFullyImmunized":43.6},{"localName":"SYLVAN LAKE","population":18013,"percentFullyImmunized":42.9},{"localName":"THREE HILLS/HIGHWAY 21","population":10816,"percentFullyImmunized":45.5},{"localName":"STARLAND COUNTY/DRUMHELLER","population":11802,"percentFullyImmunized":55.8},{"localName":"PLANNING & SPECIAL AREA 2","population":3648,"percentFullyImmunized":48},{"localName":"STETTLER & COUNTY","population":12520,"percentFullyImmunized":45.8},{"localName":"CASTOR/CORONATION/CONSORT","population":6160,"percentFullyImmunized":44.3},{"localName":"WETASKIWIN COUNTY","population":33715,"percentFullyImmunized":46.8},{"localName":"PONOKA","population":12399,"percentFullyImmunized":47.5},{"localName":"RIMBEY","population":10013,"percentFullyImmunized":44.3},{"localName":"LACOMBE","population":23417,"percentFullyImmunized":48.1},{"localName":"CAMROSE & COUNTY","population":30125,"percentFullyImmunized":57.8},{"localName":"TOFIELD","population":7797,"percentFullyImmunized":51.5},{"localName":"VIKING","population":2351,"percentFullyImmunized":55.5},{"localName":"FLAGSTAFF COUNTY","population":8426,"percentFullyImmunized":55.7},{"localName":"MD OF PROVOST","population":4860,"percentFullyImmunized":50.1},{"localName":"MD OF WAINWRIGHT","population":11915,"percentFullyImmunized":54},{"localName":"LAMONT COUNTY","population":6388,"percentFullyImmunized":52.6},{"localName":"TWO HILLS COUNTY","population":5579,"percentFullyImmunized":30.5},{"localName":"VEGREVILLE/MINBURN COUNTY","population":10323,"percentFullyImmunized":56.5},{"localName":"VERMILION RIVER COUNTY","population":36740,"percentFullyImmunized":27.9},{"localName":"RED DEER - NORTH","population":35640,"percentFullyImmunized":50},{"localName":"RED DEER - SW","population":15679,"percentFullyImmunized":51.1},{"localName":"RED DEER - EAST","population":55069,"percentFullyImmunized":57.3},{"localName":"EDMONTON - WOODCROFT EAST","population":60664,"percentFullyImmunized":59.9},{"localName":"EDMONTON - WOODCROFT WEST","population":33002,"percentFullyImmunized":63.2},{"localName":"EDMONTON - JASPER PLACE","population":46923,"percentFullyImmunized":59.6},{"localName":"EDMONTON - WEST JASPER PLACE","population":103462,"percentFullyImmunized":69.4},{"localName":"EDMONTON - CASTLE DOWNS","population":71594,"percentFullyImmunized":60.5},{"localName":"EDMONTON - NORTHGATE","population":82969,"percentFullyImmunized":59.1},{"localName":"EDMONTON - EASTWOOD","population":72156,"percentFullyImmunized":55.4},{"localName":"EDMONTON - ABBOTTSFIELD","population":14582,"percentFullyImmunized":50.5},{"localName":"EDMONTON - NE","population":90743,"percentFullyImmunized":57.6},{"localName":"EDMONTON - BONNIE DOON","population":96621,"percentFullyImmunized":67.6},{"localName":"EDMONTON - MILL WOODS WEST","population":51150,"percentFullyImmunized":62},{"localName":"EDMONTON - MILL WOODS SOUTH & EAST","population":85232,"percentFullyImmunized":65.1},{"localName":"EDMONTON - DUGGAN","population":40132,"percentFullyImmunized":66.6},{"localName":"EDMONTON - TWIN BROOKS","population":75969,"percentFullyImmunized":72.3},{"localName":"EDMONTON - RUTHERFORD","population":112265,"percentFullyImmunized":66.5},{"localName":"STURGEON COUNTY WEST","population":30154,"percentFullyImmunized":55.1},{"localName":"STURGEON COUNTY EAST","population":6095,"percentFullyImmunized":55.2},{"localName":"FORT SASKATCHEWAN","population":26795,"percentFullyImmunized":58.8},{"localName":"SHERWOOD PARK","population":82033,"percentFullyImmunized":70.1},{"localName":"STRATHCONA COUNTY EXCLUDING SHERWOOD PARK","population":17420,"percentFullyImmunized":63.1},{"localName":"BEAUMONT","population":25785,"percentFullyImmunized":59.6},{"localName":"LEDUC & DEVON","population":43021,"percentFullyImmunized":56.8},{"localName":"THORSBY","population":9090,"percentFullyImmunized":48.6},{"localName":"STONY PLAIN & SPRUCE GROVE","population":57833,"percentFullyImmunized":58},{"localName":"WESTVIEW EXCLUDING STONY PLAIN & SPRUCE GROVE","population":36730,"percentFullyImmunized":51.6},{"localName":"ST. ALBERT","population":69588,"percentFullyImmunized":70.5},{"localName":"JASPER","population":5592,"percentFullyImmunized":68},{"localName":"HINTON","population":12260,"percentFullyImmunized":53.3},{"localName":"EDSON","population":16050,"percentFullyImmunized":47.5},{"localName":"WHITECOURT","population":14719,"percentFullyImmunized":44.7},{"localName":"MAYERTHORPE","population":16200,"percentFullyImmunized":48.8},{"localName":"BARRHEAD","population":10948,"percentFullyImmunized":47.9},{"localName":"WESTLOCK","population":19168,"percentFullyImmunized":53.8},{"localName":"FROG LAKE","population":4827,"percentFullyImmunized":34.8},{"localName":"ST. PAUL","population":15522,"percentFullyImmunized":39.2},{"localName":"SMOKY LAKE","population":4728,"percentFullyImmunized":51.3},{"localName":"COLD LAKE","population":20716,"percentFullyImmunized":46.4},{"localName":"BONNYVILLE","population":16602,"percentFullyImmunized":42.2},{"localName":"BOYLE","population":3544,"percentFullyImmunized":44.4},{"localName":"ATHABASCA","population":10686,"percentFullyImmunized":55.1},{"localName":"LAC LA BICHE","population":10392,"percentFullyImmunized":43.6},{"localName":"GRANDE CACHE","population":4168,"percentFullyImmunized":44.8},{"localName":"FOX CREEK","population":2241,"percentFullyImmunized":45.7},{"localName":"VALLEYVIEW","population":7226,"percentFullyImmunized":39.6},{"localName":"BEAVERLODGE","population":12199,"percentFullyImmunized":40.5},{"localName":"GRANDE PRAIRIE COUNTY","population":20862,"percentFullyImmunized":42.6},{"localName":"SWAN HILLS","population":1336,"percentFullyImmunized":45.4},{"localName":"SLAVE LAKE","population":11676,"percentFullyImmunized":41.9},{"localName":"WABASCA","population":4238,"percentFullyImmunized":34.2},{"localName":"HIGH PRAIRIE","population":11613,"percentFullyImmunized":33.8},{"localName":"HIGH LEVEL","population":25086,"percentFullyImmunized":14.1},{"localName":"MANNING","population":3290,"percentFullyImmunized":40.2},{"localName":"PEACE RIVER","population":18611,"percentFullyImmunized":42.5},{"localName":"FALHER","population":4427,"percentFullyImmunized":48.1},{"localName":"SPIRIT RIVER","population":6114,"percentFullyImmunized":40.7},{"localName":"FAIRVIEW","population":8131,"percentFullyImmunized":39.9},{"localName":"WOOD BUFFALO","population":4062,"percentFullyImmunized":34.5},{"localName":"FORT MCMURRAY","population":79416,"percentFullyImmunized":50},{"localName":"CITY OF GRANDE PRAIRIE","population":74275,"percentFullyImmunized":43.3}]

 const orderedData = condensedData.sort((a, b) => a.percentFullyImmunized - b.percentFullyImmunized)

 function generateColourInRedGreenIntervalByProportion(prop) {
 	return `rgb(255, ${255 * prop}, 0)`;
 }

 function setup() {
 	const ctx = document.getElementById('graph').getContext('2d')
 	const options = {
 		type: 'scatter',
 		data: {
 			datasets: [
 				{
 					label: 'Health Regions',
-					data: orderedData.map(item => ({x: item.population,  y: item.percentFullyImmunized } )),
+					data: orderedData.map(item => ({x: item.population,  y: item.percentFullyImmunized, label: item.localName } )),
 					backgroundColor: orderedData.map(item => generateColourInRedGreenIntervalByProportion(item.percentFullyImmunized / 100))
 				}
 			]
 		},
 		options: {
 			scales: {
 				x: {
 					type: 'linear',
 					title: {
 						display: true,
 						text: 'Population',
 					}
 				},
 				y: {
 					type: 'linear',
 					title: {
 						display: true,
 						text: 'Percentage Fully Vaccinated',
 					}
 				}
 			},
 			plugins: {
 				title: {
 					display: true,
 					text: 'Percent Vaccination for Alberta Regions',
 				},
+				tooltip: {
+					callbacks: {
+						label: (context) => context.raw.label ? context.raw.label : '',
+					}
+				}
 			},
 		},
 	};
 	const chart = new Chart(ctx, options)
 }

 window.onload = setup
```

Now when we hover over a point, we get a much more informative tooltip.

![A tooltip which indicates the health region](/src/content/blog/2021-10-04-chart-js/resources/tooltip-good.png)

The callback function which we provided was provided a context object, which contains a wealth of information about the individual point and the graph itself. Included in that is the `raw` attribute, which is the data point itself. We amended our passed-in data with the `label` attribute, which is actually ignored by Chart.js. However, we were then able to grab that value in the callback and use it as the value of the labe displayed in the tooltip. As with everything else in Chart.js, there is a lot more that you could do with tooltips, and the [documentation is an excellent place to start](https://www.chartjs.org/docs/3.4.0/configuration/tooltip.html).

## Updating

(To start right from here, begin from [this commit](https://github.com/EricRobertCampbell/learning-chart-js/commit/9085079da5d65b08df159c70637dba7ce0490c6c))

Looking at this chart, it seems pretty clear that there is a connection of some sort between the population size and the vaccination percentage - it really looks like the larger the population, the higher the percentage. If we were interested in that, we could perhaps find a line of best fit and look at the slope. However, for now we're going to do something a bit different. We'll take the position that perhaps there is no (real) relationship between the population and the vaccination rate - perhaps what we're seeing is just an expression of the fact that in a smaller population, we would expect to see more variability. After all, it wouldn't shock you to flip a coin twice and get all heads, but it would certainly suprise you to flip that same coin 100 times and get the same result!

In order to explore that possibility, here's what we'll do. First, we'll calculate the average percent of the population that is vaccinated, and display that as a line on our graph. Next, we're going to pretend that getting vaccinated is a [Bernoulli process](https://en.wikipedia.org/wiki/Bernoulli_process) with $p$ being the average vaccination rate, and we'll construct a 95% confidence interval around the mean. To do so, we'll use a [Monte Carlo simulation](https://www.ibm.com/cloud/learn/monte-carlo-simulation) to generate the interval empirically.

```diff
 // script.js
 const condensedData =
 [{"localName":"CROWSNEST PASS","population":6280,"percentFullyImmunized":58.1},{"localName":"PINCHER CREEK","population":8344,"percentFullyImmunized":57.7},{"localName":"FORT MACLEOD","population":6753,"percentFullyImmunized":44.3},{"localName":"CARDSTON-KAINAI","population":16595,"percentFullyImmunized":48.6},{"localName":"COUNTY OF LETHBRIDGE","population":25820,"percentFullyImmunized":44},{"localName":"TABER MD","population":19028,"percentFullyImmunized":34.9},{"localName":"COUNTY OF WARNER","population":11104,"percentFullyImmunized":42.9},{"localName":"COUNTY OF FORTY MILE","population":6409,"percentFullyImmunized":28.3},{"localName":"NEWELL","population":27753,"percentFullyImmunized":46.9},{"localName":"OYEN","population":3486,"percentFullyImmunized":45.9},{"localName":"CYPRESS COUNTY","population":11298,"percentFullyImmunized":48.6},{"localName":"MEDICINE HAT","population":68115,"percentFullyImmunized":57.4},{"localName":"LETHBRIDGE - WEST","population":38163,"percentFullyImmunized":65.7},{"localName":"LETHBRIDGE - NORTH","population":27903,"percentFullyImmunized":61.8},{"localName":"LETHBRIDGE - SOUTH","population":34464,"percentFullyImmunized":65.3},{"localName":"CALGARY - UPPER NW","population":123679,"percentFullyImmunized":69.4},{"localName":"CALGARY - NORTH","population":116945,"percentFullyImmunized":67.6},{"localName":"CALGARY - NOSE HILL","population":78021,"percentFullyImmunized":65.8},{"localName":"CALGARY - LOWER NW","population":62696,"percentFullyImmunized":71.2},{"localName":"CALGARY - WEST BOW","population":21283,"percentFullyImmunized":65.7},{"localName":"CALGARY - CENTRE NORTH","population":44910,"percentFullyImmunized":68.7},{"localName":"CALGARY - UPPER NE","population":120999,"percentFullyImmunized":63.9},{"localName":"CALGARY - LOWER NE","population":96472,"percentFullyImmunized":58.3},{"localName":"CALGARY - EAST","population":72509,"percentFullyImmunized":56.7},{"localName":"CALGARY - SE","population":134420,"percentFullyImmunized":64},{"localName":"CALGARY - WEST","population":92320,"percentFullyImmunized":69.3},{"localName":"CALGARY - CENTRE","population":67568,"percentFullyImmunized":66.5},{"localName":"CALGARY - CENTRE WEST","population":65845,"percentFullyImmunized":67.7},{"localName":"CALGARY - ELBOW","population":40834,"percentFullyImmunized":69.8},{"localName":"CALGARY - FISH CREEK","population":111574,"percentFullyImmunized":66.5},{"localName":"CALGARY - SW","population":116934,"percentFullyImmunized":66.5},{"localName":"OKOTOKS-PRIDDIS","population":46042,"percentFullyImmunized":60},{"localName":"BLACK DIAMOND","population":8769,"percentFullyImmunized":52.9},{"localName":"HIGH RIVER","population":23739,"percentFullyImmunized":56.1},{"localName":"CLARESHOLM","population":6246,"percentFullyImmunized":56.9},{"localName":"VULCAN","population":6775,"percentFullyImmunized":47},{"localName":"AIRDRIE","population":73698,"percentFullyImmunized":56.8},{"localName":"CHESTERMERE","population":25015,"percentFullyImmunized":63},{"localName":"STRATHMORE","population":35685,"percentFullyImmunized":54.8},{"localName":"CROSSFIELD","population":9164,"percentFullyImmunized":50.4},{"localName":"DIDSBURY","population":16475,"percentFullyImmunized":50.3},{"localName":"COCHRANE-SPRINGBANK","population":50816,"percentFullyImmunized":63.2},{"localName":"CANMORE","population":27674,"percentFullyImmunized":64.3},{"localName":"BANFF","population":13451,"percentFullyImmunized":57.7},{"localName":"ROCKY MOUNTAIN HOUSE","population":20389,"percentFullyImmunized":43.3},{"localName":"DRAYTON VALLEY","population":18075,"percentFullyImmunized":40.6},{"localName":"SUNDRE","population":6782,"percentFullyImmunized":47.6},{"localName":"OLDS","population":12597,"percentFullyImmunized":54.9},{"localName":"INNISFAIL","population":15939,"percentFullyImmunized":57.1},{"localName":"RED DEER COUNTY","population":29495,"percentFullyImmunized":43.6},{"localName":"SYLVAN LAKE","population":18013,"percentFullyImmunized":42.9},{"localName":"THREE HILLS/HIGHWAY 21","population":10816,"percentFullyImmunized":45.5},{"localName":"STARLAND COUNTY/DRUMHELLER","population":11802,"percentFullyImmunized":55.8},{"localName":"PLANNING & SPECIAL AREA 2","population":3648,"percentFullyImmunized":48},{"localName":"STETTLER & COUNTY","population":12520,"percentFullyImmunized":45.8},{"localName":"CASTOR/CORONATION/CONSORT","population":6160,"percentFullyImmunized":44.3},{"localName":"WETASKIWIN COUNTY","population":33715,"percentFullyImmunized":46.8},{"localName":"PONOKA","population":12399,"percentFullyImmunized":47.5},{"localName":"RIMBEY","population":10013,"percentFullyImmunized":44.3},{"localName":"LACOMBE","population":23417,"percentFullyImmunized":48.1},{"localName":"CAMROSE & COUNTY","population":30125,"percentFullyImmunized":57.8},{"localName":"TOFIELD","population":7797,"percentFullyImmunized":51.5},{"localName":"VIKING","population":2351,"percentFullyImmunized":55.5},{"localName":"FLAGSTAFF COUNTY","population":8426,"percentFullyImmunized":55.7},{"localName":"MD OF PROVOST","population":4860,"percentFullyImmunized":50.1},{"localName":"MD OF WAINWRIGHT","population":11915,"percentFullyImmunized":54},{"localName":"LAMONT COUNTY","population":6388,"percentFullyImmunized":52.6},{"localName":"TWO HILLS COUNTY","population":5579,"percentFullyImmunized":30.5},{"localName":"VEGREVILLE/MINBURN COUNTY","population":10323,"percentFullyImmunized":56.5},{"localName":"VERMILION RIVER COUNTY","population":36740,"percentFullyImmunized":27.9},{"localName":"RED DEER - NORTH","population":35640,"percentFullyImmunized":50},{"localName":"RED DEER - SW","population":15679,"percentFullyImmunized":51.1},{"localName":"RED DEER - EAST","population":55069,"percentFullyImmunized":57.3},{"localName":"EDMONTON - WOODCROFT EAST","population":60664,"percentFullyImmunized":59.9},{"localName":"EDMONTON - WOODCROFT WEST","population":33002,"percentFullyImmunized":63.2},{"localName":"EDMONTON - JASPER PLACE","population":46923,"percentFullyImmunized":59.6},{"localName":"EDMONTON - WEST JASPER PLACE","population":103462,"percentFullyImmunized":69.4},{"localName":"EDMONTON - CASTLE DOWNS","population":71594,"percentFullyImmunized":60.5},{"localName":"EDMONTON - NORTHGATE","population":82969,"percentFullyImmunized":59.1},{"localName":"EDMONTON - EASTWOOD","population":72156,"percentFullyImmunized":55.4},{"localName":"EDMONTON - ABBOTTSFIELD","population":14582,"percentFullyImmunized":50.5},{"localName":"EDMONTON - NE","population":90743,"percentFullyImmunized":57.6},{"localName":"EDMONTON - BONNIE DOON","population":96621,"percentFullyImmunized":67.6},{"localName":"EDMONTON - MILL WOODS WEST","population":51150,"percentFullyImmunized":62},{"localName":"EDMONTON - MILL WOODS SOUTH & EAST","population":85232,"percentFullyImmunized":65.1},{"localName":"EDMONTON - DUGGAN","population":40132,"percentFullyImmunized":66.6},{"localName":"EDMONTON - TWIN BROOKS","population":75969,"percentFullyImmunized":72.3},{"localName":"EDMONTON - RUTHERFORD","population":112265,"percentFullyImmunized":66.5},{"localName":"STURGEON COUNTY WEST","population":30154,"percentFullyImmunized":55.1},{"localName":"STURGEON COUNTY EAST","population":6095,"percentFullyImmunized":55.2},{"localName":"FORT SASKATCHEWAN","population":26795,"percentFullyImmunized":58.8},{"localName":"SHERWOOD PARK","population":82033,"percentFullyImmunized":70.1},{"localName":"STRATHCONA COUNTY EXCLUDING SHERWOOD PARK","population":17420,"percentFullyImmunized":63.1},{"localName":"BEAUMONT","population":25785,"percentFullyImmunized":59.6},{"localName":"LEDUC & DEVON","population":43021,"percentFullyImmunized":56.8},{"localName":"THORSBY","population":9090,"percentFullyImmunized":48.6},{"localName":"STONY PLAIN & SPRUCE GROVE","population":57833,"percentFullyImmunized":58},{"localName":"WESTVIEW EXCLUDING STONY PLAIN & SPRUCE GROVE","population":36730,"percentFullyImmunized":51.6},{"localName":"ST. ALBERT","population":69588,"percentFullyImmunized":70.5},{"localName":"JASPER","population":5592,"percentFullyImmunized":68},{"localName":"HINTON","population":12260,"percentFullyImmunized":53.3},{"localName":"EDSON","population":16050,"percentFullyImmunized":47.5},{"localName":"WHITECOURT","population":14719,"percentFullyImmunized":44.7},{"localName":"MAYERTHORPE","population":16200,"percentFullyImmunized":48.8},{"localName":"BARRHEAD","population":10948,"percentFullyImmunized":47.9},{"localName":"WESTLOCK","population":19168,"percentFullyImmunized":53.8},{"localName":"FROG LAKE","population":4827,"percentFullyImmunized":34.8},{"localName":"ST. PAUL","population":15522,"percentFullyImmunized":39.2},{"localName":"SMOKY LAKE","population":4728,"percentFullyImmunized":51.3},{"localName":"COLD LAKE","population":20716,"percentFullyImmunized":46.4},{"localName":"BONNYVILLE","population":16602,"percentFullyImmunized":42.2},{"localName":"BOYLE","population":3544,"percentFullyImmunized":44.4},{"localName":"ATHABASCA","population":10686,"percentFullyImmunized":55.1},{"localName":"LAC LA BICHE","population":10392,"percentFullyImmunized":43.6},{"localName":"GRANDE CACHE","population":4168,"percentFullyImmunized":44.8},{"localName":"FOX CREEK","population":2241,"percentFullyImmunized":45.7},{"localName":"VALLEYVIEW","population":7226,"percentFullyImmunized":39.6},{"localName":"BEAVERLODGE","population":12199,"percentFullyImmunized":40.5},{"localName":"GRANDE PRAIRIE COUNTY","population":20862,"percentFullyImmunized":42.6},{"localName":"SWAN HILLS","population":1336,"percentFullyImmunized":45.4},{"localName":"SLAVE LAKE","population":11676,"percentFullyImmunized":41.9},{"localName":"WABASCA","population":4238,"percentFullyImmunized":34.2},{"localName":"HIGH PRAIRIE","population":11613,"percentFullyImmunized":33.8},{"localName":"HIGH LEVEL","population":25086,"percentFullyImmunized":14.1},{"localName":"MANNING","population":3290,"percentFullyImmunized":40.2},{"localName":"PEACE RIVER","population":18611,"percentFullyImmunized":42.5},{"localName":"FALHER","population":4427,"percentFullyImmunized":48.1},{"localName":"SPIRIT RIVER","population":6114,"percentFullyImmunized":40.7},{"localName":"FAIRVIEW","population":8131,"percentFullyImmunized":39.9},{"localName":"WOOD BUFFALO","population":4062,"percentFullyImmunized":34.5},{"localName":"FORT MCMURRAY","population":79416,"percentFullyImmunized":50},{"localName":"CITY OF GRANDE PRAIRIE","population":74275,"percentFullyImmunized":43.3}]

 const orderedData = condensedData.sort((a, b) => a.percentFullyImmunized - b.percentFullyImmunized)

+const totalPopulation = condensedData.map(item => item.population).reduce((sum, num) => sum + num, 0)
+const minPop = Math.min(...condensedData.map(item => item.population))
+const maxPop = Math.max(...condensedData.map(item => item.population))
+const averageVaccinationRate = condensedData.reduce(( mean, item ) => mean + item.population / totalPopulation * item.percentFullyImmunized, 0)
+
+/**
+ * Run a simulation of n binomial trials with probability p; return k, the number of successes
+ */
+function binomialRun(n, p) {
+	let k = 0;
+	for (let i = 0; i < n; i++) {
+		if (Math.random() < p) {
+			k++;
+		}
+	}
+	return k;
+}
+
+/**
+ * Find the numbers a and b such that in the provided array, ci% of the values are in the range [a, b]
+ */
+function empiricalConfidenceInterval(arr, ci) {
+	// first ensure that the list is sorted
+	arr = arr.sort((a, b) => a - b);
+	const remainingPercent = (1 - ci) / 2;
+	const distance = Math.floor(arr.length * remainingPercent);
+	const lower = arr[Math.max( distance - 1, 0 )];
+	const upper = arr[Math.min( arr.length - distance - 1, arr.length - 1 )];
+	return [lower, upper];
+}
+
+/**
+ * Run a Monte Carlo simulation of n binomial trials with probability p; run numTrial trials
+ */
+function runMonteCarloTrial(numTrials, n, p) {
+	return Array(numTrials)
+		.fill(0)
+		.map((_) => binomialRun(n, p));
+}
+
+function generateConfidencePlotData(ci, average) {
+	let ns = [
+		10,
+		100,
+		500,
+		1000,
+		2000,
+		3000,
+		4000,
+		5000,
+		6000,
+		7000,
+		8000,
+		9000,
+		10000,
+		120000,
+		134400,
+	];
+
+	const lowerData = [];
+	const upperData = [];
+
+	ns.forEach((n) => {
+		const [lowerNumber, upperNumber] = empiricalConfidenceInterval(
+			runMonteCarloTrial(1000, n, average / 100),
+			ci
+		);
+		lowerData.push({ x: n, y: (lowerNumber / n) * 100 });
+		upperData.push({ x: n, y: (upperNumber / n) * 100 });
+	});
+	return [lowerData, upperData]
+}
+
 function generateColourInRedGreenIntervalByProportion(prop) {
 	return `rgb(255, ${255 * prop}, 0)`;
 }

 function setup() {
 	const ctx = document.getElementById('graph').getContext('2d')
+
+	const [upperData, lowerData] = generateConfidencePlotData(0.95, averageVaccinationRate)
+
 	const options = {
-		type: 'scatter',
 		data: {
 			datasets: [
 				{
+					type: 'scatter',
 					label: 'Health Regions',
 					data: orderedData.map(item => ({x: item.population,  y: item.percentFullyImmunized, label: item.localName } )),
 					backgroundColor: orderedData.map(item => generateColourInRedGreenIntervalByProportion(item.percentFullyImmunized / 100))
-				}
+				},
+				{
+					type: 'line',
+					label: 'Average Vaccination Rate',
+					data: [{x: minPop, y: averageVaccinationRate}, {x: maxPop, y: averageVaccinationRate}],
+					borderColor: 'blue',
+					pointRadius: 0,
+				},
+				{
+					type: 'line',
+					label: 'Lower 95% Confidence',
+					data: lowerData,
+					borderColor: 'black',
+					pointRadius: 0,
+				},
+				{
+					type: 'line',
+					label: 'Upper 95% Confidence',
+					data: upperData,
+					borderColor: 'black',
+					pointRadius: 0,
+				},
 			]
 		},
 		options: {
 			scales: {
 				x: {
 					type: 'linear',
 					title: {
 						display: true,
 						text: 'Population',
 					}
 				},
 				y: {
 					type: 'linear',
 					title: {
 						display: true,
 						text: 'Percentage Fully Vaccinated',
 					}
 				}
 			},
 			plugins: {
 				title: {
 					display: true,
 					text: 'Percent Vaccination for Alberta Regions',
 				},
 				tooltip: {
 					callbacks: {
 						label: (context) => context.raw.label ? context.raw.label : '',
 					}
 				}
 			},
 		},
 	};
 	const chart = new Chart(ctx, options)
 }

 window.onload = setup
```

Which gives us the following chart:

![Chart with confidence intervals](/src/content/blog/2021-10-04-chart-js/resources/chart-4.png)

If our assumptions were correct, we would expect 95% of the data to fit within the two black bands. Instead, almost none of it does! This lends some credence to our original idea that population size and vaccination rate are related, but of course there would be much more work to do to establish that.

Before we decide that we're done with this whole enterprise, there's one more thing that we should do. Our choice of a 95% confidence interval on which to base our analysis was fairly arbitrary - what if we were interested in different intervals? Let's add in the ability for the user to select a variety of intervals, and have the graph change when a new one is selected.

```diff
 <!-- index.html -->
 <!doctype html>
 <html>
 	<head>
 		<meta charset="utf-8">
 		<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/chart.js@3.5.1/dist/chart.min.js"></script>
 		<script type="text/javascript" src="./scripts/script.js"></script>
 		<link href="./styling/style.css" rel="stylesheet" />
 	</head>
 	<body>
 		<h1>An Introduction to Chart.js</h1>
+		<label>
+			Select the confidence interval:&nbsp;
+			<select name="confidence-interval" id="confidence-interval-select" >
+				<option value="" selected>(None)</option>
+				<option value="0.5">50%</option>
+				<option value="0.75">75%</option>
+				<option value="0.9">90%</option>
+				<option value="0.95">95%</option>
+				<option value="0.99">99%</option>
+				<option value="0.999">99.9%</option>
+			</select>
+		</label>
 		<canvas id="graph"></canvas>
 	</body>
 </html>
```

```diff
// script.js
const condensedData =
[{"localName":"CROWSNEST PASS","population":6280,"percentFullyImmunized":58.1},{"localName":"PINCHER CREEK","population":8344,"percentFullyImmunized":57.7},{"localName":"FORT MACLEOD","population":6753,"percentFullyImmunized":44.3},{"localName":"CARDSTON-KAINAI","population":16595,"percentFullyImmunized":48.6},{"localName":"COUNTY OF LETHBRIDGE","population":25820,"percentFullyImmunized":44},{"localName":"TABER MD","population":19028,"percentFullyImmunized":34.9},{"localName":"COUNTY OF WARNER","population":11104,"percentFullyImmunized":42.9},{"localName":"COUNTY OF FORTY MILE","population":6409,"percentFullyImmunized":28.3},{"localName":"NEWELL","population":27753,"percentFullyImmunized":46.9},{"localName":"OYEN","population":3486,"percentFullyImmunized":45.9},{"localName":"CYPRESS COUNTY","population":11298,"percentFullyImmunized":48.6},{"localName":"MEDICINE HAT","population":68115,"percentFullyImmunized":57.4},{"localName":"LETHBRIDGE - WEST","population":38163,"percentFullyImmunized":65.7},{"localName":"LETHBRIDGE - NORTH","population":27903,"percentFullyImmunized":61.8},{"localName":"LETHBRIDGE - SOUTH","population":34464,"percentFullyImmunized":65.3},{"localName":"CALGARY - UPPER NW","population":123679,"percentFullyImmunized":69.4},{"localName":"CALGARY - NORTH","population":116945,"percentFullyImmunized":67.6},{"localName":"CALGARY - NOSE HILL","population":78021,"percentFullyImmunized":65.8},{"localName":"CALGARY - LOWER NW","population":62696,"percentFullyImmunized":71.2},{"localName":"CALGARY - WEST BOW","population":21283,"percentFullyImmunized":65.7},{"localName":"CALGARY - CENTRE NORTH","population":44910,"percentFullyImmunized":68.7},{"localName":"CALGARY - UPPER NE","population":120999,"percentFullyImmunized":63.9},{"localName":"CALGARY - LOWER NE","population":96472,"percentFullyImmunized":58.3},{"localName":"CALGARY - EAST","population":72509,"percentFullyImmunized":56.7},{"localName":"CALGARY - SE","population":134420,"percentFullyImmunized":64},{"localName":"CALGARY - WEST","population":92320,"percentFullyImmunized":69.3},{"localName":"CALGARY - CENTRE","population":67568,"percentFullyImmunized":66.5},{"localName":"CALGARY - CENTRE WEST","population":65845,"percentFullyImmunized":67.7},{"localName":"CALGARY - ELBOW","population":40834,"percentFullyImmunized":69.8},{"localName":"CALGARY - FISH CREEK","population":111574,"percentFullyImmunized":66.5},{"localName":"CALGARY - SW","population":116934,"percentFullyImmunized":66.5},{"localName":"OKOTOKS-PRIDDIS","population":46042,"percentFullyImmunized":60},{"localName":"BLACK DIAMOND","population":8769,"percentFullyImmunized":52.9},{"localName":"HIGH RIVER","population":23739,"percentFullyImmunized":56.1},{"localName":"CLARESHOLM","population":6246,"percentFullyImmunized":56.9},{"localName":"VULCAN","population":6775,"percentFullyImmunized":47},{"localName":"AIRDRIE","population":73698,"percentFullyImmunized":56.8},{"localName":"CHESTERMERE","population":25015,"percentFullyImmunized":63},{"localName":"STRATHMORE","population":35685,"percentFullyImmunized":54.8},{"localName":"CROSSFIELD","population":9164,"percentFullyImmunized":50.4},{"localName":"DIDSBURY","population":16475,"percentFullyImmunized":50.3},{"localName":"COCHRANE-SPRINGBANK","population":50816,"percentFullyImmunized":63.2},{"localName":"CANMORE","population":27674,"percentFullyImmunized":64.3},{"localName":"BANFF","population":13451,"percentFullyImmunized":57.7},{"localName":"ROCKY MOUNTAIN HOUSE","population":20389,"percentFullyImmunized":43.3},{"localName":"DRAYTON VALLEY","population":18075,"percentFullyImmunized":40.6},{"localName":"SUNDRE","population":6782,"percentFullyImmunized":47.6},{"localName":"OLDS","population":12597,"percentFullyImmunized":54.9},{"localName":"INNISFAIL","population":15939,"percentFullyImmunized":57.1},{"localName":"RED DEER COUNTY","population":29495,"percentFullyImmunized":43.6},{"localName":"SYLVAN LAKE","population":18013,"percentFullyImmunized":42.9},{"localName":"THREE HILLS/HIGHWAY 21","population":10816,"percentFullyImmunized":45.5},{"localName":"STARLAND COUNTY/DRUMHELLER","population":11802,"percentFullyImmunized":55.8},{"localName":"PLANNING & SPECIAL AREA 2","population":3648,"percentFullyImmunized":48},{"localName":"STETTLER & COUNTY","population":12520,"percentFullyImmunized":45.8},{"localName":"CASTOR/CORONATION/CONSORT","population":6160,"percentFullyImmunized":44.3},{"localName":"WETASKIWIN COUNTY","population":33715,"percentFullyImmunized":46.8},{"localName":"PONOKA","population":12399,"percentFullyImmunized":47.5},{"localName":"RIMBEY","population":10013,"percentFullyImmunized":44.3},{"localName":"LACOMBE","population":23417,"percentFullyImmunized":48.1},{"localName":"CAMROSE & COUNTY","population":30125,"percentFullyImmunized":57.8},{"localName":"TOFIELD","population":7797,"percentFullyImmunized":51.5},{"localName":"VIKING","population":2351,"percentFullyImmunized":55.5},{"localName":"FLAGSTAFF COUNTY","population":8426,"percentFullyImmunized":55.7},{"localName":"MD OF PROVOST","population":4860,"percentFullyImmunized":50.1},{"localName":"MD OF WAINWRIGHT","population":11915,"percentFullyImmunized":54},{"localName":"LAMONT COUNTY","population":6388,"percentFullyImmunized":52.6},{"localName":"TWO HILLS COUNTY","population":5579,"percentFullyImmunized":30.5},{"localName":"VEGREVILLE/MINBURN COUNTY","population":10323,"percentFullyImmunized":56.5},{"localName":"VERMILION RIVER COUNTY","population":36740,"percentFullyImmunized":27.9},{"localName":"RED DEER - NORTH","population":35640,"percentFullyImmunized":50},{"localName":"RED DEER - SW","population":15679,"percentFullyImmunized":51.1},{"localName":"RED DEER - EAST","population":55069,"percentFullyImmunized":57.3},{"localName":"EDMONTON - WOODCROFT EAST","population":60664,"percentFullyImmunized":59.9},{"localName":"EDMONTON - WOODCROFT WEST","population":33002,"percentFullyImmunized":63.2},{"localName":"EDMONTON - JASPER PLACE","population":46923,"percentFullyImmunized":59.6},{"localName":"EDMONTON - WEST JASPER PLACE","population":103462,"percentFullyImmunized":69.4},{"localName":"EDMONTON - CASTLE DOWNS","population":71594,"percentFullyImmunized":60.5},{"localName":"EDMONTON - NORTHGATE","population":82969,"percentFullyImmunized":59.1},{"localName":"EDMONTON - EASTWOOD","population":72156,"percentFullyImmunized":55.4},{"localName":"EDMONTON - ABBOTTSFIELD","population":14582,"percentFullyImmunized":50.5},{"localName":"EDMONTON - NE","population":90743,"percentFullyImmunized":57.6},{"localName":"EDMONTON - BONNIE DOON","population":96621,"percentFullyImmunized":67.6},{"localName":"EDMONTON - MILL WOODS WEST","population":51150,"percentFullyImmunized":62},{"localName":"EDMONTON - MILL WOODS SOUTH & EAST","population":85232,"percentFullyImmunized":65.1},{"localName":"EDMONTON - DUGGAN","population":40132,"percentFullyImmunized":66.6},{"localName":"EDMONTON - TWIN BROOKS","population":75969,"percentFullyImmunized":72.3},{"localName":"EDMONTON - RUTHERFORD","population":112265,"percentFullyImmunized":66.5},{"localName":"STURGEON COUNTY WEST","population":30154,"percentFullyImmunized":55.1},{"localName":"STURGEON COUNTY EAST","population":6095,"percentFullyImmunized":55.2},{"localName":"FORT SASKATCHEWAN","population":26795,"percentFullyImmunized":58.8},{"localName":"SHERWOOD PARK","population":82033,"percentFullyImmunized":70.1},{"localName":"STRATHCONA COUNTY EXCLUDING SHERWOOD PARK","population":17420,"percentFullyImmunized":63.1},{"localName":"BEAUMONT","population":25785,"percentFullyImmunized":59.6},{"localName":"LEDUC & DEVON","population":43021,"percentFullyImmunized":56.8},{"localName":"THORSBY","population":9090,"percentFullyImmunized":48.6},{"localName":"STONY PLAIN & SPRUCE GROVE","population":57833,"percentFullyImmunized":58},{"localName":"WESTVIEW EXCLUDING STONY PLAIN & SPRUCE GROVE","population":36730,"percentFullyImmunized":51.6},{"localName":"ST. ALBERT","population":69588,"percentFullyImmunized":70.5},{"localName":"JASPER","population":5592,"percentFullyImmunized":68},{"localName":"HINTON","population":12260,"percentFullyImmunized":53.3},{"localName":"EDSON","population":16050,"percentFullyImmunized":47.5},{"localName":"WHITECOURT","population":14719,"percentFullyImmunized":44.7},{"localName":"MAYERTHORPE","population":16200,"percentFullyImmunized":48.8},{"localName":"BARRHEAD","population":10948,"percentFullyImmunized":47.9},{"localName":"WESTLOCK","population":19168,"percentFullyImmunized":53.8},{"localName":"FROG LAKE","population":4827,"percentFullyImmunized":34.8},{"localName":"ST. PAUL","population":15522,"percentFullyImmunized":39.2},{"localName":"SMOKY LAKE","population":4728,"percentFullyImmunized":51.3},{"localName":"COLD LAKE","population":20716,"percentFullyImmunized":46.4},{"localName":"BONNYVILLE","population":16602,"percentFullyImmunized":42.2},{"localName":"BOYLE","population":3544,"percentFullyImmunized":44.4},{"localName":"ATHABASCA","population":10686,"percentFullyImmunized":55.1},{"localName":"LAC LA BICHE","population":10392,"percentFullyImmunized":43.6},{"localName":"GRANDE CACHE","population":4168,"percentFullyImmunized":44.8},{"localName":"FOX CREEK","population":2241,"percentFullyImmunized":45.7},{"localName":"VALLEYVIEW","population":7226,"percentFullyImmunized":39.6},{"localName":"BEAVERLODGE","population":12199,"percentFullyImmunized":40.5},{"localName":"GRANDE PRAIRIE COUNTY","population":20862,"percentFullyImmunized":42.6},{"localName":"SWAN HILLS","population":1336,"percentFullyImmunized":45.4},{"localName":"SLAVE LAKE","population":11676,"percentFullyImmunized":41.9},{"localName":"WABASCA","population":4238,"percentFullyImmunized":34.2},{"localName":"HIGH PRAIRIE","population":11613,"percentFullyImmunized":33.8},{"localName":"HIGH LEVEL","population":25086,"percentFullyImmunized":14.1},{"localName":"MANNING","population":3290,"percentFullyImmunized":40.2},{"localName":"PEACE RIVER","population":18611,"percentFullyImmunized":42.5},{"localName":"FALHER","population":4427,"percentFullyImmunized":48.1},{"localName":"SPIRIT RIVER","population":6114,"percentFullyImmunized":40.7},{"localName":"FAIRVIEW","population":8131,"percentFullyImmunized":39.9},{"localName":"WOOD BUFFALO","population":4062,"percentFullyImmunized":34.5},{"localName":"FORT MCMURRAY","population":79416,"percentFullyImmunized":50},{"localName":"CITY OF GRANDE PRAIRIE","population":74275,"percentFullyImmunized":43.3}]

const orderedData = condensedData.sort((a, b) => a.percentFullyImmunized - b.percentFullyImmunized)

const totalPopulation = condensedData.map(item => item.population).reduce((sum, num) => sum + num, 0)
const minPop = Math.min(...condensedData.map(item => item.population))
const maxPop = Math.max(...condensedData.map(item => item.population))
const averageVaccinationRate = condensedData.reduce(( mean, item ) => mean + item.population / totalPopulation * item.percentFullyImmunized, 0)

+let chart;
+
/**
 * Run a simulation of n binomial trials with probability p; return k, the number of successes
 */
function binomialRun(n, p) {
	let k = 0;
	for (let i = 0; i < n; i++) {
		if (Math.random() < p) {
			k++;
		}
	}
	return k;
}

/**
 * Find the numbers a and b such that in the provided array, ci% of the values are in the range [a, b]
 */
function empiricalConfidenceInterval(arr, ci) {
	// first ensure that the list is sorted
	arr = arr.sort((a, b) => a - b);
	const remainingPercent = (1 - ci) / 2;
	const distance = Math.floor(arr.length * remainingPercent);
	const lower = arr[Math.max( distance - 1, 0 )];
	const upper = arr[Math.min( arr.length - distance - 1, arr.length - 1 )];
	return [lower, upper];
}

/**
 * Run a Monte Carlo simulation of n binomial trials with probability p; run numTrial trials
 */
function runMonteCarloTrial(numTrials, n, p) {
	return Array(numTrials)
		.fill(0)
		.map((_) => binomialRun(n, p));
}

function generateConfidencePlotData(ci, average) {
	let ns = [
		10,
		100,
		500,
		1000,
		2000,
		3000,
		4000,
		5000,
		6000,
		7000,
		8000,
		9000,
		10000,
		120000,
		134400,
	];

	const lowerData = [];
	const upperData = [];

	ns.forEach((n) => {
		const [lowerNumber, upperNumber] = empiricalConfidenceInterval(
			runMonteCarloTrial(1000, n, average / 100),
			ci
		);
		lowerData.push({ x: n, y: (lowerNumber / n) * 100 });
		upperData.push({ x: n, y: (upperNumber / n) * 100 });
	});
	return [lowerData, upperData]
}

function generateColourInRedGreenIntervalByProportion(prop) {
	return `rgb(255, ${255 * prop}, 0)`;
}

+function updateChart(chart, ci, average) {
+	const [upperData, lowerData] = ci === 0 ? [[], []] : generateConfidencePlotData(ci, average);
+	chart.data.datasets[2].data = lowerData;
+	chart.data.datasets[3].data = upperData;
+	chart.update()
+}
+
+function handleChange(e) {
+	const newCi = Number(e.target.value)
+	updateChart(chart, newCi, averageVaccinationRate)
+}
+
function setup() {
	const ctx = document.getElementById('graph').getContext('2d')

-	const [upperData, lowerData] = generateConfidencePlotData(0.95, averageVaccinationRate)
+	document.getElementById('confidence-interval-select').onchange = handleChange

	const options = {
		data: {
			datasets: [
				{
					type: 'scatter',
					label: 'Health Regions',
					data: orderedData.map(item => ({x: item.population,  y: item.percentFullyImmunized, label: item.localName } )),
					backgroundColor: orderedData.map(item => generateColourInRedGreenIntervalByProportion(item.percentFullyImmunized / 100))
				},
				{
					type: 'line',
					label: 'Average Vaccination Rate',
					data: [{x: minPop, y: averageVaccinationRate}, {x: maxPop, y: averageVaccinationRate}],
					borderColor: 'blue',
					pointRadius: 0,
				},
				{
					type: 'line',
-					label: 'Lower 95% Confidence',
-					data: lowerData,
+					label: 'Lower Confidence',
+					data: [],
					borderColor: 'black',
					pointRadius: 0,
				},
				{
					type: 'line',
-					label: 'Upper 95% Confidence',
-					data: upperData,
+					label: 'Upper Confidence',
+					data:[],
					borderColor: 'black',
					pointRadius: 0,
				},
			]
		},
		options: {
			scales: {
				x: {
					type: 'linear',
					title: {
						display: true,
						text: 'Population',
					}
				},
				y: {
					type: 'linear',
+					min: 0,
+					max: 100,
					title: {
						display: true,
						text: 'Percentage Fully Vaccinated',
					}
				}
			},
			plugins: {
				title: {
					display: true,
					text: 'Percent Vaccination for Alberta Regions',
				},
				tooltip: {
					callbacks: {
						label: (context) => context.raw.label ? context.raw.label : '',
					}
				}
			},
		},
	};
-	const chart = new Chart(ctx, options)
+	chart = new Chart(ctx, options)
}

window.onload = setup
```

Which results in the following:

![Website - Chart with selectable confidence intervals](/src/content/blog/2021-10-04-chart-js/resources/chart-5.png)

There's actually quite a bit going on here, so let's take a look at some of the highlights. First, we want to move the chart object out of the `setup` function, since it will now be changed in a few different places. In the `setup` function, we set the data for the confidence intervals to empty arrays - before the user selects it, we want it to be blank. We also created the `updateChart` function, which updates the chart data with the new confidence interval calculations and updates the chart using `chart.update()`. Finally, we add an event handler to the select element which we created in `index.html` so that changing the confidence interval updates the graph.

## Conclusion and Areas for Improvement

So there we have it! We created a simple bar graph and scatter plot, added a line graph, and learned how to update a graph with new data. We also took a look at some simple methods of improving the aesthetic appeal of the chart itself. And hopefully, we learned something about COVID-19 vaccination rates in Alberta!

While the primary intent was to explore Chart.js using a topic that was (at least to me) somewhat interesting, there are a lot of ways that it could be improved!

First, hard-coding the data in was quite painful. Since the Alberta Government makes the data so readily available anyway, an obvious improvement would be to load in that data (using `fetch`, probably) when the page loads. This would also make it so that the data is automatically up to date - after all, we just got the most recent data on load!

Second, the site itself is not very aesthetically pleasing. It could certainly use some CSS!

Third, calculating the confidence intervals takes a noticeable amount of time, and during that time the webpage is unresponsive. Some sort of indication (a spinner?) that there is a calculation happening would make the whole interaction more pleasant. Since the calculations are so time-consuming, and there are only a few values that the confident interval can take, it would also make sense to memoize the result in some fashion as well.

However, despite these shortcomings I think that the result is still pretty interesting, and I certainly enjoyed coding something up without the use of external libraries. Good luck!
