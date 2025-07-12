import csv
from datetime import datetime
from typing import Any, Dict
from zulip_bots.lib import BotHandler
import os
import requests
import subprocess
import time
import zulip
from config import last_commit, version, zuliprc
from pgn import generate_pgn


class PuzzlerHandler:
    def usage(self) -> str:
        commit_url = f"https://github.com/fitztrev/puzzler/{version()}"
        return f"""
Usage: `@puzzler <url to pgn>`
Version: [{version()}]({commit_url}) {last_commit()}
        """

    def handle_message(self, message: Dict[str, Any], bot_handler: BotHandler) -> None:
        print(message)

        args: list[str] = message["content"].split(" ")
        url = next((arg for arg in args if arg.startswith("http")), None)

        if not url:
            bot_handler.send_reply(message, self.usage())
            return

        client = zulip.Client(config_file=zuliprc())

        # acknowledge receipt of the message by adding a reaction
        self.add_reaction(client, message["id"], "puzzle")

        filename = f"puzzles_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        pgn = requests.get(url).text
        with open(f"{filename}.pgn", "w") as f:
            f.write(pgn)

        engine_path = os.getenv("ENGINE_PATH", "./engines/stockfish")
        result = subprocess.run(
            [
                "./bin/generator",
                "--threads",
                "6",
                "--verbose",
                "--file",
                f"{filename}.pgn",
                "--engine",
                engine_path,
            ],
            capture_output=True,
            text=True,
        )

        resp = bot_handler.send_reply(
            message,
            f"```spoiler script logs\n{result.stdout}\n{result.stderr}```",
        )
        print(resp)

        puzzle_count = 0

        csv_filename = f"{filename}.csv"
        if os.path.exists(csv_filename):
            with open(csv_filename, "r") as original:
                data = original.read()
                cols = [
                    "event",
                    "white",
                    "black",
                    "white title",
                    "black title",
                    "white elo",
                    "black elo",
                    "game id",
                    "fen",
                    "ply",
                    "moves",
                    "cp",
                    "generator",
                ]

                with open(csv_filename, "w") as modified:
                    modified.write(','.join(cols) + "\n")
                    modified.write(data)
                    puzzle_count = len(data.splitlines())
                    resp = bot_handler.send_reply(
                        message, f"{puzzle_count} puzzle{'s'[:puzzle_count^1]} found in that PGN"
                    )
                    print(resp)

                with open(csv_filename, "rb") as fp:
                    result = client.upload_file(fp)
                    resp = bot_handler.send_reply(
                        message, f":attachment: [CSV report]({result['uri']})"
                    )
                    print(resp)

                reader = csv.DictReader(open(csv_filename))
                study_pgn = generate_pgn(reader)
                with open(f"{filename}.pgn", "w") as fp:
                    fp.write(study_pgn)
                with open(f"{filename}.pgn", "rb") as fp:
                    result = client.upload_file(fp)
                    instructions = [
                        'Lichess > New Study',
                        'On "New chapter" dialog, "PGN" tab > "Choose File", choose this pgn file',
                        'Set "Analysis Mode" to "Interactive lesson"',
                        'Set "Orientation" to "Automatic"',
                        'Click "Create Chapter"',
                    ]
                    resp = bot_handler.send_reply(
                        message, f":attachment: [PGN puzzles]({result['uri']})\nTo create a puzzle pack:\n" + "\n".join(instructions)
                    )
                    print(resp)
        else:
            print(f"CSV file {csv_filename} not found, no puzzles generated.")

        self.add_reaction(client, message["id"], "check")


    def add_reaction(self, client: zulip.Client, message_id: int, emoji: str) -> None:
        time.sleep(1) # zulip api seems flaky about adding reactions to just-created messages
        client.add_reaction(
            {
                "message_id": message_id,
                "emoji_name": emoji,
            }
        )


handler_class = PuzzlerHandler
