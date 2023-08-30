import traceback
from loguru import logger
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException

from src.env import NAMESPACE


class Task():
    try:
        config.load_incluster_config()
        api_instance = client.CoreV1Api()
    except ConfigException as e:
        if e.args[0] == 'Service host/port is not set.':
            logger.warning(e)
            config.load_kube_config()
            api_instance = client.CoreV1Api()
    except Exception as e:
        logger.error(traceback.format_exc())

    namespace = NAMESPACE
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()

    def __init__(self, task=None) -> None:
        self.task = task

    def worker(self):
        return client.V1Container(
            name=self.task.type,
            image=self.task.container.image,
            command=['bash'],
            args=[
                "-c",
                f"{self.task.container.command}; python /atop/cli.py"
            ],
            image_pull_policy='IfNotPresent',
            volume_mounts=[
                client.V1VolumeMount(
                    name='config',
                    read_only=True,
                    mount_path='/atop/cli.py',
                    sub_path='cli.py'
                ),
                client.V1VolumeMount(
                    name='share-volume',
                    mount_path='/report',
                )
            ],
            env=[
                client.V1EnvVar(
                    name='REPORT',
                    value=self.task.prefix
                ),
                client.V1EnvVar(
                    name='PREFIX',
                    value_from=client.V1EnvVarSource(
                        field_ref=client.V1ObjectFieldSelector(
                            field_path='metadata.name'
                        )
                    )
                ),
                client.V1EnvVar(
                    name='MINIO_HOST',
                    value_from=client.V1EnvVarSource(
                        config_map_key_ref=client.V1ConfigMapKeySelector(
                            name='atop-globe-config',
                            key='minio_host'
                        )
                    )
                ),
                client.V1EnvVar(
                    name='FILES_SERVICE',
                    value_from=client.V1EnvVarSource(
                        config_map_key_ref=client.V1ConfigMapKeySelector(
                            name='atop-globe-config',
                            key='files_service_hosts'
                        )
                    )
                )
            ]
        )

    def object(self):

        obj = client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=client.V1ObjectMeta(
                name=f'{self.task.name}',
                labels={'uid': self.task.uid},
            ),
            spec=client.V1PodSpec(
                init_containers=[],
                containers=[self.worker()],
                # host_network=True,
                # dns_policy='ClusterFirstWithHostNet',
                restart_policy='Never',
                image_pull_secrets=[
                    client.V1LocalObjectReference(
                        name='regcred'
                    )
                ],
                volumes=[
                    client.V1Volume(
                        name='kaniko-secret',
                        secret=client.V1SecretVolumeSource(
                            secret_name='regcred',
                            items=[
                                client.V1KeyToPath(
                                    key='.dockerconfigjson', path='.docker/config.json'
                                )
                            ]
                        )
                    ),
                    client.V1Volume(
                        name='config',
                        config_map=client.V1ConfigMapVolumeSource(
                            name='files-config',
                            items=[
                                client.V1KeyToPath(
                                    key='cli', path='cli.py')
                            ]
                        )
                    ),
                    client.V1Volume(
                        name='share-volume',
                        persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                            claim_name='data-atop-reports'
                        )
                    ),
                ]
            )
        )
        return obj

    def create(self):
        resp = self.core_v1.create_namespaced_pod(
            body=self.object(), namespace=self.namespace)
        return resp

    def get(self, name):
        resp = self.core_v1.read_namespaced_pod(
            name=name,
            namespace=self.namespace
        )
        return resp

    def delete(self, name):
        resp = self.core_v1.delete_namespaced_pod(
            name=name,
            namespace=self.namespace
        )
        return resp
