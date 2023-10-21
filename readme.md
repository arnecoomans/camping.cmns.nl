# VKNT Vacation Location and Activity Database

VKNT is a database for holiday locations - places to stay - and activities - things to do. By builing a
private database of possible locations, it is easier to either make holiday plans or share tips with
friends and family.

VKNT assists in sharing by allowing locations, by managing visibility of the related content. By setting
the visibility, you decide who can see your content.
- Public: everyone can see your content. Adviced for locations and activities
- Community: logged in users can see your content. Adviced for comments
- Family: only users marked as family can see your content. 

Lists are the way to make your plans more manageble. Make a list of locations that interest you. Only you
or your family can edit your list. Distances to the previous location are automatically calculated. 

## Installation
Install the application in your desired location:
$ git clone https://github.com/arnecoomans/camping.cmns.nl .

You should really run the application in a python virtual environment:
$ python -m venv ~/.venv/vknt
$ source ~/.venv/vknt/bin/activate

The Package requirements are listed in requirements.txt. 
(vknt) $ python -m pip install -r requirements.txt

Create a superuser:
Use a username, this way the superuser only has access to the admin login page and avoid using the superuser for regular use
(vknt) $ python manage.py createsuperuser



## WishList / Feature Request List
* Add description for location in list
* Add image to location
* Show locations nearby based on coördinates
* Complete Dashboard
  * Nicer views
  * Add location/tag/list shortcuts
* up / down on locations in list
* (re)calculate distances in list
* toggle show-distances per list to distinct between blog-post-like list or travel plans
* enhance location flashcard view
* ~~if no categories, build a list of default categories to make the site work:~~
  ~~home, camping, hotel, b&b, Chambre D'Hôtes, Safaritent/glamping, Gite~~
  ~~activity: city, village, zoo, theme-park, museum, park, beach,  swimmingpool, sight-to-see,~~
* Better difference between locations and activities
* Edit function in list items
* ~~create new list and add location feature (redirect to addtolist after create list)~~
* ~~location form: add chain and add to location~~
* ~~location form: add tag and add to location (create tag)~~
* ~~mark location visibility in locations list when visibility is private or family~~
* order by distance from NL
* Move feature request list to Github 
  

## Known bugs [production stopping]
* ~~When a tag is a parent, but also used as tag, the locations do not show. Should update if-changed condition~~
* ~~add location to a list doesn't work when it is the first location~~
* ~~If there is no list available, it still shows dropdown and add to list button in location view~~, should link to "create new list"
* ~~home is not yet marked as "family" visibility, while it should~~
* ~~Check for permissions when showing an object~~
  * ~~view location~~
  * ~~Lists~~
* ~~Als gebruiker nog geen profiel heeft, maak profiel aan bij bezoeken /profile~~
* When adding a location - example Domaine Sante Marie - that is not found, it throws an error
* add tag doesnt work? -> rework permissions in forms
* add location doesnt work?
* add list doesnt work?
* css is not fully loading?

## Knwon bugs [to be solved]
* some translations are missing
