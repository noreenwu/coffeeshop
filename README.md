# Project: Coffee Shop Authentication
# Noreen Wu
# December 2019


## Introduction

This Coffee Shop application allows any visitor to view the drinks menu,
baristas to view the drinks menu and the recipes for the drinks, and
shop managers to view the menu and the recipes, and also make changes to the recipes,
to add new drinks and to delete drinks from the menu.

The access control for these functions was implemented in Flask; the users,
their roles and their permissions are defined at auth0.com, which issues
jwt's with appropriate permissions on successful login.

Most endpoints require specific permissions; users who authenticate with these
defined permissions are allowed access to the endpoints.


## Running the Application

# Back-end

It is assumed that the following technologies are already available on your platform:
Python 3.7, pip and node; also Postman.

Download the repository at https://github.com/noreenwu/coffeeshop and cd into the
backend directory.

Set up your [python virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/), 
and then obtain the dependencies by running:

    pip install -r requirements.txt

The sqlite database is empty to begin with, so if you'd like to pre-load a couple
of drinks, then cd into backend/src/database to run:

    python loaddb.py


Then, from backend/src start up the backend server:

    export FLASK_APP=api.py
    export FLASK_ENV=development
    flask run

To verify that the backend is working, go to http://127.0.0.1:5000 in your browser.


# Postman

The endpoints may be tested by running Postman on the collection udacity-fsnd-udaspicelatte.


# Front-end

From the front-end folder (/frontend), use npm to install the dependencies:

    npm install

Then start the front-end service:

    ionic serve

The front-end can be accessed at http://localhost:8100


## Auth0, Roles and Permissions

The authentication for this application is made possible with the help of auth0.com.
Two accounts have been created at the tenant domain wudev.auth0.com: noreenwu@gmail.com
and noreen@wufried.com.

Two roles, Barista and Manager have been created. The Barista role is able to
perform the action "get:drinks-detail," which allows any user with this role
to see recipes for all listed drinks, but not make any changes to them.

The Manager role is able to "get:drinks-detail" (view drink recipes), "post:drinks"
(create new drinks), "patch:drinks" (modify existing drinks), and "delete:drinks"
(delete drinks).

noreenwu@gmail.com was given Manager privileges while noreen@wufried.com
was given Barist privileges.

Viewing just the list of drinks with associated graphic does not require any
special permissions. This is the default menu view for anyone viewing the site with
no credentials.


## Endpoint Library

GET /drinks

    Does not require credentials. 
    Returns a drinks array. Each drink contains an id, recipe and title.
    Each recipe includes a color (but does not identify ingredient name)
    and the number of parts included in the drink.

    {
    "drinks": [
        {
        "id": 2,
        "recipe": [
            {
            "color": "yellow",
            "parts": 1
            },
            {
            "color": "blue",
            "parts": 3
            },
            {
            "color": "lightgrey",
            "parts": 1
            }
        ],
        "title": "Lemonade I"
        },
        {
        "id": 3,
        "recipe": [
            {
            "color": "purple",
            "parts": 1
            },
            {
            "color": "red",
            "parts": 1
            },
            {
            "color": "yellow",
            "parts": 1
            }
        ],
        "title": "acai smoothie"
        },
        {
        "id": 4,
        "recipe": [
            {
            "color": "red",
            "parts": 1
            },
            {
            "color": "yellow",
            "parts": 1
            },
            {
            "color": "white",
            "parts": 1
            }
        ],
        "title": "strawberry smoothie"
        },
        {
        "id": 5,
        "recipe": [
            {
            "color": "lightgrey",
            "parts": 3
            },
            {
            "color": "blue",
            "parts": 1
            },
            {
            "color": "yellow",
            "parts": 1
            }
        ],
        "title": "Fancy Lemonade"
        }
    ],
    "success": true
    }

GET /drinks-detail

    Requires the permission 'get:drinks-detail,' which both the Barista
    and Manager roles have. 
    Returns a drinks array. Each drink contains an id, recipe and title.
    Each recipe includes name of ingredient, color and proportion (number of parts)
    in recipe.

    {
    "drinks": [
        {
        "id": 2,
        "recipe": [
            {
            "color": "yellow",
            "name": "lemon juice",
            "parts": 1
            },
            {
            "color": "blue",
            "name": "water",
            "parts": 3
            },
            {
            "color": "lightgrey",
            "name": "sugar",
            "parts": 1
            }
        ],
        "title": "Lemonade I"
        },
        {
        "id": 3,
        "recipe": [
            {
            "color": "purple",
            "name": "acai",
            "parts": 1
            },
            {
            "color": "red",
            "name": "stawberry",
            "parts": 1
            },
            {
            "color": "yellow",
            "name": "banana",
            "parts": 1
            }
        ],
        "title": "acai smoothie"
        },
        {
        "id": 4,
        "recipe": [
            {
            "color": "red",
            "name": "strawberries",
            "parts": 1
            },
            {
            "color": "yellow",
            "name": "banana",
            "parts": 1
            },
            {
            "color": "white",
            "name": "milk",
            "parts": 1
            }
        ],
        "title": "strawberry smoothie"
        },
        {
        "id": 5,
        "recipe": [
            {
            "color": "lightgrey",
            "name": "Seltzer",
            "parts": 3
            },
            {
            "color": "blue",
            "name": "sugar",
            "parts": 1
            },
            {
            "color": "yellow",
            "name": "lemon",
            "parts": 1
            }
        ],
        "title": "Fancy Lemonade"
        }
    ],
    "success": true
    }


POST /drinks

    Requires the permission 'post:drinks,' which only the Manager possesses
    at this time. This allows the manager to add new drinks to the menu.
    A new drink must contain for each ingredient a name, color and number
    of parts.

    passed in the body portion of the request:
    {
        "title": "Fancy Lemonade",
        "recipe": [{
            "name": "Seltzer",
            "color": "clear",
            "parts": 3
        }, {
            "name": "sugar",
            "color": "blue",
            "parts": 1
        }, {
            "name": "lemon",
            "color": "yellow",
            "parts": 1
        }
        ]
    }

    received as the result of a successful POST request (the new drink and success value):

    {
    "drinks": [
        {
        "id": 3,
        "recipe": [
            {
            "color": "clear",
            "name": "Seltzer",
            "parts": 3
            },
            {
            "color": "blue",
            "name": "sugar",
            "parts": 1
            },
            {
            "color": "yellow",
            "name": "lemon",
            "parts": 1
            }
        ],
        "title": "Fancy Lemonade"
        }
    ],
    "success": true
    }    

PATCH /drinks/int:id

    Requires the permission 'patch:drinks,' which only the manager has.
    This allows the manager to make changes to a drink on the menu.

    The drink id is specified in the url. Data passed in the body portion of the request:
    {
        "title": "NY root beer float",
        "recipe": [
        {
            "color": "tan",
            "name": "Seltzer",
            "parts": 1
        }] 
    }

    received as the result of a successful PATCH:
    {
    "drinks": [
        {
        "id": 1,
        "recipe": [
            {
            "color": "tan",
            "name": "Seltzer",
            "parts": 1
            }
        ],
        "title": "NY root beer float"
        }
    ],
    "success": true
    }


DELETE /drinks/int:id

    Requires the permission 'delete:drinks,' which only the manager has.
    This allows the manager to delete drinks from the menu.

    The drink id is specified in the url. No data needs to be passed in.
    
    The endpoint returns the id that was deleted and a success value:

    {
    "delete": 1,
    "success": true
    }    



## Front-end

The Ionic front-end is configured to work with the backend and authentication
pieces in the file frontend/src/environments/environment.ts


Aside from these configuration settings, edits were made to disable edit
function buttons inside the recipe edit screens; baristas may view
recipes but they are unable to save changes, so it is misleading to
suggest that they can.

## Authors

Ionic front-end, partial Flask server, SQLAlchemy module, sqlite database
schema by Udacity FSND

Minor changes to Ionic front-end, front-end configuration to coordinate
with Flask backend, completion of Flask server endpoints, authentication and
authorization of endpoints using Flask and Auth0 by Noreen Wu


## Acknowledgements

I would like to thank my family for allowing me to create Uda-Spice Latte Cafe
drinks on Christmas Eve Eve, instead of making a flourless chocolate cake
like I was supposed to.





