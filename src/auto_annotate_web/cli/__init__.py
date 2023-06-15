# SPDX-FileCopyrightText: 2023-present Danny Kim <imbird0312@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
import os
from pathlib import Path

import click
from loguru import logger

from auto_annotate_web.__about__ import __version__
from auto_annotate_web.app import __file__ as app


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="auto-annotate-web")
def auto_annotate_web():
    os.chdir(Path(app).parent)
    logger.info("Launch auto-annotate-web..!")
    os.system("uvicorn app:app --port=8123 --host=0.0.0.0")
    logger.info("Program end")
