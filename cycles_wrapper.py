#!/usr/bin/env python3
"""Cycles Executor."""

import argparse
import csv
import logging
import os
import shutil
import subprocess
import sys
from string import Template

log = logging.getLogger()


def _generate_inputs(
        prefix,
        start_year,
        end_year,
        baseline,
        crop,
        start_planting_date,
        end_planting_date,
        fertilizer_rate,
        weed_fraction,
        forcing,
        weather_file,
        reinit_file,
        crop_file,
        soil_file,
        **kwargs):

    ctrl_file = "cycles-run.ctrl"
    op_file = "cycles-run.operation"

    # process CTRL file
    with open("template.ctrl") as t_ctrl_file:
        src = Template(t_ctrl_file.read())
        ctrl_data = {
            "start_year": start_year,
            "end_year": end_year,
            "rotation_size": 1,
            "crop_file": crop_file,
            "operation_file": op_file,
            "soil_file": soil_file,
            "weather_file": weather_file,
            "reinit": 0 if baseline == "True" else 1,
        }
        result = src.substitute(ctrl_data)
        with open("./input/" + ctrl_file, "w") as f:
            f.write(result)

    # process Operation file
    operation_contents = ""
    with open("template.operation") as t_op_file:
        src = Template(t_op_file.read())
        op_data = {
            "year_count": 1,
            "crop_name": crop,
            "fertilization_date": int(start_planting_date) - 10,
            "fertilization_rate": fertilizer_rate,
            "start_planting_date": start_planting_date,
            "end_planting_date": end_planting_date,
            "tillage_date": int(start_planting_date) + 20,
        }
        result = src.substitute(op_data)
        operation_contents += result + "\n"

        # handling weeds
        if float(weed_fraction) > 0:
            with open("template-weed.operation") as t_wd_file:
                wd_src = Template(t_wd_file.read())
                wd_data = {
                    "year_count": 1,
                    "weed_planting_date": int(start_planting_date) + 7,
                    "weed_fraction": weed_fraction
                }
                wd_result = wd_src.substitute(wd_data)
                operation_contents += wd_result + "\n"

    # writing operations file
    with open("./input/" + op_file, "w") as f:
        f.write(operation_contents)


def _launch(prefix, baseline, **kwargs):
    #cmd = "Cycles -s -l 1 cycles-run" 
    if baseline:
        cmd = "Cycles -s -l 1 cycles-run"
    else:
        cmd = "Cycles cycles-run"
    print(cmd)
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        print("Status : FAIL", exc.returncode, exc.output)
        exit(1)
    else:
        print("Output: \n{}\n".format(output))