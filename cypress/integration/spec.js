describe('App', function(){
  it('should have a title', function() {
    cy.visit('http://localhost:8888/');
    cy.title().should('equal', 'Heatmap + Scatterplots');
    cy.contains('Volcano').click();

    cy.get('body').should('not.contain', 'linear');
    cy.contains('log').parent().click();
    cy.get('body').should('contain', 'linear').click();

    // TODO: This has been flakey for me.
    // cy.get('body').should('not.contain', 'log');
    // cy.contains('linear').parent().click();
  });
});
