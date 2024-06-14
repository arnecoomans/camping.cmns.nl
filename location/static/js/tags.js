function getTagDisplay(tag) {
  var display = '<a class="tag ' + tag.get_list_as_display + '" href="' + tag.url + '">'
  if (tag.list_as == 'a') {
    display = display + '<img src="/static/bootstrap-icons/hand-thumbs-up-fill.svg">'
  } else if (tag.list_as == 'd') {
    display = display + '<img src="/static/bootstrap-icons/hand-thumbs-down-fill.svg">'
  }
  display = display + tag.parent + tag.name
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

  $('#autocomplete').autocomplete({
    source: function(request, response) {
        $.ajax({
            url: fetchTagSuggestions, // Update with your API endpoint
            data: {
                query: request.term // The current input string
            },
            success: function(data) {
                response(data); // Assuming your API returns a JSON array of suggestions
            }
        });
    },
    minLength: 2 // Only start suggesting after 2 characters have been typed
});

  // Handle Add Tag
  $('#addtagbutton').click(function(){
    tag = $('input[name="addtag"]').val();
    console.log(tag);
    if (tag == undefined) {
      $('#tagmessages').append('<div class="alert alert-danger" role="alert">No tag entered</div>');
      return false;
    }
    url = $('input[name="addtag"]').data('url');
    console.log(url);
    $.ajax({
      url: url,
      headers: {'X-CSRFToken': csrf_token},
      data: {
        'tag': tag,
      },
      dataType: 'json',
      success: function(data){
        console.log(data)
        if (data.status.code == 0) {
          $('#tagmessages').append('<div class="alert alert-danger" role="alert">' + data.status.name + ': ' + data.status.message + '</div>');
          return false;
        } else {
          getAllTags(fetchTagUrl, function(data){
            // take no action, the comments are already added to the DOM
          });
          $('input[name="addtag"]').val('');
          $('.row.addtag').hide();
          $('#addtag').show();
        }
      }
    });
  });

  // Capitalize input
  $('input[name="addtag"]').on('input', function() {
    var inputVal = $(this).val();
    var capitalizedVal = inputVal.replace(/\b\w/g, function(char) {
        return char.toUpperCase();
    });
    $(this).val(capitalizedVal);
});
  
  // Accept enter to submit tag
  $('input[name="addtag"]').keypress(function(event) {
    // Check if the key pressed is Enter (key code 13)
    if (event.which === 13) {
        event.preventDefault(); // Prevent the default action if needed
        $('#addtagbutton').click(); // Trigger the button click
    }
  });
});