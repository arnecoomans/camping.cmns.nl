$(document).ready(function() {
  // Fetch new comments
  console.log('Fetching comments from ' + baseUrl)
  $.ajax({
    url: baseUrl,
    headers: {'X-CSRFToken': csrf_token},
    dataType: 'json',
    success: function(data){
      // Based on the status of the response, take the correct action
      // Ranging from bad to good; error, warning, success
      console.log(data)
      if (data.status.code == 0) {
        $('#messages').append('<div class="alert alert-danger" role="alert">' + data.status.name + ': ' + data.status.message + '</div>');
        return false;
      } else {
        $.each(data['data']['comments'], function(index, comment){
          var display = '<div class="comment card" data-id="comment-' + comment.id + '">' +
                        '  <div class="header">' +
                        '    <span data-bs-toggle="tooltip" data-bs-placement="top" title="' + comment.date_added + '">' + comment.date_added +  '</span>' +
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
          $('#comments').append(display);
        });
      } 
    }
  });
});