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
  $('#tags').empty();
  $.ajax({
    url: url,
    headers: {'X-CSRFToken': csrf_token},
    dataType: 'json',
    success: function(data){
      // Based on the status of the response, take the correct action
      // Ranging from bad to good; error, warning, success
      if (data.status.code == 0) {
        $('#tag-messages').append('<div class="alert alert-danger" role="alert">' + data.status.name + ' when loading tags: ' + data.status.message + '</div>');
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
        $('#tags').append(' &nbsp;&nbsp;<button class="btn btn-outline-secondary" id="addtag">+</a>');
      } 
    }
  });
}

$(document).ready(function() {
  $('.row.addtag').hide();
  // Fetch new comments on page load
  getAllTags(fetchTagUrl, function(data){
    // take no action, the comments are already added to the DOM
  });

  // Show Add Tag Form
  $('#tags').on('click', '#addtag', function(){
    $('.row.addtag').show();
    $(this).hide();
  });

  // Handle Add Tag
  $('#addtagbutton').click(function(){
    tag = $('select[name="addtag"]').val();
    if (tag == '-') {
      $('#tagmessages').append('<div class="alert alert-danger" role="alert">No tag selected</div>');
      return false;
    }
    url = $('select[name="addtag"]').data('url');
    $.ajax({
      url: url,
      headers: {'X-CSRFToken': csrf_token},
      data: {
        'tag': tag,
      },
      dataType: 'json',
      success: function(data){
        if (data.status.code == 0) {
          $('#tagmessages').append('<div class="alert alert-danger" role="alert">' + data.status.name + ': ' + data.status.message + '</div>');
          return false;
        } else {
          getAllTags(fetchTagUrl, function(data){
            // take no action, the comments are already added to the DOM
          });
          $('select[name="addtag"]').prop('selectedIndex', 0);
          $('select[name="addtag"] option[value="' + tag + '"]').remove();
          $('.row.addtag').hide();
          $('#addtag').show();
        }
      }
    });
  });
});