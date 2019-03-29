# Changelog



## v1.0.0

- Build(project): Add docker-compose, change to env vars, documentation.
  [Ricardo Santos Diaz]
- Test(project): Add tests for engine, and api endpoints. [Ricardo
  Santos Diaz]
- Feat(project): Add the game engine and the ai. Add the endpoints.
  [Ricardo Santos Diaz]

  This is a huge update, first, all the endpoints are working as expected and specified. Regarding the game engine, or just the game rules, the engine module contains all of its elements.
- Feat(handlers): change handlers structure to be reusable, added
  decorators to validate. [Ricardo Santos Diaz]
- Feat(project): add handlers for users and games with get and post.
  [Ricardo Santos Diaz]
- Feat(project): add persistence layer with user and games object.
  [Ricardo Santos Diaz]

  There is currently an ODM helping with the persistence process. This ODM is umongo running on top of motor driver for mongo async operations. Based on these, two main classes were created: USer and Games. It was also added support to different configurations through environment variables.
- Build(project): Add the project initial dependencies and structure.
  [Ricardo Santos Diaz]


