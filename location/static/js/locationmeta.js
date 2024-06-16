$(document).ready(function(){
  // Initialize the tooltip for the like button
  $('#like').tooltip();

  $('.action.list').on('click', '#like', function(){
    url = $(this).data('url');
    $.ajax({
      url: url,
      type: 'GET',
      success: function(data){
        if (data.status.code == 0) {
          $('#messages').append('<div class="alert alert-danger alert-dismissible fade show" role="alert">' + data.status.name + ': ' + data.status.message + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
          return false;
        } else {
          // Based on the feedback of the server, if the location is liked or not, change the icon and the title of the like button
          if (data['data']['favorite'] == true) {
            $('#like').attr('title', 'Je vindt deze locatie leuk');
            $('#like').find('use').attr('xlink:href', '/static/bootstrap-icons/bootstrap-icons.svg#balloon-heart-fill');
            $('#like').tooltip('dispose').tooltip();
          } else {
            $('#like').attr('title', 'Je vindt deze locatie niet meer leuk');
            $('#like').find('use').attr('xlink:href', '/static/bootstrap-icons/bootstrap-icons.svg#balloon-heart');
            $('#like').tooltip('dispose').tooltip();
          }
        }
      }
    });
    // Prevent the following of the link
    return false;
  });
});