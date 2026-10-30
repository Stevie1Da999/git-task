# Cape Market - Django eCommerce Application Part 1

This project was adapted from the supplied bulletin board starter project into an eCommerce web app.

## Main features
- Buyer and vendor registration/login
- Vendor store and product CRUD
- Buyer session cart and checkout
- Stock reduction and saved orders
- Invoice email through Django's email backend
- Verified/unverified product reviews
- Password reset by time-limited email link
- Django groups, permissions and ownership checks
- SQLite relational database for easy local assessment

## Run the project
1. Create/activate a virtual environment.
2. Install Django: `python -m pip install django`
3. Run `python manage.py migrate`
4. Optional admin: `python manage.py createsuperuser`
5. Start: `python manage.py runserver`

Emails use Django's console backend for assessment, so invoice and password-reset emails appear in the terminal instead of needing real email credentials.
