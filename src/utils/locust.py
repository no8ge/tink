from kubernetes import client

from src.utils.base_job import BaseJob


class Locust(BaseJob):

    def create_job(self, job):

        worker = client.V1Container(
            name=job.type,
            image=job.container.image,
            command=['bash'],
            args=[
                "-c",
                job.container.command
            ],
            image_pull_policy='IfNotPresent',
            ports=[
                client.V1ContainerPort(container_port=9090, name='locust')
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
                        'curl --fail 127.0.0.1:9090'
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

        spec = client.V1JobSpec(
            ttl_seconds_after_finished=10,
            backoff_limit=4,
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    hostname=job.name,
                    containers=[worker, filebeat],
                    restart_policy='Never',
                    image_pull_secrets=[
                        client.V1LocalObjectReference(
                            name='regcred'
                        )
                    ],
                    volumes=[
                        client.V1Volume(
                            name='filebeat-config',
                            config_map=client.V1ConfigMapVolumeSource(
                                name='filebeat-config-locust',
                                items=[
                                    client.V1KeyToPath(
                                        key='filebeat.yml', path='filebeat.yml')
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
            ),
        )

        metadata = client.V1ObjectMeta(
            name=job.name,
        )

        job_object = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=spec)

        resp = self.batch_v1.create_namespaced_job(
            body=job_object, namespace=self.namespace)
        return resp
