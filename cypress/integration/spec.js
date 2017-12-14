describe('App', function(){
  it('should have a title', function() {
    cy.visit('http://localhost:8888/');
    cy.title().should('equal', 'Heatmap + Scatterplots');
  });
});
