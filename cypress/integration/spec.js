describe('App', function(){
  it('should have a title', function() {
    cy.visit('http://localhost:8888/');
    cy.title().should('equal', 'Heatmap + Scatterplots');

    // TODO: Test heatmap interactions

    // TODO: Test sample-by-sample plot

    cy.contains('Volcano').click();
    // TODO: Test volcano plot

    cy.contains('Table').click();
    // TODO: Test gene table

    cy.contains('List').click();
    // TODO: Test gene list


    // TODO: Test PCA

    cy.contains('IDs').click();
    // TODO: Test IDs list

    cy.contains('Options').click();
    // TODO: Test options

    cy.contains('Help').click();
    // TODO: Test help
  });
});
