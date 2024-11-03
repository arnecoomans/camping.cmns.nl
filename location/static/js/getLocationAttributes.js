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
        $('#attributemessages').append('<div class="alert alert-danger alert-dismissible fade show" role="alert">' + data.message + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
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
  url = $(element).attr('href');
  console.log('toggle value on ' + url);
  $.ajax({
    url: url,
    dataType: 'json',
    success: function(data){
      // console.log(data);
      console.log('Request executed successfully: ' + data.message);
      $('#messages-placeholder').empty().append('<div class="alert alert-success alert-dismissible fade show" role="alert">' + data.message + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
      callback(data['success-url'], data['target']);
    },
    error: function(jqXHR, textStatus, errorThrown){
      console.log('Error: ' + errorThrown);
      if (jqXHR.responseJSON && jqXHR.responseJSON.message) {
        $('#messages-placeholder').append('<div class="alert alert-danger alert-dismissible fade show" role="alert">Error: ' + jqXHR.responseJSON.message + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
      } else {
        $('#messages-placeholder').append('<div class="alert alert-danger alert-dismissible fade show" role="alert">Error: ' + errorThrown + '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>');
      }
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