#!/usr/bin/env python

import json
import logging
import os
import subprocess
import sys

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.root.setLevel(logging.DEBUG)

OPA_BINARY_PATH = os.environ["OPA_BINARY_PATH"]
OPA_FILES_DIR = sys.argv[1]
INPUT_FILES = sys.argv[2:]
OPA_COMMAND_TEMPLATE = "{opa_binary_path} eval --format pretty -d {opa_policy_files_dir} -i {input_file_path} '{query}'"
COMPLIANCE_CHECK_QUERY = '[ f | props := walk(data); props[0][count(props[0]) - 1] == "compliant"; f := {"package": concat(".", array.slice(props[0], 0, count(props[0]) - 1)), "compliant": props[1]}]'


def run_process(command):
    try:
        process = subprocess.run(
            command, capture_output=True, shell=True, encoding="utf-8"
        )
    except BrokenPipeError as e:
        logger.error("Process failed with %s", e)
        raise
    except Exception as e:
        logger.error("Process failed with %s", e)
        raise
    else:
        try:
            output = json.loads(process.stdout)
        except json.decoder.JSONDecodeError:
            logger.error(
                "Could not decode JSON from stdout. stdout: '%s', stderr: '%s'",
                process.stdout,
                process.stderr,
            )
            sys.exit(2)
        logger.debug("Shell command stdout: %s", output)
        return output


def main():
    if INPUT_FILES:
        logger.info("Received input files %s", INPUT_FILES)
    else:
        logger.warning("No input files received")
    for input_file in INPUT_FILES:
        command = OPA_COMMAND_TEMPLATE.format(
            opa_binary_path=OPA_BINARY_PATH,
            opa_policy_files_dir=OPA_FILES_DIR,
            input_file_path=input_file,
            query=COMPLIANCE_CHECK_QUERY,
        )
        opa_result = run_process(command)
        for compliance_result in opa_result:
            if compliance_result["compliant"]:
                logger.info(
                    "OPA policy %s succeeded on input file %s",
                    compliance_result["package"],
                    input_file,
                )
            else:
                logger.error(
                    "OPA policy %s failed on input file %s",
                    compliance_result["package"],
                    input_file,
                )
                sys.exit(1)
        logger.info("All OPA policy checks succeeded")


if __name__ == "__main__":
    main()
