from datetime import datetime
from typing import Any, Dict
from zulip_bots.lib import BotHandler
import os
import requests
import subprocess
import time
import zulip
from config import last_commit, version, zuliprc


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

        bot_handler.send_reply(
            message,
            f"```spoiler script logs\n{result.stdout}\n{result.stderr}```",
        )

        puzzle_count = 0

        csv_filename = f"{filename}.csv"
        if os.path.exists(csv_filename):
            with open(csv_filename, "r") as original:
                data = original.read()
                puzzle_count = len(data.splitlines())
                first_line = "white,black,game id,fen,ply,moves,cp,generator"
                with open(csv_filename, "w") as modified:
                    modified.write(first_line + "\n")
                    modified.write(data)

                with open(csv_filename, "rb") as fp:
                    result = client.upload_file(fp)
                    bot_handler.send_reply(
                        message, f"[{os.path.basename(result['uri'])}]({result['uri']})"
                    )

        bot_handler.send_reply(
            message, f"{puzzle_count} puzzle{'s'[:puzzle_count^1]} found in that PGN"
        )
        self.add_reaction(client, message["id"], "check")

    def add_reaction(self, client: zulip.Client, message_id: int, emoji: str) -> None:
        # zulip api seems flaky about adding reactions to just-created messages
        time.sleep(1)
        client.add_reaction(
            {
                "message_id": message_id,
                "emoji_name": emoji,
            }
        )


handler_class = PuzzlerHandler
