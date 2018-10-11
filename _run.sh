#!/bin/bash
./_clean.sh
./maas --reset
ansible-playbook k8s-01-base.yaml
ansible-playbook k8s-02-install.yaml
ansible-playbook k8s-03-common.yaml
ansible-playbook k8s-04-localhost.yaml
