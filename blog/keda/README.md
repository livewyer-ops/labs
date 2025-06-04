<!-- omit from toc -->
# KEDA Blog Series - Demo Code

The code used for the explanations and demonstrations in the KEDA Blog Series are located in this directory.

Instructions for reproducing the demonstrations are below.

- [Demo Setup](#demo-setup)
  - [Create a Local Cluster](#create-a-local-cluster)
  - [Fetch the Helm Repositories](#fetch-the-helm-repositories)
- [Demo 1 - KEDA ScaledObject: Autoscaling a Deployment with Prometheus Metrics](#demo-1---keda-scaledobject-autoscaling-a-deployment-with-prometheus-metrics)
  - [Install the Kube Prometheus Stack](#install-the-kube-prometheus-stack)
  - [Install KEDA](#install-keda)
  - [Install the PodInfo Application](#install-the-podinfo-application)
  - [Deploy the ScaledObject](#deploy-the-scaledobject)
  - [Trigger the Scale Up](#trigger-the-scale-up)
  - [Clean up](#clean-up)
- [Demo 2 - KEDA ScaledJob: Autoscaling a Job with Redis Lists](#demo-2---keda-scaledjob-autoscaling-a-job-with-redis-lists)
  - [Install KEDA](#install-keda-1)
  - [Install Redis](#install-redis)
  - [Deploy the TriggerAuthentication and ScaledJob](#deploy-the-triggerauthentication-and-scaledjob)
  - [Trigger the Scale Up](#trigger-the-scale-up-1)
  - [Clean up](#clean-up-1)

## Demo Setup

Note: KEDA version 2.17.1 requires a Kubernetes cluster using version 1.29 and higher

### Create a Local Cluster

Any cluster with a compatible Kubernetes version should be able follow these instructions to demonstrate using KEDA. For a quick proof of concept, you can create a cluster using [KIND](https://kind.sigs.k8s.io/) with the following command:

```bash
kind create cluster
```

Once `kind` has finished creating the cluster, run `kubectl version` to check the Kubernetes version.

### Fetch the Helm Repositories

Get the required helm repositories with the commands below:

```bash
helm repo add kedacore https://kedacore.github.io/charts
helm repo add podinfo https://stefanprodan.github.io/podinfo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

## Demo 1 - KEDA ScaledObject: Autoscaling a Deployment with Prometheus Metrics

Demo 1 will showcase KEDA using Prometheus metrics to automatically scale a front-end workload based on the amount of traffic it is receiving.

### Install the Kube Prometheus Stack

Install the Kube Prometheus Stack, but override the default configurations and have the the `PrometheusOperator` watch/use any `serviceMonitor` object in the cluster. You can use following command:

```bash
helm install kube-prom-stack prometheus-community/kube-prometheus-stack \
--create-namespace --namespace obs-system \
--version 70.4.2 \
--set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

Using `--set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues` will cause Helm to render the manifest for the `Prometheus` object to include the following:

```yaml
    serviceMonitorNamespaceSelector: {}
    serviceMonitorSelector: {}
```

Once the Prometheus pod is running, you can access the Prometheus UI local at <localhost:8081> with `kubectl -n obs-system port-forward svc/kube-prom-stack-kube-prome-prometheus 8081:9090`

### Install KEDA

Install the KEDA using it's Helm chart with the following command:

```bash
helm install keda kedacore/keda \
--create-namespace --namespace keda \
--version 2.17.1
```

### Install the PodInfo Application

Install the front-end workload, in this case we will be using the podinfo app with `serviceMonitor.enabled=true` for the Prometheus Operator to find and use to configure Prometheus to scrape metrics from the podinfo app with the following command

```bash
helm install podinfo podinfo/podinfo \
--create-namespace --namespace podinfo \
--version 6.8.0 \
--set serviceMonitor.enabled=true
```

### Deploy the ScaledObject

1. Update the `serverAddress` in the `manifests/keda/prom-scaledobject.yaml` file.
    - If you want to access it internally, you can use the format `http://SVC_NAME.NAMESPACE.svc.cluster.local:9090` (e.g. `http://kube-prom-stack-kube-prome-prometheus.obs-system.svc.cluster.local:9090`).
      - If your Prometheus instance is served on a subpath you must attach the subpath after the port number (e.g. `http://SVC_NAME.NAMESPACE.svc.cluster.local:9090/prometheus`)
2. Deploy the `ScaledObject` with the prometheus trigger

    ```bash
    kubectl apply -f manifests/keda/prom-scaledobject.yaml -n podinfo
    ```

3. Check the scaled object is ready with `kubectl get scaledobject -n podinfo`
    1. If it is not ready, check the logs of the KEDA Operator pod (`kubectl logs POD_NAME -n podinfo`). It will most likely be the server address being incorrectly set.
4. Check and examine the HPA object created by KEDA with `kubectl describe hpa -n podinfo && kubectl get hpa -n podinfo`.

### Trigger the Scale Up

Now we want to trigger the autoscaling.

1. Run `kubectl -n podinfo port-forward deploy/podinfo 8080:9898` to allow you to access the podinfo app at <localhost:8080>
2. Open another terminal and watch the pods in the `podinfo` namespace with `kubectl get pods -n podinfo -w`.
3. Open another terminal and watch the deployments in the `podinfo` namespace with `kubectl get deployments -n podinfo -w`.
4. Now we want to trigger the autoscaling. Repeatedly run curl commands against the PodInfo app with `while :; do curl localhost:8080; sleep 1; done`.
5. As you run the curl commands, you will eventually see the number of replicas of the consumer workload increase in the other terminals.
6. Stop running the curl commands (with `Ctrl+C`).
7. Observe the number of pods scale down back to the minimum number of replicas

### Clean up

Run the following commands to clean up all demo resources:

```bash
kubectl delete -f manifests/keda/prom-scaledobject.yaml -n podinfo
helm uninstall podinfo -n podinfo
helm uninstall keda -n keda
helm uninstall kube-prom-stack -n obs-system
kubectl delete ns podinfo keda obs-system
```

## Demo 2 - KEDA ScaledJob: Autoscaling a Job with Redis Lists

Demo 2 will showcase KEDA authenticating against Redis and using a Redis list to automatically scale jobs.

### Install KEDA

Install the KEDA using it's Helm chart with the following command:

```bash
helm install keda kedacore/keda \
--create-namespace --namespace keda \
--version 2.17.1
```

### Install Redis

Install a Redis Deployment and Services using the example manifest in this repository.

```bash
kubectl create ns redis
kubectl apply -f manifests/redis/redis.yaml -n redis
kubectl get pods -n redis
```

### Deploy the TriggerAuthentication and ScaledJob

1. Deploy the `TriggerAuthentication` and `ScaledJob` with the Redis trigger

    ```bash
    kubectl apply -f manifests/keda/redis-triggerauth.yaml -n redis
    kubectl apply -f manifests/keda/redis-scaledjob.yaml -n redis
    ```

2. Check the `TriggerAuthentication` with `kubectl describe triggerauth keda-trigger-auth-redis-secret -n redis`
3. Check the scaled object is ready with `kubectl get scaledjob -n redis`
    1. If it is not ready, check the logs of the keda pod (`kubectl logs POD_NAME -n keda`). It will most likely be the configurations to connect to Redis being incorrect.

### Trigger the Scale Up

Now we want to trigger the autoscaling.

1. Watch the jobs in the `redis` namespace with `kubectl get jobs -n redis -w`
2. Open another terminal and store the redis pod name and password in variables with:

    ```bash
    export REDIS_POD=$(kubectl get pods -n redis -l app=redis --no-headers -o custom-columns=":metadata.name")
    export REDIS_PASS=$(kubectl get secret redis -n redis --template={{.data.REDIS_PASS}} | base64 --decode)
    ```

3. Exec into the redis pod with `kubectl -n redis exec -it $REDIS_POD -- redis-cli -a $REDIS_PASS`
4. Check the length of the list stored in the `myotherlist` key with `LLEN myotherlist`
5. Add an item to the list with `LPUSH myotherlist "my-item"` to put the length of the list above the autoscaling threshold
6. Wait and observe as jobs gets created
7. Remove the item from the list with `LPOP myotherlist`
8. Wait and observe as jobs stopped getting created by KEDA

### Clean up

Run the following commands to clean up all demo resources:

```bash
kubectl delete -f manifests/redis/redis.yaml -n redis
kubectl delete -f manifests/keda/redis-scaledjob.yaml -n redis
kubectl delete -f manifests/keda/redis-triggerauth.yaml -n redis
helm uninstall keda -n keda
kubectl delete ns keda redis
```
