function getTagDisplay(tag) {
  var display = '<a class="tag ' + tag.get_list_as_display + '" href="' + tag.url + '">'
  if (tag.list_as == 'a') {
    display = display + '<img src="/static/bootstrap-icons/hand-thumbs-up-fill.svg">'
  } else if (tag.list_as == 'd') {
    display = display + '<img src="/static/bootstrap-icons/hand-thumbs-down-fill.svg">'
  }
  display = display + tag.name
  if (tag.locations > 1) {
    display = display + ' <sup>' + tag.locations + '</sup>'
  }
  display = display + '</a>'
  return display;
}

function getAllTags(url, callback) {
  $.ajax({
    url: url,
    headers: {'X-CSRFToken': csrf_token},
    dataType: 'json',
    success: function(data){
      // Based on the status of the response, take the correct action
      // Ranging from bad to good; error, warning, success
      if (data.status.code == 0) {
        $('#comment-messages').append('<div class="alert alert-danger" role="alert">' + data.status.name + ' when loading comments: ' + data.status.message + '</div>');
        return false;
      } else {
        if (data['data']['tags'].length > 0) {
          $('#tagcounter').text(' (' + data['data']['tags'].length + ')')
        }
        $('#tags').empty();
        $.each(data['data']['tags'], function(index, tag){
          var seperator = ', ';
          if (index == data['data']['tags'].length - 1) {
            seperator = '';
          }
          $('#tags').append(getTagDisplay(tag) + seperator);
        });
      } 
    }
  });
}

$(document).ready(function() {
  // Fetch new comments on page load
  getAllTags(fetchTagUrl, function(data){
    // take no action, the comments are already added to the DOM
  });

  // Handle Add Comment
  $('#add-comment').click(function(){
    // Fetch required fields
    var url = $(this).data('url');
    var content = $('textarea[name="content"]').val();
    var visibility = $('select[name="visibility"]').val();
    /// Submit the data to the server
    $.ajax({
      url: url,
      headers: {'X-CSRFToken': csrf_token},
      data: {
        'content': content,
        'visibility': visibility,
      },
      dataType: 'json',
      success: function(data){
        if (data.status.code == 0) {
          $('#comment-messages').append('<div class="alert alert-danger alert-dismissible fade show" role="alert">' + data.status.name + ': ' + data.status.message + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
          return false;
        } else {
          $('#comment-messages').append('<div class="alert alert-success alert-dismissible fade show" role="alert">Comment added succesfully!<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
          $('#comments').prepend(getCommentDisplay(data.data.comment));
          $('textarea[name="content"]').val('');
        }
      }
    });
  });

});