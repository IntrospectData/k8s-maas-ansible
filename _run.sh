#!/bin/bash
./_clean.sh
./maas --reset
ansible-playbook k8s-base.yaml
ansible-playbook k8s-common.yaml
