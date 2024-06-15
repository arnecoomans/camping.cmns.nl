function getCategoryDisplay(category) {
  var display = '<a class="category" href="' + category.url + '">'
  display = display + category.parent + category.name
  if (allowRemove == 1) {
    display = display + ' <sup>x</sup>'
  } else if (category.locations > 1) {
    display = display + ' <sup>' + category.locations + '</sup>'
  }
  display = display + '</a>'
  return display;
}

function getAllCategories(url, callback) {
  $('#additional_categories').empty();
  $.ajax({
    url: url,
    headers: {'X-CSRFToken': csrf_token},
    dataType: 'json',
    success: function(data){
      if (data.status.code == 0) {
        $('#category-messages').append('<div class="alert alert-danger" role="alert">' + data.status.name + ' when loading categories: ' + data.status.message + '</div>');
        return false;
      } else {
        if (data['data']['categories'].length > 0) {
          $('#categorycounter').text(' (' + data['data']['categories'].length + ')')
        }
        $('#additional_categories').empty();
        $.each(data['data']['categories'], function(index, category){
          var seperator = ', ';
          if (index == data['data']['categories'].length - 1) {
            seperator = '';
          }
          $('#additional_categories').append(getCategoryDisplay(category) + seperator);
        });
        add_show_autosuggest_button($(this))
        // $('#additional_categories').append(' &nbsp;&nbsp;<button class="btn btn-outline-secondary show_autosuggest" id="">+</a>');
      } 
    }
  });
}

$(document).ready(function() {
  // Fetch new comments on page load
  getAllCategories(categoryBaseUrl + 'list/', function(data){
    // take no action, the comments are already added to the DOM
  });

//   // Show Add Tag Form
//   $('#additional_categories').on('click', '#addcategory', function(){
//     $('.row.add_additional_categories').show();
//     $(this).hide();
//   });

//   $('#autocomplete').autocomplete({
//     source: function(request, response) {
//         $.ajax({
//             url: categoryBaseUrl + 'suggestion/',
//             data: {
//                 query: request.term
//             },
//             success: function(data) {
//                 response(data);
//             }
//         });
//     },
//     minLength: 2 // Only start suggesting after 2 characters have been typed
// });

//   // Handle Add Tag
//   $('#addtagbutton').click(function(){
//     tag = $('input[name="addtag"]').val();
//     if (tag == undefined) {
//       $('#tagmessages').append('<div class="alert alert-danger" role="alert">No tag entered</div>');
//       return false;
//     }
//     url = $('input[name="addtag"]').data('url');
//     console.log(url);
//     $.ajax({
//       url: url,
//       headers: {'X-CSRFToken': csrf_token},
//       data: {
//         'tag': tag,
//       },
//       dataType: 'json',
//       success: function(data){
//         console.log(data)
//         if (data.status.code == 0) {
//           $('#tagmessages').append('<div class="alert alert-danger" role="alert">' + data.status.name + ': ' + data.status.message + '</div>');
//           return false;
//         } else {
//           getAllTags(fetchTagUrl, function(data){
//             // take no action, the comments are already added to the DOM
//           });
//           $('input[name="addtag"]').val('');
//           $('.row.addtag').hide();
//           $('#addtag').show();
//         }
//       }
//     });
//   });

//   // Capitalize input
//   $('input[name="addtag"]').on('input', function() {
//     var inputVal = $(this).val();
//     var capitalizedVal = inputVal.replace(/\b\w/g, function(char) {
//         return char.toUpperCase();
//     });
//     $(this).val(capitalizedVal);
// });
  
//   // Accept enter to submit tag
//   $('input[name="addtag"]').keypress(function(event) {
//     // Check if the key pressed is Enter (key code 13)
//     if (event.which === 13) {
//         event.preventDefault(); // Prevent the default action if needed
//         $('#addtagbutton').click(); // Trigger the button click
//     }
//   });
});