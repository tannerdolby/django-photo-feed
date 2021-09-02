# Django Interactive Photo Feed
A simple photography feed application I built to practice using Django. The home page is a responsive CSS grid representing the feed of images being rendered from the `main_feed` collection stored in the SQLite database. The project only consists of a single app, `feed`.

Users may login or create an account if not registered and may click on images from the main feed to see more details about an image. Users have the option to "like" an image, adding it to their profile's personal liked collection. A running poll of most liked images can be found on the leaderboard page. Admin (superusers) users can access the bundled admin dashboard for performing CRUD operations.

## Uploading Images
To upload your own images, make sure your logged into an account with 'superuser' privelages or else the UI won't display in the template. After your logged in, click the 'profile' nav link and scroll down to see two forms: one for adding a single user uploaded (from users filesystem) image, and another for a handling user uploaded CSV files that contains title, src, alt columns for inserting multiple images at a time.

## Local setup
1. Get the code on your computer - Fork this repo and clone it
2. Perform a migration `python3 manage.py migrate`
3. Make migrations `python3 manage.py makemigrations`
4. Start dev server `python3 manage.py runserver`

## Database Models
I created two data models `Collection` and `Image` aside from the built-in `User` model. The `Image` model has two Foreign keys, `collection` and `user`. This relationship allows a Collection to be related to multiple images and for images to be related to many different collections. Using `ImageField` for the user uploaded images and `FileField` for the uploaded CSV files along with `ModelForm`.

I opted for this data model structure to keep track of each `User` records "liked" images by quickly querying all the records in that users associated collection for display on profile pages. A unique collection, ie `{name}_{id}` is created for new users when they like their first photo or access the profile for the first time and this is the collection that "liked" images from the 'main_feed' collection are added into. This allows for simply adding images into that users associated `collection.image_set` for a user after the collection is created (if it doesn't already exist), and then increment the `votes` counter for the image with that `id` to ensure the public leaderboard updates with the most recent database records.

Each user can have a relationship with a `Collection` (or many) and multiple different `Image` objects. Allowing for quick tracking of associated User/Image or Collection/Image records.

## Resources
[Django docs](https://docs.djangoproject.com/en/3.2/)