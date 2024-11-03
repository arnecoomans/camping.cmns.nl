$(document).ready(function() {
  /// Handle Submit Comments
  $('button.submit-comment').on('click', function() {
    console.log('Submit Comment');
    // Fetch Comment Data
    parent = $('#addcomment')
    var url = parent.data('url');
    var csrf = parent.data('csrf');
    var location = parent.data('location');
    var comment = $('textarea[name="content"]').val();
    var visibility = $('select[name="visibility"]').val();
    /// Submit the data to the server
    console.log('Preparing to post comment: "' + comment + '" to ' + url + ' with visibility ' + visibility);
    $.ajax({
      url: url,
      headers: {'X-CSRFToken': csrf},
      data: {
        'location': location,
        'comment': comment,
        'visibility': visibility,
      },
      dataType: 'json',
      success: function(data){
        console.log(data);
        $('#messages-placeholder').empty().append('<div class="alert alert-success alert-dismissible fade show" role="alert">Comment added succesfully!<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
        $('textarea[name="content"]').val('');
        getLocationAttributes(data['success-url'], 'commentlist');
      }, 
      error: function(jqXHR, textStatus, errorThrown){
        console.log(jqXHR);
        $('#messages-placeholder').empty().append('<div class="alert alert-danger alert-dismissible fade show" role="alert">Error ' + jqXHR.status + ': ' + jqXHR.responseJSON.message + '.<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
        return false;
      }
    });
  });
});