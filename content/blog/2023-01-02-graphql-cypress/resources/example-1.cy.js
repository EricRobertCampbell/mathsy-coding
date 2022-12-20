// example.cy.js

const aliasGraphqlQuery = (query, operationName, alias) => {
  if (
    query.body.hasOwnProperty("operationName") &&
    query.body.operationName === operationName
  ) {
    query.alias = alias;
  }
};

describe("The application", () => {
  beforeEach(() => {
    cy.intercept("/graphql", res => {
      aliasGraphqlQuery(res, "todos", "getTodosQuery");
    });
  });

  it("Should make the graphql call to load the todos when the button is pressed", () => {
    cy.visit("/");
    cy.contains("h1", "Todos").should("exist");
    cy.contains("button", /get todos/i).click();
    cy.wait("@getTodosQuery");
    cy.get("label").its("length").should("be.gt", 0);
  });
});
