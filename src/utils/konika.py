from kubernetes import client, config

from src.env import INCLUSTER, NAMESPACE


class Konika():

    if INCLUSTER == 'true':
        config.load_incluster_config()
    else:
        config.load_kube_config()
    namespace = NAMESPACE
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()

    def create(self,job):

        initer = client.V1Container(
            name='initer',
            image='mx2542/demo:latest',
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
                    mount_path=f'/demo/{job.prefix}'

                )
            ],
            env=[
                client.V1EnvVar(
                    name='PREFIX',
                    value=job.prefix
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

        builder = client.V1Container(
            name=job.type,
            image='gcr.io/kaniko-project/executor:latest',
            args=[
                "--dockerfile=Dockerfile",
                f"--context=dir:///{job.prefix}",
                f"--destination={job.container.image}"
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
                    mount_path=f'/{job.prefix}'
                )
            ],
            env=[
                client.V1EnvVar(
                    name='DOCKER_CONFIG',
                    value='/secret/.docker/'
                )
            ]
        )

        spec = client.V1PodSpec(
            init_containers=[initer],
            containers=[builder],
            restart_policy='Never',
            # restart_policy='OnFailure',
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
                    name='cache-volume',
                    empty_dir=client.V1EmptyDirVolumeSource()
                ),
            ]
        )

        metadata = client.V1ObjectMeta(
            name=job.name
        )

        object = client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=metadata,
            spec=spec
        )

        resp = self.core_v1.create_namespaced_pod(
            body=object, namespace=self.namespace)
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
