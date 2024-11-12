/** FetchData
 * Fetch data from a given url and add the payload html to a given target element.
 * 
 * @param {string} url - The url to fetch the data from.
 * @param {string} target - The target element (id) to add the payload html to.
 * @returns {void}
 */

function getLocationAttributes(url, target) {
  console.log('fetching data from ' + url + ' for ' + target);
  $.ajax({
    url: url,
    dataType: 'json',
    success: function(data){
      // console.log(data);
      if (data.error == true) {
        $('#messages-placeholder').append('<div class="alert alert-danger alert-dismissible fade show" role="alert">' + data.message + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
        console.log('Error: ' + data.message);
        return false;
      } else {
        console.log('Data fetched successfully and writing to ' + target);
        $('#' + target).empty();
        $.each(data['payload'], function(index, payload){
          $('#' + target).append(payload);
        });
        if (data['message']) {
          $('#messages-placeholder').append('<div class="alert alert-success alert-dismissible fade show" role="alert">' + data.message + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
        }
      }
    },
    error: function(jqXHR, textStatus, errorThrown){
      console.log(jqXHR);
      console.log('Error: ' + errorThrown);
      if (jqXHR.responseJSON && jqXHR.responseJSON.message) {
        $('#messages-placeholder').append('<div class="alert alert-danger alert-dismissible fade show" role="alert">Error A: ' + jqXHR.responseJSON.message + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
      } else {
        $('#messages-placeholder').append('<div class="alert alert-danger alert-dismissible fade show" role="alert">Error B: ' + errorThrown + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
      }
    }
  });
}

/** toggleLocationAttribute
 * 
 * Toggle the location attribute of an element by calling an ajax function toggle
 * a location attribute. On success, reload the container element with the new data.
 * Address of the toggle function should be the same as the href for the non-ajax
 * request, but response should be in json format for json requests.
 * @param {element} element - The element that triggers the action.
 * @param {function} callback - The callback function to call after the ajax request
 *   with the fields success-url and target.
 * @returns {void}
 */
function toggleLocationAttribute(element, callback) {
  console.log('toggleLocationAttribute');
  url = $(element).attr('href');
  console.log('toggle value on ' + url);
  $.ajax({
    url: url,
    dataType: 'json',
    success: function(data){
      // console.log(data);
      console.log('Request executed successfully: ' + data.__meta['resolver']);
      /** Add messages to messages container */
      data['messages'].forEach(function(message){
        $('#messages-placeholder').append('<div class="alert alert-' + message[0] + ' alert-dismissible fade show" role="alert">' + message[1] + '.  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
      });
      /** Callback - Update field data that has been toggled */
      list = $('#' + data['field']);
      if (list.attr('data-source')) {
        getLocationAttributes(list.attr('data-source'), list.attr('id'));
      } else {
        console.log('No data-source found for ' + list.attr('id'));
      }
    },
    error: function(jqXHR, textStatus, errorThrown){
      console.log('Error: ' + errorThrown);
      jqXHR.responseJSON['messages'].forEach(function(message){
        $('#messages-placeholder').append('<div class="alert alert-' + message[0] + ' alert-dismissible fade show" role="alert">' + message[1] + '.  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
      });
    }
  });
}

$(document).ready(function(){
  $(document).on('click', '.toggable', function(event) {
    $(this).tooltip('dispose');
    toggleLocationAttribute($(this), getLocationAttributes);
    event.preventDefault();
    return false;
  });
});