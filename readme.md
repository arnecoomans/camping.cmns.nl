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

## More information
- Check out the GitHub https://github.com/arnecoomans/camping.cmns.nl
- Log your issues and/or feature requests in github issues
- Contact me at https://bsky.app/profile/arnecoomans.bsky.social


## Installation tips
Install the application in your desired location:

> $ git clone https://github.com/arnecoomans/camping.cmns.nl .

You should really run the application in a python virtual environment:

> $ python -m venv ~/.venv/vknt
> $ source ~/.venv/vknt/bin/activate


The Package requirements are listed in requirements.txt. 

> (vknt) $ python -m pip install -r requirements.txt

Create a settings.py file in /vknt/ based on the settings.example file. Make some required changes.
The changes required are marked in the example file. Start by configuring a SECRET_KEY and set the ALLOWED_HOSTS.
When running in production, make sure to set DEBUG to False.

> (vknt) $ cp vknt/settings.example vknt/settings.py


Run database migrations to ensure a database with the correct structure is available:

> (vknt) $ python manage.py migrate


Create a superuser:

> (vknt) $ python manage.py createsuperuser


Test the setup with the development server. This should run without issues. If any issues have appeared, they should show up.

> (vknt) $ python manage.py runserver


Stop the development server and set up a proper hosting environment. I reccomend using gunicorn with supervisord and nginx.
- https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04#testing-gunicorn-s-ability-to-serve-the-project


## About the Application

VKNT is a holiday location management system, collecting possible holiday locations and activities and storing these 
for when you make your holiday plans. It is always hard to remember what the name of that campground was you saw earlier.
Or where to write down that one tip a friend gave you. Let alone to remember why it sounded interesting. VKNT gives you 
a spot to drop your holiday destinations and helps you order them.

### Locations
The Location is the most important element of the tool. This is where you write down the name of the spot. Entering a
location is easy: you only really need the name. The address is automatically googled so it can be shown on the map. 
If you don't write down a website, a Google search is automatically stored. You do need to check what kind of location
you are storing, but that is something that I think you know. 

Once written down, you can start adding data: add categories that the site also offers, add tags to recognize locations
quickly, jolt down a comment why you liked the location. 

### Activities
Activities are not that different to Locations. Just that it is not a holiday destination on itself, but something to do.
Write down the museum you'd absolutely like to see, zoo's you've heard good stories of or villages you like. 
[@todo]I am working on making this information readily available to you in the location view[/@todo]

### Lists
One way to order this ever growing list of holiday destination is to make your own list. This can be a shortlist with 
candidates for the coming holiday, or even an itenary for your next trip. 
Distances to the last location in the list are automatically fetched, so this gives you an idea how the day would look like. 