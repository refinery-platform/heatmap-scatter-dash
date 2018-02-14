describe('heatmap-scatterplot', function(){
  it('dash (heatmap) works', function() {
    cy.visit('http://localhost:8888/');
    cy.title().should('equal', 'Heatmap + Scatterplots');
    cy.location('search').should('equal',
        '?scale=log&palette=black-white&cluster-rows=cluster'
        + '&cluster-cols=cluster&label-rows=auto&label-cols=auto');
    cy.get('#heatmap svg').should('be.visible');
    cy.get('#search-genes').click(); // TODO: type() fails
  });

  it('dash (top tabs) work', function() {
    cy.visit('http://localhost:8888/');
    cy.get('#pca svg').should('be.visible');

    cy.get('#ids-iframe').should('not.be.visible');
    cy.contains('IDs').click();
    cy.get('#pca svg').should('not.be.visible');
    cy.get('#ids-iframe').should('be.visible');

    cy.contains('Options').click();
    cy.get('#ids-iframe').should('not.be.visible');
    cy.contains('.Select', 'log').click();
    cy.contains('.Select', 'black-white').click();
    cy.contains('.Select', 'cluster').click();
    cy.contains('.Select', 'auto').click();
    // TODO: Change selection: They are not really selects, so this is hard?

    cy.contains('a', 'Help').click();
    // Can't actually visit new page:
    // https://docs.cypress.io/faq/questions/using-cypress-faq.html#Can-I-test-anchor-links-that-open-in-a-new-tab

  });

  it('dash (bottom tabs) work', function() {
    cy.visit('http://localhost:8888/');
    cy.get('#sample-by-sample svg').should('be.visible');

    cy.get('#volcano svg').should('not.be.visible');
    cy.contains('Volcano').click();
    cy.get('#volcano svg').should('be.visible');
    // TODO: Test volcano plot

    cy.contains('.Select', 'log_fold_change').click();
    cy.contains('.Select', '-log10').click();
    cy.contains('.Select', 'stats-with-genes-in-col-1.csv').click();
    // TODO: Change selection

    cy.get('#table-iframe').should('not.be.visible');
    cy.contains('Table').click();
    cy.get('#table-iframe').should('be.visible');
    // TODO: Test content of iframe

    cy.get('#list-iframe').should('not.be.visible');
    cy.contains('List').click();
    cy.get('#list-iframe').should('be.visible');
    // TODO: Test content of iframe
  });

  it('help works', function() {
    cy.visit('http://localhost:8888/help');
    cy.title().should('equal', 'Heatmap + Scatterplots: Help');
    cy.contains('This is a tool for exploring');
  });
});
