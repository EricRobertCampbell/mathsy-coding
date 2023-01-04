const aliasGraphqlQuery = (query, operationName, alias) => {
  if (
    query.body.hasOwnProperty("operationName") &&
    query.body.operationName === operationName
  ) {
    query.alias = alias;
  }
};

/**
 * Function to ensure that no call matching the filter condition is made after an action is performed
 * @param {string} queryAlias - The alias for the query to be checked against
 * @param {function} filter - A filter function which takes an interception as an argument
 * @param {function} action - A function which should perform some sort of action which should *not* cause a graphql call matching the filter condition
 * @param {number} timeout - the number of milliseconds to wait after taking the action for the call to be made
 */
const ensureQueryNotMadeAfterAction = (
  queryAlias,
  filter,
  action,
  timeout = 500
) => {
  const allAlias = `${queryAlias}.all`;
  let numCalls;
  // get the initial number of matching calls
  cy.get(allAlias).then(interceptions => {
    numCalls = interceptions.filter(filter).length;
  });

  // take some action and wait to give time for the call to be made
  action();
  cy.wait(timeout);

  // now check that the number of matching calls hasn't changed
  cy.get(allAlias).then(interceptions => {
    expect(interceptions.filter(filter).length).to.eq(numCalls);
  });
};
describe("The application", () => {
  beforeEach(() => {
    cy.intercept("/graphql", res => {
      aliasGraphqlQuery(res, "todos", "getTodosQuery");
    }).as("graphql");
  });
  it("Should make the graphql call to load the todos when the button is pressed", () => {
    cy.visit("/");
    cy.contains("h1", "Todos").should("exist");
    cy.contains("button", /get todos/i).click();
    cy.wait("@getTodosQuery");
    cy.get("label").its("length").should("be.gt", 0);
  });
  it("Should not make a graphql call when the broken button is clicked", () => {
    cy.visit("/");
    cy.contains("h1", "Todos").should("exist");

    // we care about the 'todo' operation
    const filter = interception =>
      interception.request.body.operationName === "todo";
    // the action that shouldn't trigger the query is clicking the broken button
    const action = () =>
      cy.contains("button", /don't get additional todos/i).click();
    ensureQueryNotMadeAfterAction("@graphql", filter, action);
  });
});
