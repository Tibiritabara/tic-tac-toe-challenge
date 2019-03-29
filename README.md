# Tic Tac Toe

## Tech behind
This project was built using mongodb for the data storage and tornado web is the main framework. In order 
to take advantage of the async nature of the framework, umongo is being used on top of motor for mongo.

## REST API DOCUMENTATION

We support three elements that are going to be stored: Users, Games, and GameMoves.

### Users
A user is a player of our tool. This is how a user looks in the database:
```json
{
    "_id" : ObjectId("5c9d5702e3872b02c94ecdb0"),
    "email" : "test@test.de",
    "username" : "usertest",
    "created_at" : ISODate("2019-03-29T00:21:29.287Z"),
    "victories" : 0
}
```

In order to manipulate users we have the next set of endpoints:

#### POST /api/users
```json

{
	"username": "test",
	"email": "test@test.de"
}
```
There are two main attributes, email and username, which are unique.


#### PUT /api/users/{user_id}
```json
{
	"email": "test@test.de"
}
```
The user_id is the mongo_id of the user when stored. Any of field can be modified by just sending 
the updated fields in the json body of the request

#### GET /api/users
Retrieves the full list of users stored.

#### GET /api/users/{user_id}
The user_id as explained before, is the object_id of the database entry


#### DELETE /api/users/{user_id}
It is a user hard delete. Soft delete will be for a later improvement.

### Games
A game is an object represented by a board, a set of players and a state. Each move on this board
will be stored in the GameMove collection, being able then to trace the user behavior on the game.
A game has a status, which might be: `created`, `in_progress`, `tie` or `finished`. Each of these states
will be updated accordingly to the game progress. 

A game entry will look like this in the database:
```json
{
    "_id" : ObjectId("5c9d59d3e3872b091268fa1b"),
    "players" : [ 
        ObjectId("5c9d59cfe3872b091268fa19"), 
        ObjectId("5c9d59d1e3872b091268fa1a")
    ],
    "status" : "created",
    "board" : [ 
        [ 
            "", 
            "", 
            ""
        ], 
        [ 
            "", 
            "", 
            ""
        ], 
        [ 
            "", 
            "", 
            ""
        ]
    ],
    "multiplayer" : true
}
```
The board is a 3 by 3 grid, that is represented by a matrix on the board field of the database entry
```
[["", "", ""],
 ["", "", ""],
 ["", "", ""]]
```
This should be the visual representation of the board. We have two available markers `X` or `O` and each cell 
of the grid will be replaced with those values when the game starts moving forward.

#### POST /api/games
```json
{
 "players": [
    "5c9d51d5e3872b71421ae42c",
    "5c9d50f5e3872b6fb001ae77"
  ]
}
```
This will create a new game board. The game will be multiplayer or single player depending on the amount of players sent
on the json body. A player is a mongo_id.

### GET /api/games
Retrieve the full list of games stored


### GET /api/games/{game_id}
game_id is the mongo_od of the database entry. When calling this endpoint it will return the current state
of the requested game.

### GameMoves
A game move is an object that describes the next requested move by the user. This move will be stored on the database
to give transparency and a visible trace on how was the game progress, and this object will be processed on our engine
in order to move forward on the game. When is a single player game, whenever a user creates a move, the AI will move 
immediately.

This is how a GameMove object look on the database
```json
{
    "_id" : ObjectId("5c9d5c30e3872b0da34d3e7d"),
    "symbol" : "X",
    "player" : ObjectId("5c9d5c2ae3872b0da34d3e7a"),
    "cell" : {
        "row" : 0,
        "column" : 1
    },
    "created_at" : ISODate("2019-03-29T00:43:35.053Z"),
    "game" : ObjectId("5c9d5c2de3872b0da34d3e7c")
}
```
In order to trigger and manage moves we have the next endpoints:

#### POST /api/games/{game_id}
When posting to this url, while using the game_id which is the mongo generated id, it will then trigger a game
move based on the next json body:
```json
{
	"player": ObjectId("5c9d5c2ae3872b0da34d3e7a"),
	"symbol": "X",
	"cell": {
		"row": 0,
		"column": 1
	}
}
```
Where row and column are the coordinates of the cell on the grid where the marker is going to be placed. Almost everything
is validated, so the game can flow without issues. The symbol is the selected marker by the user. The same user cannot play
twice or the next user cannot use the same marker as the user before him.


#### GET /api/games/{game_id}/moves
This endpoint return the full list of moves for the given game_id.

## How to build
The project is using docker and docker-compose in order to be able to work on it locally.

It is enough with doing 
```
docker-compose up -d --build
```
And you will be able to access the application through `http://localhost:8000`

If you want to run the project locally with all its dependencies please follow the next steps:

* Install Pipenv if you don't have it already ([download here](https://pipenv.readthedocs.io/en/latest/)): $`pip install --user pipenv`
* Install mongodb locally or run it in a docker container.
* then run `pipenv install` on the project folder. This will create a virtual environment with all 
of the dependencies inside.
* Execute `cp .env.dist .env` to ensure the environment variables are loaded.
* To run the server just execute `pipenv run python main.py`. This will run the project on the port 8000.

Now in order to run the tests please run:
* Run `PIPENV_DOTENV_LOCATION=.env.test pipenv run python unittest app/tests/tests.py` in order to override
the .env file and use the testing configuration

## Final words
The code is completely documented and the tests have a 90+% coverage. There are lots of improvements that 
can be made, starting with logging.

Im thankful for the opportunity and I hope this project gives you a better understanding of my 
skills and how do I like to design software.
