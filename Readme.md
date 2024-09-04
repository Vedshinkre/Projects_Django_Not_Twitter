
## FameSocialNetwork Integration Project
This project is a Proof of Concept (POC) for integrating "Fame Profiles" into a social network, based on the ideas presented in the novel "Fameland" by Tom J. Petersson. The goal is to enhance social interactions by tracking users' skills and knowledge, and adjusting their ability to influence others based on their expertise. This project was developed as part of the Big Data Engineering course at Saarland University.

## Project Overview
# Fame Profiles
In the FameSocialNetwork, each user has a "fame profile" that records and tracks their skills. These profiles help determine the influence a user has within the network, based on their expertise in various topics. Positive or negative fame can affect a user's ability to interact with the network, particularly in posting content.

## Key Features
# Fame Integration: Users' posts are evaluated based on their fame profiles, and posts that fall within a user's negative expertise areas are not published.
# Fame Adjustment: The fame profile of a user is automatically adjusted when they post content with a negative truth rating.
# Expert and Bullshitter Lists: The system can generate lists of users recognized as experts or bullshitters in specific areas based on their fame profiles.
## Implemented Tasks
# Task 1: Modify api.submit_post
Behavior: Posts are only published if the user does not have negative fame in the related expertise area. The system also adjusts the user's fame based on the truth rating of the post.
# Task 2: Fame Adjustment on Post Submission
Fame Reduction: If a user posts content with a negative truth rating, their fame in the relevant area is reduced. If their fame cannot be lowered further, the user is banned from the platform.
# Task 3: Expert List API
API Endpoint: Implemented an API that returns a ranked list of users who are considered experts in specific areas.
# Task 4: Bullshitter List API
API Endpoint: Implemented an API that returns a ranked list of users who are recognized as bullshitters in specific areas.

## Preliminary

You need [pipenv](https://pipenv.pypa.io/en/latest/) to run the project. If you use our
Vagrant VM, please run the following command inside the VM:
```
pip install --user --break-system-packages pipenv
```
If you use our Docker container, please run the following command inside the container:
```
pip install --user pipenv
```

If you are using Windows as OS, you should use the PowerShell to install pipenv and
run the project.

## Installation

Install the project using pipenv in the directory where the `Pipfile` resides. The command

``` 
pipenv install
```

will create a virtual environment and install the required dependencies. Note that our Docker container only has
Python3.10 installed, however, you may also use this instead with the command
```
pipenv --python /usr/bin/python3 install
```
When using an IDE like PyCharm you want to make sure that that virtual environment is used for the project.

Then
```
pipenv shell
```
will activate that virtual environment.

After working on the project, the virtual environment can be deactivated again using the
```
exit
```
command.

## Unit Tests

To run the unit tests in the virtual environment, use the following command:

```
python manage.py test
```

Recall to disable the failing tests and enable them one by one to see the failing tests. 
Note that the tests use the fixture `database_dump.json`.

## Server

To run the server in the virtual environment, use the following command:
```
python manage.py runserver
```

If you are using our Vagrant VM or our Docker container, you need to explicitly specify the IP address and port:
```
python manage.py runserver 0.0.0.0:8000
```

In both cases, you can access the server in a browser of your choice under http://127.0.0.1:8000/.

## Models, Database, and Fake Data

Use the script
```
recreate_models_and_data.sh
```
to recreate the migrations, database, fake data and fixtures.
