# LearningPortal

This project gets course questions from pdf and store it onto db.The online users can take up exam time bound on those course 

# Tech Stack 
Django 4.1, Postgres DB, HTML,CSS,Bootstrap 4

Default Django features used for authentication, admin interface and so on

# Deployment procedure 
1. Would need to have postgres db service uprunning 
2. need to make db connection changes on settings.py 
3. need to run command for making db changes if any "python manage.py makemigrations"
4. need to run command "python manage.py migrate"
5. need to run the server using "python manage.py runserver 80"
