# Changelog

## V1.1.0

- Style(engine): Pylint corrections. [Ricardo Santos Diaz]
- Fix(test): fix to unit test documentation on readme. [Ricardo Santos
  Diaz]
- Feat(game): Add support for multidimensional boards. [Ricardo Santos
  Diaz]
- Docs(project): Minor grammar fixes. [Ricardo Santos Diaz]
- Feat(bots): better support for strategy extension for next move
  calculation. [Ricardo Santos Diaz]
- Fix(games): Add back the retrieve for a single game method. [Ricardo
  Santos Diaz]
- Ci(prooject): Gitlab_ci implementation. [Ricardo Santos Diaz]
- Docs(project): Add the changelog. [Ricardo Santos Diaz]
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
