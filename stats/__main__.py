import argparse
from pathlib import Path

import pandas as pd

import stats.utils as utils
from stats.snapshot import BrawlStatsLogger


def get_parser(_=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--token_path", type=str, help="path of API token")
    parser.add_argument("--output_dir", type=str, help="output directory")
    parser.add_argument("--tag", type=str, help="user tag")
    return parser


if __name__ == "__main__":
    args, _ = get_parser().parse_known_args()

    brawl_stats_logger = BrawlStatsLogger(Path(args.token_path).expanduser(), args.tag)
    parsed_logs = brawl_stats_logger.parse_battle_logs(args.tag)

    df_parsed_logs = pd.DataFrame(parsed_logs)
    df_parsed_logs.to_csv(
        Path(args.output_dir).expanduser().joinpath(f"log.{utils.get_datetime()}.csv"), index=False
    )

    all_logs = brawl_stats_logger.parse_battle_logs_all_user(args.tag)
    df_all_logs = pd.DataFrame(all_logs)
