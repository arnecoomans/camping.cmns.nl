// Function to apply fade-out to alerts
function applyFadeOut() {
  var duration = 10 * 1000; // X times 1000 ms = X seconds

  $('.alert').each(function() {
    var $this = $(this);

    // Check if the alert already has a fade-out timer to prevent duplication
    if (!$this.data('fade-out-set')) {
      $this.data('fade-out-set', true); // Mark this alert as having a fade-out timer

      // Set the timer for fade-out
      setTimeout(function() {
        $this.fadeOut(1000, function() { // 1000 ms = 1 second fade-out
          message = $this.text();
          message = message.replace('(Undo)', '').trim();
          console.log('Removing alert "' + message + '"');
          $this.remove();
        });
      }, duration);
    }
  });
}

$(document).ready(function() {
  /**  Auto-Capitalize
   * Auto-capitalize the first letter of each word in an input field
   * with the class 'autocapitalize'
   */
  $('input.autocapitalize').on('input', function() {
    var inputVal = $(this).val();
    var capitalizedVal = inputVal.replace(/\b\w/g, function(char) {
        return char.toUpperCase();
    });
    $(this).val(capitalizedVal);
  });

  /** Site Search Autocomplete
   * Site-search is a slugles autocomplete
   */
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

  // Select all alert messages and set a timer to fade them out
  $(document).ready(function() {
    applyFadeOut();
  });

  // Reapply fade-out logic after AJAX content is loaded
  $(document).ajaxComplete(function() {
    applyFadeOut();
});
});