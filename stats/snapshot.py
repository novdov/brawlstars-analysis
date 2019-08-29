from pathlib import PosixPath
from typing import List, Mapping, Optional, Union, Tuple

import brawlstats
from tqdm import tqdm

import stats.utils as utils


class BrawlStatsLogger:
    TARGET_MATCHES = {"gemGrab", "heist", "bounty", "brawlBall", "siege"}

    def __init__(self, token_path: Union[PosixPath, str], tag: str):
        self.client = brawlstats.Client(utils.read_file(token_path))
        self.tag = tag

        self.cache = set()

    def get_battle_logs(self, tag: str) -> List[Mapping]:
        battle_logs = self.client.get_battle_logs(tag)
        return [log.raw_data for log in battle_logs][0]

    def parse_battle_logs_all_user(self, init_tag: str) -> List[Mapping]:
        visited = {hash(init_tag)}
        first_parsed_logs = self.parse_battle_logs(init_tag)

        all_logs = []
        all_logs.extend(first_parsed_logs)

        for log in tqdm(first_parsed_logs):
            tag = log["tag"][1:]
            tag_hash = hash(tag)
            if tag_hash not in visited:
                visited.add(tag_hash)
                all_logs.extend(self.parse_battle_logs(tag))
        return all_logs

    def parse_battle_logs(self, tag: str) -> List[Mapping]:
        parsed_logs = []
        raw_logs = self.get_battle_logs(tag)
        for log in raw_logs:
            parsed_log_hash_val = self.parse_single_battle_log(log, tag)
            if parsed_log_hash_val is not None:
                parsed_log, hash_val = parsed_log_hash_val
                if hash_val not in self.cache:
                    self.cache.add(hash_val)
                    parsed_logs.extend(parsed_log)
        return parsed_logs

    def parse_single_battle_log(
            self,
            battle_log: Mapping,
            tag: str
    ) -> Optional[Tuple[List[Mapping], int]]:
        """Parse single battle log."""

        match_cond = battle_log["battle"]["mode"] in self.TARGET_MATCHES
        result_cond = "result" in battle_log["battle"]
        type_cond = "type" in battle_log["battle"] and battle_log["battle"]["type"] == "ranked"

        if not all([match_cond, result_cond, type_cond]):
            return None

        hash_val = 0
        parsed_log = []
        battle_info = {
            "mode": battle_log["battle"]["mode"],
            "result": battle_log["battle"]["result"],
            "duration": battle_log["battle"]["duration"],
            "map": battle_log["event"]["map"],
            "battle_time": battle_log["battleTime"],
        }

        star_player = battle_log["battle"]["starPlayer"]["tag"]
        teams: List[List[Mapping]] = battle_log["battle"]["teams"]

        hash_val += hash(battle_info["battle_time"])
        for team in teams:
            for player in team:
                hash_val += hash(player["tag"][1:])

        for team in teams:

            players = [log["tag"][1:] for log in team]
            side = 1 if tag in players else 0

            for player in team:
                team_info = {
                    "brawler": player["brawler"]["name"],
                    "brawler_power": player["brawler"]["power"],
                    "brawler_trophies": player["brawler"]["trophies"],
                    "name": player["name"],
                    "tag": player["tag"],
                    "team": side,
                    "star_player": 1 if player["tag"] == star_player else 0,
                    "hash": hash_val
                }
                parsed_log.append({**battle_info, **team_info})

        return parsed_log, hash_val
