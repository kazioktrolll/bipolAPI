"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""


from src.app import App
from src.scenes import GeoDesignScene
from src.backend.geo_design import GeometryGenerator
import logging
import argparse
import sys
from platformdirs import user_config_dir
from pathlib import Path


def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-console", default="WARNING",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level for console output")
    parser.add_argument("--log-file", default="DEBUG",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level for file output")
    args = parser.parse_args()
    return args


def setup_logging(console_level: str, file_level: str):
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Master level (lowest of all handlers)

    # --- Console handler ---
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(getattr(logging, console_level))
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s"))
    logger.addHandler(ch)

    # --- File handler ---
    logfile_path = Path(user_config_dir("GAVL")) / "logs.txt"
    logfile_path.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(logfile_path, mode="w", encoding="utf-8")
    fh.setLevel(getattr(logging, file_level))
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(fh)


def main():
    # --- parse arguments ---
    args = setup_args()
    # --- setup logging ---
    setup_logging(args.log_console, args.log_file)

    # --- run app ---
    logging.debug("Starting app...")
    app = App()
    logging.debug("App started.")
    logging.debug("Loading default geometry...")
    app.set_geometry(GeometryGenerator.default())
    logging.debug("Default geometry loaded.")
    logging.debug("Setting scene...")
    app.set_scene(GeoDesignScene(app))
    logging.debug("Scene set.")
    logging.debug("Starting main loop...")
    app.run()


if __name__ == '__main__':
    main()
