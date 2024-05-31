# PARKTALK

## Description
Have you ever looked at a parking sign and not have a clue what it means? This project aims to solve that problem. This project is a social app for android devices where users will upload posts on parking signs and ask the community what the signs mean. You can ask for help or help others to gain points and climb a worldwide leaderboard.

## Setup
Here is how to setup the application.

### Backend
The "backend" directory contains the backend which is written in python. This directory can be opened and edited with any IDE. VSCode was used during development, so VSCode is recommended.

We use flask as our framework and an sqlite database. The database will start of being empty.

To start the backend, navigate to the backend directory, optionally create a virtual environment and then run the following command:

* pip install -r requirements.txt

This will install all the required packages used.
After installing, run the following command to start the backend:

* flask run

Now the backend should be active with an empty database.
If you want to add some placeholder users, run the following command:

* python3 dbLoader.py

This will create users, posts, comments and like differnet items randomly. Can be used to easily debug or experiment with the app.

### Frontend
The frontend will require an emulator or physical device to run. It is highly recommended to run this in Android Studio, which can also handle emulators. Refer to https://developer.android.com/studio for installation. 

The emulator "Pixel 3a" was used during development. Make sure API level is 34+. 

To run the frontend app, open the directory "frontend" in Android Studio as a project, and after gradle has finished syncing, launch the emulator and start the app by pressing the green "play" button in the top right.

## Testing
Simple testing with edge cases etc can be run by running the following command:

* python3 request.py

Ensure that the database is dropped before running this command, since otherwise it will fail due to users already existing.
We also use coverage with pytest on our requests. To test the coverage, run the following command:

* coverage run -m pytest coverageTest.py
* coverage report