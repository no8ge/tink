from kubernetes import client, config

from src.env import NAMESPACE


class Task():

    config.load_incluster_config()
    # config.load_kube_config()
    namespace = NAMESPACE
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()

    def __init__(self, task=None) -> None:
        self.task = task

    def puller(self):
        return client.V1Container(
            name='initer',
            image='dockerhub.qingcloud.com/qingtest/demo:dev',
            command=['python'],
            args=[
                "/demo/puller.py"
            ],
            image_pull_policy='IfNotPresent',

            volume_mounts=[
                client.V1VolumeMount(
                    name='puller',
                    read_only=True,
                    mount_path='/demo/puller.py',
                    sub_path='puller.py'
                ),
                client.V1VolumeMount(
                    name='cache-volume',
                    mount_path=f'/demo/{self.task.prefix}'

                )
            ],
            env=[
                client.V1EnvVar(
                    name='PREFIX',
                    value=self.task.prefix
                ),
                client.V1EnvVar(
                    name='MINIO_HOST',
                    value_from=client.V1EnvVarSource(
                        config_map_key_ref=client.V1ConfigMapKeySelector(
                            name='atop-globe-config',
                            key='minio_host'
                        )
                    )
                )
            ]
        )

    def builder(self):
        return client.V1Container(
            name=self.task.type,
            image='gcr.io/kaniko-project/executor:latest',
            args=[
                "--dockerfile=Dockerfile",
                f"--context=dir:///{self.task.prefix}",
                f"--destination={self.task.container.image}"
            ],

            image_pull_policy='IfNotPresent',
            ports=[
            ],
            volume_mounts=[
                client.V1VolumeMount(
                    name='kaniko-secret',
                    mount_path='/secret'
                ),
                client.V1VolumeMount(
                    name='cache-volume',
                    mount_path=f'/{self.task.prefix}'
                )
            ],
            env=[
                client.V1EnvVar(
                    name='DOCKER_CONFIG',
                    value='/secret/.docker/'
                )
            ]
        )

    def worker(self):
        return client.V1Container(
            name=self.task.type,
            image=self.task.container.image,
            command=['bash'],
            args=[
                "-c",
                f"{self.task.container.command}; python /atop/script.py"
            ],
            image_pull_policy='IfNotPresent',
            ports=[
                client.V1ContainerPort(container_port=9090, name='locust'),
            ],
            volume_mounts=[
                client.V1VolumeMount(
                    name='pusher',
                    read_only=True,
                    mount_path='/atop/script.py',
                    sub_path='script.py'
                )
            ],
            env=[
                client.V1EnvVar(
                    name='PREFIX',
                    value=self.task.prefix
                ),
                client.V1EnvVar(
                    name='POD_NAME',
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
                )
            ]
        )

    def object(self):

        if self.task.type == 'konika':
            init_containers = [self.puller()]
            containers = [self.builder()]

        if self.task.type in ['jmeter', 'aomaker', 'locust']:
            init_containers = []
            containers = [self.worker()]

        obj = client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=client.V1ObjectMeta(
                name=self.task.name,
                labels={'uid': self.task.uid},
            ),
            spec=client.V1PodSpec(
                init_containers=init_containers,
                containers=containers,
                # restart_policy='Never',
                restart_policy='OnFailure',
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
                        name='puller',
                        config_map=client.V1ConfigMapVolumeSource(
                            name='puller',
                            items=[
                                client.V1KeyToPath(
                                    key='puller', path='puller.py'
                                )
                            ]
                        ),
                    ),
                    client.V1Volume(
                        name='pusher',
                        config_map=client.V1ConfigMapVolumeSource(
                            name='pusher',
                            items=[
                                client.V1KeyToPath(
                                    key='script', path='script.py')
                            ]
                        )
                    ),
                    client.V1Volume(
                        name='cache-volume',
                        empty_dir=client.V1EmptyDirVolumeSource()
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
