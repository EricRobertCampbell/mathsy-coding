import express from "express";
import cors from "cors";
import { graphqlHTTP } from "express-graphql";
import { buildSchema } from "graphql";

const schema = buildSchema(`
type Todo {
	task: String!
	complete: Boolean!
}
type Query {
	todos: [Todo]
}
`);

const root = {
	todos: () => {
		return [
			{
				task: "Finish the first task",
				complete: true,
			},
			{
				task: "Finish the second task",
				complete: false,
			},
			{
				task: "Finish the third task",
				complete: false,
			},
		];
	},
};

const app = express();
app.use(cors({ credentials: true, origin: true }));
app.use(
	"/graphql",
	graphqlHTTP({
		schema,
		rootValue: root,
		graphiql: true,
	})
);
app.listen(4000);
console.log("Running a GraphQL API server at http://localhost:4000/graphql");
