# SPDX-FileCopyrightText: 2023-present Danny Kim <imbird0312@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
from auto_annotate_web.core.check import check

check()

from auto_annotate_web.annotator import annotate  # noqa
from auto_annotate_web.poly2bbox import p2b  # noqa

__all__ = "annotate", "p2b"
