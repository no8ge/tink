from src.env import NAMESPACE, INCLUSTER
from kubernetes import client, config


class Locust():

    if INCLUSTER == 'true':
        config.load_incluster_config()
    else:
        config.load_kube_config()
    namespace = NAMESPACE
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    def create_pod(self, pod):

        worker_logs_path = pod.container.volume_mounts.log_mount_path

        worker = client.V1Container(
            name=pod.type,
            image=pod.container.image,
            command=['bash'],
            args=[
                "-c",
                f"echo health > {worker_logs_path}/health; $(CMD); rm -rf {worker_logs_path}/health"
            ],
            image_pull_policy='IfNotPresent',
            ports=[
                client.V1ContainerPort(container_port=9090)
            ],
            volume_mounts=[
                client.V1VolumeMount(
                    name='logs-volume',
                    mount_path=worker_logs_path
                )
            ],
            env=[
                client.V1EnvVar(
                    name='CMD',
                    value=pod.container.command
                )
            ]
        )

        filebeat = client.V1Container(
            name="filebeat",
            image="docker.elastic.co/beats/filebeat:8.3.3",
            image_pull_policy='IfNotPresent',
            args=[
                '-e',
                '-E',
                "http.enabled=true"
            ],
            liveness_probe=client.V1Probe(
                _exec=client.V1ExecAction(
                    command=['cat', '/logs/health']),
                initial_delay_seconds=5,
                period_seconds=3
            ),
            volume_mounts=[
                client.V1VolumeMount(
                    name='logs-volume',
                    mount_path='/logs'
                ),
                client.V1VolumeMount(
                    name='filebeat-config',
                    read_only=True,
                    mount_path='/usr/share/filebeat/filebeat.yml',
                    sub_path='filebeat.yml'
                ),
            ],
            env=[
                client.V1EnvVar(
                    name='LOG_NAME',
                    value=pod.log_name
                ),
                client.V1EnvVar(
                    name='POD_IP',
                    value_from=client.V1EnvVarSource(
                        field_ref=client.V1ObjectFieldSelector(
                            field_path='status.podIP'
                        )
                    )
                )
            ]
        )

        spec = client.V1PodSpec(
            containers=[worker, filebeat],
            restart_policy='OnFailure',
            image_pull_secrets=[
                client.V1LocalObjectReference(
                    name='regcred'
                )
            ],
            volumes=[
                client.V1Volume(
                    name='logs-volume',
                    empty_dir=client.V1EmptyDirVolumeSource()
                ),
                client.V1Volume(
                    name='filebeat-config',
                    config_map=client.V1ConfigMapVolumeSource(
                        name=f'filebeat-config-{pod.type}',
                        items=[
                            client.V1KeyToPath(
                                key='filebeat.yml', path='filebeat.yml')
                        ]
                    )
                ),
            ]
        )

        metadata = client.V1ObjectMeta(
            name=pod.name,
        )

        pod_object = client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=metadata,
            spec=spec)

        resp = self.core_v1.create_namespaced_pod(
            body=pod_object, namespace=self.namespace)
        return resp

    def get_pod(self, name):
        resp = self.core_v1.read_namespaced_pod(
            name=name,
            namespace=self.namespace
        )
        return resp

    def delete_pod(self, name):
        resp = self.core_v1.delete_namespaced_pod(
            name=name,
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
