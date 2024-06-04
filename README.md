# Social_Networking_Application
#Execute inside postgresql to create database:
---------------------------------------------------------------------------------
CREATE DATABASE social_networking;
CREATE USER social_networkinguser WITH PASSWORD 'password';
ALTER ROLE social_networkinguser SET client_encoding TO 'utf8';
ALTER DATABASE social_networking SET timezone TO 'Asia/Kolkata';
ALTER ROLE social_networkinguser SET default_transaction_isolation TO 'read committed';
ALTER ROLE social_networkinguser SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE social_networking TO social_networkinguser;
\c social_networking
GRANT ALL PRIVILEGES ON SCHEMA public TO social_networkinguser;

#Create virtual environment and activate it:
---------------------------------------------------------------------------------
python3 -m venv virtual-env

source virtual-env/bin/activate

pip install -r requirements.txt

#Create django project:
---------------------------------------------------------------------------------
django-admin startproject social_networking

#Create django app:
---------------------------------------------------------------------------------
python manage.py startapp accounts

---------------------------------------------------------------------------------

for x in accounts; do rm -rf $x/migrations; mkdir $x/migrations; touch $x/migrations/__init__.py; done

python manage.py makemigrations

python manage.py migrate

python manage.py create_debug_user

python manage.py runserver

---------------------------------------------------------------------------------
