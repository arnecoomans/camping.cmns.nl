function getCommentDisplay(comment) {
  var dt = DateTime.fromISO(comment.date_added);
  var display = '<div class="comment card" data-id="comment-' + comment.id + '">' +
                '  <div class="header">' +
                '    <span data-bs-toggle="tooltip" data-bs-placement="top" title="' + dt.toFormat("dd LLLL y HH:MM") + '">' + dt.toRelative() +  '</span>' +
                '    <a href="/comments/by:' + comment.user.username + '/">' + comment.user.displayname + '</a>' +
                '    @ <a href="/location/' + comment.location.slug + '/">' + comment.location.name + '</a>' +
                '   (' + comment.visibility + ')' +
                '  </div>' +
                '  <div class="content">' + comment.content + '</div>'
  if (comment.user.id == currUser || currAuth === 'True') {
    display = display + '<ul class="action list">'
    if (comment.user.id == currUser) {
      display = display + '<li><a href="/comment/' + comment.id + '/edit/"><svg class="bi" width="16" height="16" fill="currentColor"><use xlink:href="/static/bootstrap-icons/bootstrap-icons.svg#pencil"/></svg></a></li>' +
                          '<li><a href="/comment/' + comment.id + '/delete/"><svg class="bi" width="16" height="16" fill="currentColor"><use xlink:href="/static/bootstrap-icons/bootstrap-icons.svg#trash"/></svg></a></li>'
    }
    if (currAuth === 'True') {
      display = display + '<li><a href="/admin/location/comment/' + comment.id + '/change/" target="_blank" ><svg class="bi" width="16" height="16" fill="currentColor"><use xlink:href="/static/bootstrap-icons/bootstrap-icons.svg#pencil-square"/></svg></a></li>'
    }
    display = display +'</ul>'

  }
  var display = display + '</div>'
  return display;
}

function getAllComments(url, callback) {
  $.ajax({
    url: url,
    headers: {'X-CSRFToken': csrf_token},
    dataType: 'json',
    success: function(data){
      // Based on the status of the response, take the correct action
      // Ranging from bad to good; error, warning, success
      if (data.status.code == 0) {
        $('#messages').append('<div class="alert alert-danger" role="alert">' + data.status.name + ': ' + data.status.message + '</div>');
        return false;
      } else {
        $.each(data['data']['comments'], function(index, comment){
          $('#comments').append(getCommentDisplay(comment));
        });
      } 
    }
  });
}

$(document).ready(function() {
  // Fetch new comments on page load
  getAllComments(fetchCommentUrl, function(data){
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