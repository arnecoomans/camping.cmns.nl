function getTagDisplay(tag) {
  var display = '<a class="tag ' + tag.get_list_as_display + '" data-tag="' + tag.name + '" href="' + tag.url + '">'
  if (tag.list_as == 'a') {
    display = display + '<img src="/static/bootstrap-icons/hand-thumbs-up-fill.svg">'
  } else if (tag.list_as == 'd') {
    display = display + '<img src="/static/bootstrap-icons/hand-thumbs-down-fill.svg">'
  }
  display = display + tag.parent + tag.name
  if (tagAllowRemove == 1) {
    display = display + ' <sup>x</sup>'
  } else if (tag.locations > 1) {
    display = display + ' <sup>' + tag.locations + '</sup>'
  }
  
  display = display + '</a>'
  return display;
}

function getAllTags(url, callback) {
  $('#tags').empty();
  $.ajax({
    url: tagBaseUrl + 'list/',
    headers: {'X-CSRFToken': csrf_token},
    dataType: 'json',
    success: function(data){
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
      } 
    }
  });
}

// function toggleTag(tag) {
//   $.ajax({
//     url: tagBaseUrl,
//     headers: {'X-CSRFToken': csrf_token},
//     data: {
//       'tag': tag,
//     },
//     dataType: 'json',
//     success: function(data){
//       if (data.status.code == 0) {
//         $('#tagmessages').append('<div class="alert alert-danger" role="alert">' + data.status.name + ': ' + data.status.message + '</div>');
//         return false;
//       } else {
//         getAllTags(tagBaseUrl + 'list/', function(data){
//           // take no action, the comments are already added to the DOM
//         });
//         console.log(data['data']['status'])
//         $('input[name="addtag"]').val('');
//         $('.row.addtag').hide();
//         $('#addtag').show();
//       }
//     }
//   });
// }

$(document).ready(function() {
  // Fetch new comments on page load
  getAllTags(tagBaseUrl + 'list/', function(data){
    // take no action, the comments are already added to the DOM
  });

//   // Show Add Tag Form
//   $('#tags').on('click', '#addtag', function(){
//     $('.row.addtag').show();
//     $(this).hide();
//   });

//   $('#autocomplete').autocomplete({
//     source: function(request, response) {
//         $.ajax({
//             url: tagBaseUrl + 'suggest/', 
//             data: {
//                 query: request.term // The current input string
//             },
//             success: function(data) {
//                 response(data); // A JSON array of suggestions
//             }
//         });
//     },
//     minLength: 2 // Only start suggesting after 2 characters have been typed
// });

  // // Handle Add Tag
  // $('#addtagbutton').click(function(){
  //   tag = $('input[name="addtag"]').val();
  //   if (tag == undefined) {
  //     $('#tagmessages').append('<div class="alert alert-danger" role="alert">No tag entered</div>');
  //     return false;
  //   }
  //   url = $('input[name="addtag"]').data('url');
  //   toggleTag(tag);
  // });

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

  $('#tags').on('click', '.tag', function(event){
    if (tagAllowRemove == 1) {
      // Prevent following the link
      event.preventDefault();
      toggleTag($(this).data('tag'));
    }
  });
});