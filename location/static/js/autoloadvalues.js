function displayElement(type, element) {
  display = '<a class="' + type 
  if (typeof allowDelete != 'undefined' && allowDelete == 1) {
    display = display + ' remove-value';
  }
  display = display + '" href="' + element.url + '" '
  display = display + 'data-value="' + element.name + '" ';
  display = display + '>';
  if (element.parent.length > 0) {
    display = display + element.parent + ': ';
  }
  display = display + element.name;
  if (typeof(allowDelete) !== 'undefined' && allowDelete == 1) {
    display = display + ' <sup>x</sup>';
  } else if (element.locations > 1) {
    display = display + ' <sup>' + element.locations + '</sup>';
  }
  display = display + '</a>';
  return display;
}

function autoloadData(element) {
  var url = element.data('url');
  var type = element.data('type');
  if (typeof debug != 'undefined' && debug == 1) {
    console.log('autoloading ' + type + ' on ' + url);
  }
  $.ajax({
    url: url,
    dataType: 'json',
    success: function(data){
      if (data.status.code == 0) {
        element.append('<div class="alert alert-danger alert-dismissible fade show" role="alert">' + data.status.name + ': ' + data.status.message + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
        return false;
      } else {
        // Update .valuecounter with the number of values
        if (data['data']['values'].length > 0) {
          element.children('.title-col').children('.valuecounter').text(' (' + data['data']['values'].length + ')')
        }
        // Store the target for the values
        var target = element.children('.list-col');
        // Set seperator to ', ' unless it's the last value
        var seperator = ', ';
        // Clear the list-col to avoid duplicates
        target.empty();
        // For each value in data, add it to the list-col
        $.each(data['data']['values'], function(index, value){
          
          if (index == data['data']['values'].length - 1) {
            seperator = '';
          }
          target.append(displayElement(type, value) + seperator);
        });
      }
    }
  });
}

$(document).ready(function() {
  // For each autoload element, fetch the data from the server
  $('.autoload').each(function() {
    var element = $(this);
    autoloadData(element);
  });
});