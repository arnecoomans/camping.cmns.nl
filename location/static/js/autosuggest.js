function toggleValue(element, url, value) {
  if (typeof debug != 'undefined' && debug == 1) {
    console.log('toggeling value of ' + value + ' on ' + url);
  }
  // Only proceed if the value is not empty or too short
  if (value.length < 2) {
    $(element).parent().append('<div class="alert alert-danger alert-dismissible fade show" role="alert">Value is too short or invalid  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
    return false;
  }
  // Send the value to the server
  $.ajax({
    url: url,
    data: {
      'value': value
    },
    dataType: 'json',
    success: function(data){
      if (typeof debug != 'undefined' && debug == 1) { console.log(data); }
      // If the server returns an error, show the error message
      if (data.status.code == 0) {
        $(element).parent().append('<div class="alert alert-danger alert-dismissible fade show" role="alert">' + data.status.name + ': ' + data.status.message + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
        return false;
      } else {
        // If the server returns success, empty the element, hide the autosuggest form
        // and show the [+] button
        $(element).val('');
        $(element).closest('.row').hide();

        $(element).closest('.row').prev('.row').find('.show-edit').show();

        // Update the list of values
        var autoload = element.closest('.row').prev('.row');
        if (autoload.length) {
          autoloadData(autoload);
        }
      }
    }
  });
}


$(document).ready(function() {
  $('.row.add_autosuggest').hide();

  // When the [+] button is clicked, unhide the autosuggest form
  // and focus on the input field
  // and hide the [+] button
  $('div').on('click', '.show-edit', function(){
    var element = $(this).parent().closest('.row').next('.row');
    element.show();
    element.find('input').focus();
    $(this).hide();
  });

  // Capitalize input
  $('input.autocapitalize').on('input', function() {
    var inputVal = $(this).val();
    var capitalizedVal = inputVal.replace(/\b\w/g, function(char) {
        return char.toUpperCase();
    });
    $(this).val(capitalizedVal);
});
  // When text is entered in the autocomplete form, fetch suggestions
  // from the server based on the data-suggestions URL and show the 
  // suggestions in a dropdown
  $('.autocomplete').autocomplete({
    source: function(request, response) {
      $.ajax({
        // Get the URL from the data-suggestions attribute of the input field
        // Allows for multiple autocomplete fields on the same page
        url: this.element.data('suggestions'),
        data: {
          // Send the search term to the server
          query: request.term
        },
        success: function(data) {
          response(data);
        }
      });
    },
    minLength: 0 // Only start suggesting after 2 characters have been typed
                 // Issue #248 experiment with autosuggest tags: show from 0 characters
  });

  // When the "Add" button is clicked, submit the form
  // $('div').on('click', '.submit-value', function(){
  //   console.log('submitting');
  // });
  $('.row').on('click', '.submit-value', function() {
  // $('.submit-value').click(function(){
    // Fetch element and element data
    var element = $(this).parent().closest('.row').find('input');
    var value = element.val();
    var url = element.data('url');
    toggleValue(element, url, value);
    event.stopPropagation(); // Prevent the event from bubbling up the DOM tree
    event.preventDefault(); // Prevent the default action if needed
  });
  $('.row').on('keypress', '.submit-value', function(e) {
    if(e.which === 13){
      // Fetch element and element data
      var element = $(this);
      var value = element.val();
      var url = element.data('url');
      toggleValue(element, url, value);
      event.stopPropagation(); // Prevent the event from bubbling up the DOM tree
      event.preventDefault(); // Prevent the default action if needed
    }
    });

  // When the "x" button is clicked, remove the value from the list
  $('div').on('click', '.remove-value', function(event){
    // Fetch element and element data
    var element = $(this).closest('.row').next('.row').find('input');
    var value = $(this).data('value');
    var url = $(this).closest('.row').next('.row').find('input').data('url');
    // Send the value to the server
    toggleValue(element, url, value);
    event.stopPropagation(); // Prevent the event from bubbling up the DOM tree
    event.preventDefault(); // Prevent the default action if needed
  });
});
