from kubernetes import client

from src.utils.base_job import BaseJob


class Locust(BaseJob):

    def create_job(self, job):

        worker_logs_path = job.container.volume_mounts.log_mount_path

        worker = client.V1Container(
            name=job.type,
            image=job.container.image,
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
                    value=job.container.command
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
                    value=job.log_name
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
                            name='logs-volume',
                            empty_dir=client.V1EmptyDirVolumeSource()
                        ),
                        client.V1Volume(
                            name='filebeat-config',
                            config_map=client.V1ConfigMapVolumeSource(
                                name=f'filebeat-config-{job.type}',
                                items=[
                                    client.V1KeyToPath(
                                        key='filebeat.yml', path='filebeat.yml')
                                ]
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
