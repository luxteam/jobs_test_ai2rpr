import argparse
import sys
import os
import subprocess
import psutil
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from jobs_launcher.core.config import main_logger


def createArgsParser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--tests_list', required=True, metavar="<path>")
    parser.add_argument('--render_path', required=True, metavar="<path>")
    parser.add_argument('--scene_path', required=True, metavar="<path")
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--output_img_dir', required=True)
    parser.add_argument('--output_file_ext', required=True)
    return parser


def main():
    args = createArgsParser().parse_args()

    tests_list = {}
    with open(args.tests_list, 'r') as file:
        tests_list = json.loads(file.read())

    try:
        os.makedirs(args.output_img_dir)
    except OSError as err:
        main_logger.error(str(err))
        return 1

    for test in tests_list:
        if test['status'] == 'active':
            render_log_path = os.path.join(args.output_dir, test['name'] + '.rs.log')
            cmd_script = '"{}" -r arnold -log "{}" -rd "{}" -cam persp -im {} -of {} "{}"'\
                .format(args.render_path, render_log_path, args.output_img_dir, test['name'], args.output_file_ext, os.path.join(args.scene_path, test['name']))
            cmd_script_path = os.path.join(args.output_dir, test['name'] + '.renderArnold.bat')

            try:
                with open(cmd_script_path, 'w') as file:
                    file.write(cmd_script)
                with open(render_log_path, 'w') as file:
                    pass
            except OSError as err:
                main_logger.error("Error while saving bat: {}".format(str(err)))
            else:
                rc = -1
                os.chdir(args.output_dir)
                p = psutil.Popen(cmd_script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()

                try:
                    rc = p.wait()
                except psutil.TimeoutExpired as err:
                    main_logger.error("Terminated by simple render. {}".format(str(err)))
                    rc = -1
                    for child in reversed(p.children(recursive=True)):
                        child.terminate()
                    p.terminate()
                # return rc
    return 0


if __name__ == "__main__":
    exit(main())
