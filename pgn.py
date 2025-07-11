from csv import DictReader
import chess
import chess.pgn

def generate_pgn(reader: DictReader[str]) -> str:
    return "\n\n".join(
        str(chapter(puzzle, first=(i == 0))) for i, puzzle in enumerate(reader)
    )

def chapter(puzzle, first: bool = False) -> chess.pgn.Game:
    game = chess.pgn.Game()
    print(puzzle)
    game.headers["Event"] = puzzle["event"]
    game.headers["White"] = puzzle["white"]
    game.headers["Black"] = puzzle["black"]
    game.headers["Result"] = "*"
    game.headers["WhiteElo"] = puzzle["white elo"]
    game.headers["BlackElo"] = puzzle["black elo"]
    game.headers["WhiteTitle"] = puzzle["white title"]
    game.headers["BlackTitle"] = puzzle["black title"]
    game.headers["Variant"] = "From Position"
    game.headers["FEN"] = puzzle["fen"]
    game.headers["SetUp"] = "1"
    game.headers["ChapterMode"] = "gamebook"

    moves = puzzle["moves"].split(",")

    node = game.add_variation(chess.Move.from_uci(moves[0]))

    if first:
        node.comment = f"All these puzzles were generated from games played in the {puzzle['event']}."

    for move in moves[1:]:
        node = node.add_variation(chess.Move.from_uci(move))
    
    return game
