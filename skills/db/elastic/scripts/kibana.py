"""Kibana saved objects — dashboard, visualization, data-view, and case commands."""

from __future__ import annotations

import argparse

from case import KibanaCase
from dashboard import KibanaDashboard
from data_view import KibanaDataView
from visualization import KibanaVisualization


class Kibana:
    @staticmethod
    def register(sub: argparse._SubParsersAction) -> None:
        p = sub.add_parser("kibana", help="Kibana saved objects and cases")
        cmds = p.add_subparsers(required=True)
        KibanaDashboard.register_cmds(cmds)
        KibanaVisualization.register_cmds(cmds)
        KibanaDataView.register_cmds(cmds)
        KibanaCase.register_cmds(cmds)
