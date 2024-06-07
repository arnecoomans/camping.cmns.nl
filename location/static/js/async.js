function getData(scope, query, callback) {
  // Get the data from the server
  $.ajax({
    url: baseUrl + scope + '/',
    headers: {'X-CSRFToken': csrf_token},
    data: {
      'q': query
    },
    dataType: 'json',
    success: function(data){
      // Based on the status of the response, take the correct action
      // Ranging from bad to good; error, warning, success
      if (data.status == 'error') {
        $('.messages').append('<div class="alert alert-danger" role="alert">' + data.status + ': ' + data.message + '</div>');
        if (debug) { console.log(data.status + ' when requesting permits: ' + data.message); }
        return false;
      } else if (data.status == 'warning') {
        $('.messages').append('<div class="alert alert-warning" role="alert">' + data.message + '</div>');
        if (debug) { console.log(data.status + ' when requesting permits: ' + data.message); }
        return false;
      } else if (data.status == 'success') {
        if (data.data.length > 0) {
          if (debug) { console.log(data) }
        }
        callback(data);
      } else {
        // Handle unknown status with a console log message
        if (debug) { console.log('Unknown status: ' + data.status + ': ' + data.message) }
      }
    }
  });
}