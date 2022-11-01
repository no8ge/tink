from src.env import NAMESPACE, INCLUSTER
from kubernetes import client, config


class BaseJob():

    if INCLUSTER == 'true':
        config.load_incluster_config()
    else:
        config.load_kube_config()
    namespace = NAMESPACE
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    def get_job(self, name):
        resp = self.batch_v1.read_namespaced_job(
            name=name,
            namespace=self.namespace
        )
        return resp

    def delete_job(self, name):
        resp = self.batch_v1.delete_namespaced_job(
            name=name,
            propagation_policy='Background',
            namespace=self.namespace
        )
        return resp

    def creat_configmap_from_file(self, name, fp, key='filebeat.yml'):

        metadata = client.V1ObjectMeta(name=name)
        config_map = client.V1ConfigMap(
            api_version='v1',
            kind='ConfigMap',
            data={
                key: open(fp).read()
            },
            metadata=metadata
        )
        result = self.core_v1.create_namespaced_config_map(
            namespace=self.namespace,
            body=config_map,

        )
        return result

    def delete_configmap(self, name):
        resp = self.core_v1.delete_namespaced_config_map(
            name=name,
            namespace=self.namespace
        )
        return resp
