#! /usr/bin/env python3
desc = """
Simplify eicrecon run with a set of debug flags

    python3 debug_run.py input_file.edm4hep.root output_name_no_ext
    
Script should successfully run and create files:

    output_name_no_ext.edm4eic.root    # with output flat tree
    output_name_no_ext.ana.root        # with histograms and other things filled by monitoring plugins
    
One can add -n/--nevents file with the number of events to process    
"""

import io
from pprint import pprint
import os
import sys
import subprocess
from datetime import datetime
import argparse

def _print_path_env(env_str: str, title: str):
    tokens = env_str.split(":")
    lines = [f"   {token}" for token in tokens if token]
    print(title)
    pprint(lines)


if __name__ == "__main__":

    # Separate all parameters that starts with -P/-p from args
    parameter_args = []
    sys_argv = sys.argv.copy()
    for arg in sys_argv:
        if arg.startswith(("-P", "-p")):
            parameter_args.append(arg)
            sys.argv.remove(arg)

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('input_file', help="Input file name")
    parser.add_argument('output_base_name', help="Output files names (no file extensions here)")
    parser.add_argument('-n', '--nevents', default="10", help="Number of events to process")
    args = parser.parse_args()

    # Identify repository root
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    print(f"Repo root_dir: {root_dir}")

    # Identify executable to run
    executable = os.path.join(root_dir, "cmake-build-debug/eicrecon/src/utilities/eicrecon/eicrecon")
    print(f"Using executable:\n {executable}")
    print(f"File exists: {os.path.exists(executable)}")

    # Add compiled plugins to JANA_PLUGIN_PATH
    jana_plugin_path_env = os.environ.get("JANA_PLUGIN_PATH", "")
    plugin_dirs = [
        os.path.join(root_dir, "lib/EICrecon/plugins"),
        # os.path.join(root_dir, "cmake-build-debug/src/plugins/test_cdaq"),
        # os.path.join(root_dir, "cmake-build-debug/src/services/log"),
        # os.path.join(root_dir, "cmake-build-debug/src/services/root_output"),
    ]
    for plugin_dir in plugin_dirs:
        jana_plugin_path_env = plugin_dir + ":" + jana_plugin_path_env
    os.environ["JANA_PLUGIN_PATH"] = jana_plugin_path_env

    os.environ["LD_LIBRARY_PATH"] = "/home/romanov/eic/soft/irt/irt-v1.0.3/lib:"+os.environ.get("LD_LIBRARY_PATH", "")
    _print_path_env(jana_plugin_path_env, "Initial JANA_PLUGIN_PATH")

    run_command = [
        executable,
        f"-Pplugins=dump_flags",
        f"-Pdd4hep:xml_files=epic_brycecanyon.xml"
        f"-Pdump_flags:json={args.output_base_name}.flags.json",
        f"-Pjana:debug_plugin_loading=1",
        f"-Pjana:nevents={args.nevents}",
        f"-Ppodio:output_file={args.output_base_name}.tree.edm4eic.root",
        f"-Phistsfile={args.output_base_name}.ana.root",
        f"{args.input_file}",
    ]

    # RUN EICrecon
    start_time = datetime.now()
    print(" ".join(run_command))
    subprocess.run(run_command, shell=False, check=True)
    end_time = datetime.now()

    # Print execution time
    print("Start date and time : {}".format(start_time.strftime('%Y-%m-%d %H:%M:%S')))
    print("End date and time   : {}".format(end_time.strftime('%Y-%m-%d %H:%M:%S')))
    print("Execution real time : {}".format(end_time - start_time))
