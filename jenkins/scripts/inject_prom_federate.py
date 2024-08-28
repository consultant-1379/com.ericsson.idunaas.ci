#!/usr/bin/python3

from  kubernetes import client, config
import argparse
import yaml

config.load_kube_config()
kube_api = client.CoreV1Api()

def is_prom_federate_enabled():
    # Return True of any job contains metric path points to federation
    _prom_cm = kube_api.read_namespaced_config_map(name="prometheus-server",namespace="prometheus")
    _prom_config = yaml.safe_load(_prom_cm.data["prometheus.yml"])
    for job in _prom_config['scrape_configs']:
        if '/metrics/viewer/federate' in job.values():
            return True
    return False

def enable_federation(app_namespace):
    # Parse exisiting prometheus config and add federation job targetting prometheus from application namespace.
    _prom_cm = kube_api.read_namespaced_config_map(name="prometheus-server",namespace="prometheus")
    _prom_config = yaml.safe_load(_prom_cm.data["prometheus.yml"])
    _federate_job = {'job_name': 'eiap_federate',
                    'honor_labels': True,
                    'metrics_path': '/metrics/viewer/federate',
                    'params': {'match[]': ['{job!=""}']},
                    'static_configs': [{'targets': ['eric-pm-server.' + app_namespace + ':9090']}]
                    }
    _prom_config['scrape_configs'].append(_federate_job)
    _prom_yml = yaml.dump(_prom_config)
    body = client.V1ConfigMap(data={"prometheus.yml": _prom_yml})
    resp = kube_api.patch_namespaced_config_map(name='prometheus-server',namespace='prometheus',body=body)
    print("Federation job added")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--namespace', type=str, required=True)
    args = parser.parse_args()
    if is_prom_federate_enabled():
        print("Federation already enabled")
        exit(0)
    enable_federation(args.namespace)



if __name__ == '__main__':
    main()




