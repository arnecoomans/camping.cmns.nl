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

