# pyright: reportMissingImports=false, reportUndefinedVariable=false

# Load extensions
load('ext://restart_process', 'docker_build_with_restart')
load('ext://uibutton', 'cmd_button')

# Allowed clusters
allow_k8s_contexts('minikube')

# Define the container builds for each microservice
docker_build_with_restart(
    'gateway',
    '.',
    dockerfile='services/gateway/Dockerfile',
    entrypoint='gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --reload',
    live_update=[
        sync('./services/gateway/source', '/data')
    ]
)
docker_build_with_restart(
    'tracker',
    '.',
    dockerfile='services/tracker/Dockerfile',
    entrypoint='python main.py',
    live_update=[
        sync('./services/tracker/source', '/data')
    ]
)
docker_build_with_restart(
    'worker',
    '.',
    dockerfile='services/worker/Dockerfile',
    entrypoint='python main.py',
    live_update=[
        sync('./services/worker/source', '/data')
    ]
)
docker_build_with_restart(
    'scheduler',
    '.',
    dockerfile='services/scheduler/Dockerfile',
    entrypoint='python main.py',
    live_update=[
        sync('./services/scheduler/source', '/data')
    ]
)

# Buttons
pod_exec_script = '''
set -eu
POD_NAME="$(tilt get kubernetesdiscovery scheduler -ojsonpath='{.status.pods[0].name}')"
kubectl exec "$POD_NAME" -- python3 /data/task.py compare
'''
cmd_button('scheduler:compare',
    argv=['sh', '-c', pod_exec_script],
    resource='scheduler',
    icon_name='schedule',
    text='Schedule Compare',
)

pod_exec_script = '''
set -eu
POD_NAME="$(tilt get kubernetesdiscovery rabbitmq -ojsonpath='{.status.pods[0].name}')"
kubectl exec "$POD_NAME" -- rabbitmqctl purge_queue tasks
'''
cmd_button('rabbitmq:purge',
    argv=['sh', '-c', pod_exec_script],
    resource='rabbitmq',
    icon_name='delete',
    text='Purge Queue',
)

# Define Kubernetes objects for each component
k8s_resource("gateway", labels=["app"], port_forwards=8000)
k8s_resource("tracker", labels=["app"])
k8s_resource("worker", labels=["app"])
k8s_resource("scheduler", labels=["app"])
k8s_resource("redis", labels=["state"])
k8s_resource("rabbitmq", labels=["state"], port_forwards=15672)

k8s_resource("step-ci", labels=["test"])

# Define Kubernetes resources for each service
k8s_yaml("develop/kubernetes/gateway.yaml")
k8s_yaml("develop/kubernetes/tracker.yaml")
k8s_yaml("develop/kubernetes/worker.yaml")
k8s_yaml("develop/kubernetes/scheduler.yaml")

# Define Kubernetes resources for stateful resources
k8s_yaml("develop/kubernetes/redis.yaml")
k8s_yaml("develop/kubernetes/rabbitmq.yaml")

# Define Kubernetes resources for running tests
k8s_yaml("develop/kubernetes/step-ci.yaml")

# Health checks and basic tests
docker_build_with_restart(
    'step-ci',
    '.',
    dockerfile="tests/step-ci/Dockerfile",
    entrypoint="node dist/index.js run /tests/workflow.yml",
    live_update=[
        sync("./tests", "/tests"),
    ]
)