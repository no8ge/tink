from kubernetes import client, config

from src.env import NAMESPACE, INCLUSTER


class Pod():

    if INCLUSTER == 'true':
        config.load_incluster_config()
    else:
        config.load_kube_config()
    namespace = NAMESPACE
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    def create_job(self, pod):

        worker = client.V1Container(
            name=pod.type,
            image=pod.container.image,
            command=['bash'],
            args=[
                "-c",
                f"python /atop/ack.py; {pod.container.command}; python /atop/script.py"
            ],
            image_pull_policy='IfNotPresent',
            ports=[
                client.V1ContainerPort(container_port=9090, name='locust'),
                client.V1ContainerPort(container_port=8000, name='ack')
            ],
            volume_mounts=[
                client.V1VolumeMount(
                    name='pusher',
                    read_only=True,
                    mount_path='/atop/script.py',
                    sub_path='script.py'
                ),
                client.V1VolumeMount(
                    name='ack',
                    read_only=True,
                    mount_path='/atop/ack.py',
                    sub_path='ack.py'
                )
            ],
            env=[
                client.V1EnvVar(
                    name='PREFIX',
                    value=pod.prefix
                )
            ]
        )

        filebeat = client.V1Container(
            name="filebeat",
            image="docker.elastic.co/beats/filebeat:8.3.3",
            image_pull_policy='IfNotPresent',
            security_context=client.V1SecurityContext(
                privileged=False,
                run_as_user=0
            ),
            args=[
                '-e',
                '-E',
                "http.enabled=true"
            ],
            liveness_probe=client.V1Probe(
                _exec=client.V1ExecAction(
                    command=[
                        'sh',
                        '-c',
                        'curl --fail 127.0.0.1:8000'
                    ]
                ),
                initial_delay_seconds=5,
                period_seconds=3,
                timeout_seconds=5,
                success_threshold=1,
                failure_threshold=3
            ),
            volume_mounts=[
                client.V1VolumeMount(
                    name='filebeat-config',
                    read_only=True,
                    mount_path='/usr/share/filebeat/filebeat.yml',
                    sub_path='filebeat.yml'
                ),
                client.V1VolumeMount(
                    name='varlibdockercontainers',
                    mount_path='/var/lib/docker/containers'
                ),
                client.V1VolumeMount(
                    name='varlog',
                    mount_path='/var/log'
                ),
                client.V1VolumeMount(
                    name='varrundockersock',
                    mount_path='/var/run/docker.sock'
                ),
            ],
            env=[
                client.V1EnvVar(
                    name='POD_NAME',
                    value_from=client.V1EnvVarSource(
                        field_ref=client.V1ObjectFieldSelector(
                            field_path='metadata.name'
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
                    name='filebeat-config',
                    config_map=client.V1ConfigMapVolumeSource(
                        name=f'filebeat-config-{pod.type}',
                        items=[
                            client.V1KeyToPath(
                                key='filebeat.yml', path='filebeat.yml')
                        ]
                    )
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
                    name='ack',
                    config_map=client.V1ConfigMapVolumeSource(
                        name='ack',
                        items=[
                            client.V1KeyToPath(
                                key='ack', path='ack.py')
                        ]
                    )
                ),
                client.V1Volume(
                    name='varrundockersock',
                    host_path=client.V1HostPathVolumeSource(
                        path='/var/run/docker.sock'
                    )
                ),
                client.V1Volume(
                    name='varlog',
                    host_path=client.V1HostPathVolumeSource(
                        path='/var/log'
                    )
                ),
                client.V1Volume(
                    name='varlibdockercontainers',
                    host_path=client.V1HostPathVolumeSource(
                        path='/var/lib/docker/containers'
                    )
                )
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

    def get_job(self, name):
        resp = self.core_v1.read_namespaced_pod(
            name=name,
            namespace=self.namespace
        )
        return resp

    def delete_job(self, name):
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
