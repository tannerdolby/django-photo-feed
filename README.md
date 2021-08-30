# Django Interactive Photo Feed
A simple photography feed application I built to practice using Django. The home page is a responsive CSS grid representing the feed of images being rendered from the `main_feed` collection stored in the SQLite database. The project only consists of a single app, `feed`.

Users may login or create an account if not registered and may click on images from the main feed to see more details about an image. Users have the option to "like" an image, adding it to their profile's personal liked collection. A running poll of most liked images can be found on the leaderboard page. Admin (superusers) users can access the bundled admin dashboard for performing CRUD operations.

## Local setup
1. Get the code on your computer - Fork this repo and clone it
2. Perform a migration `python3 manage.py migrate`
3. Make migrations `python3 manage.py makemigrations`
4. Start dev server `python3 manage.py runserver`

## Database Models
I created two data models `Collection` and `Image` aside from the built-in `User` model. The `Image` model has two Foreign keys, `collection` and `user`. This relationship allows a collection to be related to multiple images and for images to be within many different collections. I use this to keep track of each `User` objects "liked" images to display on profile pages. A unique collection, ie `{name}_{id}` is created for new users when they like their first photo or access the profile for the first time. 

This allows me to simply add images to that associated `collection.image_set` for a user after its created (if it doesn't already exist), and increment the `votes` counter for the image with that `id` to ensure the leaderboard updates with the updated database records.

Each user can have a relationship with a `Collection` (or many) and multiple different `Image` objects. Allowing for quick tracking of associated records.

## Resources
[Django docs](https://docs.djangoproject.com/en/3.2/)