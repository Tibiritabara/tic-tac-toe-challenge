"""
The collection of classes and methods to actually play the game
"""
import asyncio
import random
from tornado.web import HTTPError
from app.models import Game, GameMove, User


class GameEngine:
    """
    This class handles how the winners are calculated and the rule
    enforcing of the game
    """
    async def execute_move(self, game: Game, move: GameMove) -> Game:
        """
        Execute a move specified by the user considering the restrictions
        and the game winning calculation.
        :param Game game:
        :param GameMove move:
        :return Game:
        """
        user = await User.find_by_id(move.player.pk.__str__())
        move.game = game.pk
        if not await self.__validate_player_move(game, move):
            raise HTTPError(
                412,
                'Invalid move'
            )
        game.board[move.cell.get('row')][move.cell.get('column')] = move.symbol
        game.status = Game.STATUS_IN_PROGRESS
        return await self.validate_board(game, move, user)

    async def __validate_player_move(self, game: Game, move: GameMove) -> bool:
        """
        The player move should be allowed depending on a set of rules:
        - It is not the same player as the previous move
        - The player is using the alternate symbol (X or O)
        - The coordinates of the cell exist
        - The selected cell is empty
        :param Game game:
        :param GameMove move:
        :return bool:
        """
        if move.cell.get('row') > 2 or  move.cell.get('column') > 2:
            return False

        if game.board[move.cell.get('row')][move.cell.get('column')] != '':
            return False

        prev_move = await GameMove.find_one(
            {'game': game.pk},
            sort=[("_id", -1)]
        )
        if prev_move is None:
            return True

        if prev_move.player == move.player:
            raise HTTPError(
                412,
                'User already played its turn'
            )

        if prev_move.symbol == move.symbol:
            raise HTTPError(
                412,
                'Player is not allowed to use that symbol'
            )
        return True

    async def __validate_right_diagonal(self, game: Game) -> bool:
        """
        Validate if there is a winner by checking the diagonal coming from left
        to right
        :param Game game:
        :return bool:
        """
        win = True
        prev = None
        for i in range(0, 3):
            value = game.board[i][i]
            if value == '' or (prev is not None and value != prev):
                win = False
                break
            prev = value
        return win

    async def __validate_left_diagonal(self, game: Game) -> bool:
        """
        Validate if there is a winner by checking the diagonal coming from right
        to left
        :param Game game:
        :return bool:
        """
        win = True
        prev = None
        for i in range(0, 3):
            value = game.board[i][2-i]
            if value == '' or (prev is not None and value != prev):
                win = False
                break
            prev = value
        return win

    async def __validate_rows(self, game: Game) -> bool:
        """
        Validate if there is a winner by checking each row
        :param Game game:
        :return bool:
        """
        win = True
        for i in range(0, 3):
            prev = None
            win = True
            for j in range(0, 3):
                value = game.board[i][j]
                if value == '' or (prev is not None and value != prev):
                    win = False
                    break
                prev = value
            if win:
                break
        return win

    async def __validate_columns(self, game: Game) -> bool:
        """
        Validate if there is a winner by checking each column
        :param Game game:
        :return bool:
        """
        win = True
        for i in range(0, 3):
            prev = None
            win = True
            for j in range(0, 3):
                value = game.board[j][i]
                if value == '' or (prev is not None and value != prev):
                    win = False
                    break
                prev = value
            if win:
                break
        return win

    async def __validate_tie(self, game: Game) -> bool:
        """
        Validate if there is a tie
        :param Game game:
        :return bool:
        """
        tie = True
        for i in range(0, 3):
            for j in range(0, 3):
                value = game.board[j][i]
                if value == '':
                    tie = False
                    break
        return tie

    async def validate_board(self, game: Game, move: GameMove, user: User) -> Game:
        """
        Validate if the board to check if there are winners or if
        there is a tie.
        :param Game game:
        :param GameMove move:
        :param User user:
        :return Game:
        """
        win_validations = await asyncio.gather(
            self.__validate_right_diagonal(game),
            self.__validate_left_diagonal(game),
            self.__validate_columns(game),
            self.__validate_rows(game),
        )
        tasks = [asyncio.create_task(move.commit())]
        if True in win_validations:
            game.status = Game.STATUS_FINISHED
            game.winner = move.player
            user.victories += 1
            tasks.append(asyncio.create_task(
                user.commit()
            ))
        elif await self.__validate_tie(game):
            game.status = Game.STATUS_TIE

        tasks.append(asyncio.create_task(game.commit()))
        await asyncio.gather(*tasks)
        return game

    async def ai_move(self, game: Game, prev_move: GameMove) -> GameMove:
        """
        Return a move made by the AI. This can be vastly improved,
        right now is just a random available cell.
        """
        available_cells = []
        for i in range(0, 3):
            for j in range(0, 3):
                if game.board[i][j] == '':
                    available_cells.append((i, j))

        user = await User.find_one({'username': 'tictactoeai'})
        symbol = list(filter(
            lambda x: x != prev_move.symbol,
            GameMove.SYMBOLS,
        ))[0]
        cell = random.choice(available_cells)
        data = {
            'symbol': symbol,
            'player': user.pk.__str__(),
            'cell': {
                'row': cell[0],
                'column': cell[1],
            }
        }
        return GameMove(**data)
