$(document).ready(function() {
  
  $('.site_seach').autocomplete({
    source: function(request, response) {
      $.ajax({
        // Get the URL from the data-suggestions attribute of the input field
        // Allows for multiple autocomplete fields on the same page
        url: this.element.data('suggestions'),
        data: {
          // Send the search term to the server
          q: request.term
        },
        success: function(data) {
          response(data);
        }
      });

    },
    minLength: 2 // Only start suggesting after 2 characters have been typed
                // Issue #248 experiment with autosuggest tags: show from 0 characters
  });
});