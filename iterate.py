#!/usr/bin/env python
import os
import stat
import subprocess
import click
import logging
from datetime import datetime
import json


log = logging.getLogger(__name__)

console = logging.StreamHandler()
format_str = '[%(asctime)s]\t%(levelname)s | %(process)s %(filename)s:%(lineno)s | %(message)s'
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console) # prints to console.
log.setLevel(logging.DEBUG if os.getenv('DEBUG') else logging.INFO)

def timed_cmd(cmd):
    if type(cmd) == str:
        cmd = cmd.split(' ')
    log.debug('Starting to run command {}'.format(cmd))
    t1 = datetime.utcnow()
    ret_val = {'start': t1.isoformat()}
    try:
        output = subprocess.check_output(cmd)
        ret_val['log'] = output.decode('utf-8').split('\n')
        ret_val['return_code'] = 0
    except subprocess.CalledProcessError as cpex:
        ret_val['log'] = (cpex.output or cpex.stdout + cpex.stderr).decode('utf-8').split('\n')
        ret_val['return_code'] = cpex.returncode
    td = (datetime.utcnow() - t1)
    ret_val['elapsed'] = td.total_seconds()
    log.info('Command {} took {} seconds to return status {}'.format(cmd, str(ret_val['elapsed']), str(ret_val['return_code'])))
    return ret_val

COMMAND_LIST = ['rm -rf *.retry',
                'python maas --kill',
                'python maas --reset',
                'ansible-playbook k8s-base.yaml',
                'ansible-playbook k8s-common.yaml',
                'ansible-playbook k8s-kube-system.yaml']

@click.command()
@click.argument('stage', envvar='STAGE', type=click.IntRange(min=0, max=4), default=1)
@click.option('--maas-url', envvar='MAAS_API_URL', default='http://172.16.16.2:5240/MAAS', required=True)
@click.option('--maas-key', envvar='MAAS_API_KEY', required=True)
@click.option('--debug', default=False)
@click.option('--output-log', default=True)
def cli(stage, maas_url, maas_key, debug, output_log):
    """iterate.py - roll through scripts systematically

    This script is designed to instrument the serial processing of scripts for debug purposes.
    """
    if debug:
        log.setLevel(logging.DEBUG)
    detail = {'start': datetime.utcnow().isoformat(), }
    results = {}
    log_id = '{}-{}'.format(str(stage), datetime.utcnow().isoformat().replace(':', '_').replace('.', '_'))
    log.info('Starting to run proces for stage {} with commands: '.format(str(stage), COMMAND_LIST[:stage + 1]))
    for cmd in COMMAND_LIST[:stage + 1]:
        results[cmd] = timed_cmd('{}'.format(cmd))
    if output_log:
        if not os.path.isdir('log'):
            os.makedirs('log')
        if not os.path.isdir('log/{}'.format(str(stage))):
            os.makedirs('log/{}'.format(str(stage)))
        with open('log/{}/{}.json'.format(str(stage), log_id), 'w') as f:
            f.write(json.dumps(results))
    if results:
        log.info('')
        log.info('          started          -    cmd    - elapsed')
    for k, v in results.items():
        log.info('{} - {} - {} seconds'.format(v.get('start'), k, v.get('elapsed')))


if __name__ == '__main__':
  cli()
