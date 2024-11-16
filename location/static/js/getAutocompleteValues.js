$(document).ready(function() {
  /** Hide The Autocomplete  */
  $('.row.add_autocomplete').hide();
  /** Show The Autocomplete  */
  $('button.show-autocomplete').on('click', function() {
    $('.row.add' + $(this).attr('for')).show();
    $(this).hide();
  });

  /** Autocomplete with slug
    */
  $('input.autocomplete').autocomplete({
    source: function(request, response) {
      // Make an AJAX request to fetch suggestions
      $.ajax({
        url: this.element.data('suggest'),
        data: { 'query': request.term.toLowerCase() },
        dataType: 'json',
        success: function(data) {
          // console.log(data);
          // Transform the data into a format that jQuery UI Autocomplete can understand
          response($.map(data['payload'], function(payload) {
            console.log('Autocomplete: found: ' + data['payload'].length + ' results for query ' + request.term);
            return {
              label: payload.text, // The display text
              value: payload.text, // The value to insert into the input field
              slug: payload.slug   // The slug value to store
            };
          }));
        },
        error: function(data) {
          console.log('error: ' + data['message']);
          // console.log(data);
        }
      });

      minLength: 2 // Only start suggesting after 2 characters have been typed
    },
    select: function(event, ui) {
      // When a suggestion is selected, set the input value and the slug
      $(this).val(ui.item.value); // Set the display text
      $(this).data('slug', ui.item.slug); // Store the slug in data-slug
      return false; // Prevent the default behavior
    }
  });

  /** Handle Submit Value Button
   * 
   */
  $('button.submit-value').on('click', function() {
    // Fetch the target from the "for" attribute of the button
    var target = $(this).attr('for');
    // Get the value and the slug
    var value = $('input#' + target).val();
    var slug = $('input#' + target).data('slug');
    var url = $(this).data('url');
    if (value == '') {
      console.log('Value is empty');
      return false
    } else if (slug == '') {
      // If the slug is empty, submit the value
      data = {
        'value': value,
      };
    } else {
      // Submit the slug
      data = {
        'value': slug,
      };
    }
    // Submit to the URL
    console.log('Submit "' + data['value'] +  '" to URL:' + url);
    $.ajax({
      url: url,
      data: data,
      dataType: 'json',
      success: function(data) {
        console.log(data);
        console.log('Request executed successfully: ' + data.__meta['resolver']);
        /** Add messages to messages container */
        data['messages'].forEach(function(message){
          $('#messages-placeholder').append('<div class="alert alert-' + message[0] + ' alert-dismissible fade show" role="alert">' + message[1] + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
        });
        /** Callback - Update field data that has been toggled */
        list = $('#' + data['field']);
        if (list.attr('data-source')) {
          console.log('Get location attributes for ' + list.attr('data-source') + ' and ' + list.attr('id'));
          getLocationAttributes(list.attr('data-source'), list.attr('id'));
        } else {
          console.log('No source for ' + list.attr('id'));
        }
        // getLocationAttributes(data['success-url'], data['target']);
        $('input#' + target).val('');
        $('input#' + target).data('slug', '');
        // $('#messages-placeholder').append('<div class="alert alert-' + data[0] + ' alert-dismissible fade show" role="alert">' + data.message[1] + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
        // $('#messages-placeholder').append('<div class="alert alert-success" role="alert">' + data['message'] + '</div>');
      },
      error: function(data) {
        console.log('Error' + data['message']);
        // console.log(data);
      }
    });
  });
});