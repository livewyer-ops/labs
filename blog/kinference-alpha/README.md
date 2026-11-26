<!-- omit from toc -->
# [K]inference - Demo Code

The code used for the demonstrations in the blog post [[K]inference puts inference policy in YAML, but who writes it?](https://livewyer.io/blog/kinference-puts-inference-policy-in-yaml-but-who-writes-it/) is located in this directory.

Instructions for reproducing the demonstrations are below. Each demo ends with what we saw on our own run.

- [Demo Setup](#demo-setup)
  - [Create a Cluster](#create-a-cluster)
  - [Install the Gateway and \[K\]inference](#install-the-gateway-and-kinference)
  - [Install the Demo Chart](#install-the-demo-chart)
- [Demo 1 - A PII Policy That Fails Open](#demo-1---a-pii-policy-that-fails-open)
- [Demo 2 - \[K\]inference Against a Plain Service](#demo-2---kinference-against-a-plain-service)
- [Demo 3 - A Noisy Neighbour](#demo-3---a-noisy-neighbour)
- [Demo 4 - Restarting \[K\]inference Under Load](#demo-4---restarting-kinference-under-load)
- [Clean up](#clean-up)
- [Things We Hit Along the Way](#things-we-hit-along-the-way)

## Demo Setup

This demo was tested with [K]inference `0.1.0-alpha.8`, the Buoyant Gateway `0.1.0-alpha.7`, Gateway API `v1.5.1`, vLLM `0.31.0`, and the NVIDIA device plugin `0.20.2`, on kind and on EKS `1.37`.

Demo 1 runs on a local kind cluster. Demos 2 to 4 need GPUs, so they run on EKS.

### Create a Cluster

For Demo 1, create a local cluster with [kind](https://kind.sigs.k8s.io/):

```bash
kind create cluster --name kinference-demo
```

For Demos 2 to 4, create an EKS cluster with one CPU node and three `g5.xlarge` GPU nodes (NVIDIA A10G) in `eu-west-1`. You need quota for 12 vCPUs of G instances in that region. The cluster costs about $4 an hour while it runs, so remember to [clean up](#clean-up) afterwards.

```bash
eksctl create cluster -f clusters/eks.yaml --install-nvidia-plugin=false
```

On EKS, install the NVIDIA device plugin so the GPUs show up as `nvidia.com/gpu`:

```bash
helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
helm repo update
helm install nvidia-device-plugin nvdp/nvidia-device-plugin \
--namespace kube-system \
--version 0.20.2 \
-f values/nvidia-device-plugin.yaml
```

Check that each GPU node reports one GPU with `kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\\.com/gpu`.

### Install the Gateway and [K]inference

Install the Gateway API CRDs, then the Buoyant Gateway's CRDs and controller:

```bash
kubectl apply --server-side --force-conflicts \
-f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.5.1/standard-install.yaml

helm install gateway-crds oci://ghcr.io/buoyantio/charts/gateway-crds --version 0.1.0-alpha.7
helm install gateway oci://ghcr.io/buoyantio/charts/gateway --version 0.1.0-alpha.7 --wait
```

Install [K]inference's CRDs, then [K]inference itself with the values in `values/kinference.yaml`. Those values read the tenant from an `x-tenant` header and switch tokenisation to `local`; see [Things We Hit Along the Way](#things-we-hit-along-the-way) for why.

```bash
helm install kinference-crds oci://cr.kinference.ai/kinference-ai/charts/kinference-crds --version 0.1.0-alpha.8
helm install kinference oci://cr.kinference.ai/kinference-ai/charts/kinference --version 0.1.0-alpha.8 \
-f values/kinference.yaml --wait
```

### Install the Demo Chart

The demo chart holds the `Gateway`, the `HTTPRoute`, the `InferencePool`, the vLLM workers, and a mock external provider which logs every request body it receives.

On kind, it runs one vLLM worker on the CPU build with dummy weights:

```bash
helm install demo ./demo-chart
```

On EKS, it runs three workers serving `Qwen/Qwen3-8B-FP8`:

```bash
helm install demo ./demo-chart -f demo-chart/values-eks.yaml
```

Wait for the workers with `kubectl rollout status deploy/vllm`. On EKS the first start takes a few minutes, while each node pulls the vLLM image and the model.

The `InferencePool` uses whichever `InferencePolicy` is named `active`. Each demo applies one from `policies/`, and `kubectl get infpol active` shows whether [K]inference has accepted it.

## Demo 1 - A PII Policy That Fails Open

Demo 1 applies the "keep personal data on the cluster" policy from [K]inference's launch post, takes the local workers away, and checks where a request containing personal data ends up.

1. In another terminal, port-forward the gateway with `kubectl port-forward svc/llm-gw-gatewayd 8080:80`.
2. Apply the launch policy and check it is accepted:

    ```bash
    kubectl apply -f policies/pii-launch.yaml
    kubectl get infpol active
    ```

3. Scale the local workers to zero, so that in step 6 the only choice left is between rejecting the request and sending it to the provider:

    ```bash
    kubectl scale deploy/vllm --replicas=0
    ```

4. Send a request containing personal data:

    ```bash
    curl -s localhost:8080/v1/chat/completions \
    -H 'content-type: application/json' -H 'x-tenant: clinic' \
    -d '{"model":"chat","max_tokens":16,"messages":[{"role":"user","content":"Patient Jane Example, NHS number 943 476 5919, asks about her results."}]}'
    ```

5. Check what the mock provider received with `kubectl logs deploy/mock-provider`.
6. Apply the fail-closed policy, which only lets a request leave the cluster when it carries a `pii-cleared` tag, and send the same request again:

    ```bash
    kubectl apply -f policies/pii-fail-closed.yaml
    ```

7. Scale the workers back up with `kubectl scale deploy/vllm --replicas=1`.

**What we saw:** the request came back from the mock provider with a 200, and the provider's log held the full prompt and the `x-tenant` header. The NHS number is only a marker. [K]inference has no way of knowing it is personal data, because nothing in `0.1.0-alpha.8` sets tags on requests, so the `pii-detected` exclusion never matches any request. The launch policy lists the provider before the local workers, so the request goes to the provider even with a local worker up; skip step 3 to see that. `onEmpty: Reject` does not stop it, because it only applies once every backend has been excluded. With the fail-closed policy, which needs a `pii-cleared` tag before a request may leave, the same request came back as a 403, with "every candidate was excluded".

## Demo 2 - [K]inference Against a Plain Service

Demo 2 sends the same traffic through [K]inference and then straight to the vLLM `Service`, where kube-proxy picks a pod at random, and compares how many requests each serves.

The traffic is built on shared prompts: long blocks of text which many requests start with, such as an agent's system prompt and tool definitions. The load generator calls them prefixes. vLLM caches the work it does on a prefix, so a request which lands on a worker that has already seen its prefix skips most of that work, and [K]inference's job is to send it there. The demo varies how many shared prompts there are, because that decides how often a random pick finds a warm cache anyway.

The load generator runs as a `Job` inside the cluster, and `loadgen/run.sh` saves every request to `results/<name>.jsonl` and prints a summary.

1. Apply the policy which routes across the local workers only:

    ```bash
    kubectl apply -f policies/local-only.yaml
    ```

2. Restart the workers so neither run inherits the other's cache, then run the [K]inference side with 24 shared prompts of about 8,000 tokens:

    ```bash
    kubectl rollout restart deploy/vllm && kubectl rollout status deploy/vllm
    ./loadgen/run.sh kinference-p24 --url http://llm-gw-gatewayd \
    --workload shared-prefix --prefixes 24 --concurrency 8
    ```

3. Restart the workers again, then run the plain `Service` side, which needs the full model name:

    ```bash
    kubectl rollout restart deploy/vllm && kubectl rollout status deploy/vllm
    ./loadgen/run.sh service-p24 --url http://vllm:8000 --model Qwen/Qwen3-8B-FP8 \
    --workload shared-prefix --prefixes 24 --concurrency 8
    ```

4. Repeat with `--prefixes 8`, `--prefixes 48`, or `--workload unique` to change how much of the traffic one worker's cache can hold.
5. Check that [K]inference is using the KV cache at all. In another terminal run `kubectl port-forward svc/kinference 9001:9001`, then:

    ```bash
    curl -s localhost:9001/metrics | grep kinference_tokenize_total
    ```

    Requests should be counted under `path="local"`. If they are under `path="unavailable"`, [K]inference is picking workers on load alone.

**What we saw** (requests a minute at 8 clients):

| Traffic           | [K]inference | Plain `Service` |
| ----------------- | ------------ | --------------- |
| 8 shared prompts  | 86.7         | 86.7            |
| 24 shared prompts | 45.3         | 35.7            |
| 48 shared prompts | 36.3         | 37.0            |
| Unique prompts    | 35.7         | 28.7            |

Eight prompts fit in every worker's cache, so random routing hits a warm cache too. Twenty-four outgrow one worker's cache but fit the pool's, which is where [K]inference helped most. 48 outgrow the pool. On unique prompts, [K]inference's queue-aware balancing still served more.

## Demo 3 - A Noisy Neighbour

Demo 3 measures one interactive tenant's latency on its own, beside a batch tenant flooding the pool, and then with a policy which makes the batch tenant yield.

1. Apply the local-only policy and measure the interactive tenant on its own:

    ```bash
    kubectl apply -f policies/local-only.yaml
    ./loadgen/run.sh quiet-alone --url http://llm-gw-gatewayd --tenant interactive \
    --workload shared-prefix --prompt-words 1500 --concurrency 2
    ```

2. Start a batch flood in the background, give it 30 seconds, then measure the interactive tenant again:

    ```bash
    ./loadgen/run.sh flood --url http://llm-gw-gatewayd --tenant batch \
    --workload unique --concurrency 48 --max-tokens 512 --duration 260 --warmup 0 &
    sleep 30
    ./loadgen/run.sh quiet-flooded --url http://llm-gw-gatewayd --tenant interactive \
    --workload shared-prefix --prompt-words 1500 --concurrency 2
    wait
    ```

3. Apply the batch-yields policy, which skips any worker with more than one prompt queued or a cache over 60% full for the `batch` tenant, and rejects the request when none is left. Then repeat step 2, with the names changed to `flood-yields` and `quiet-yields`:

    ```bash
    kubectl apply -f policies/batch-yields.yaml
    ```

**What we saw:** the interactive tenant's median time to first token was 0.1 seconds on its own, 59 seconds beside the batch flood, and 1.4 seconds with the batch-yields policy. The batch tenant still got through 86% of its earlier work, but only by receiving thousands of 403s, because the load generator retries without backoff. [K]inference `0.1.0-alpha.8` has no rate limiting yet, so a policy like this is the nearest tool.

## Demo 4 - Restarting [K]inference Under Load

Demo 4 restarts the single [K]inference replica while steady traffic is running, and counts the failed requests.

1. Start five minutes of steady traffic in the background:

    ```bash
    ./loadgen/run.sh steady --url http://llm-gw-gatewayd --workload shared-prefix \
    --concurrency 8 --duration 300 --warmup 0 &
    ```

2. After about 90 seconds, restart [K]inference and wait for it to come back:

    ```bash
    kubectl rollout restart deploy/kinference && kubectl rollout status deploy/kinference
    ```

3. When the traffic finishes, list the failed requests and when they were sent, in seconds from the start:

    ```bash
    wait
    jq -c 'select(.status != null and .status != 200) | {t, status}' results/steady.jsonl
    ```

**What we saw:** [K]inference was back in about 8 seconds, and 8 of 414 requests failed with a 500, all in the same 10-second window. The chart runs one replica with a `Recreate` strategy, so every tenant sees the restart.

The load generator does not retry, so these are the failures a client without retries would see. The OpenAI and Anthropic SDKs retry twice by default with a short backoff, which would not cover an 8-second gap; a retry at the gateway would, and is safe here because the requests never reached a GPU.

## Clean up

On kind:

```bash
kind delete cluster --name kinference-demo
```

On EKS, which stops the hourly cost:

```bash
eksctl delete cluster -f clusters/eks.yaml --disable-nodegroup-eviction --wait
```

## Things We Hit Along the Way

- **[K]inference's default tokenisation does not work with vLLM 0.31.0.** The chart asks vLLM's `/render` routes for token IDs, and those return 404, so [K]inference silently picks workers on load alone. The only signs are a `WARN` in its log and `kinference_tokenize_total{path="unavailable"}`. `values/kinference.yaml` sets `tokenize.mode: local` to fix it.
- **A `Service` named `vllm` stops vLLM from starting.** This is a known clash, and vLLM's error message points to its docs: Kubernetes injects `VLLM_PORT=tcp://...` into every pod for a `Service` of that name, and vLLM reads it as its own setting. The demo chart sets `enableServiceLinks: false`; naming the `Service` something else works too.
- **vLLM needs more `/dev/shm` than the 64 MiB container default.** This is standard for vLLM and PyTorch: they share memory between processes, and vLLM's own Kubernetes guide mounts a memory-backed `emptyDir` at `/dev/shm`. The demo chart does the same, capped at 2 GiB, because that memory counts against the pod.
- **Install the NVIDIA device plugin yourself.** eksctl adds one automatically, but only after the whole node group is ready. When `g5.xlarge` capacity ran short in our zone, two GPU nodes were running with their GPUs invisible. The setup installs the plugin with Helm instead, which is the usual approach. Pass `--install-nvidia-plugin=false` to `eksctl create cluster` so you do not end up with two, and spread the GPU nodes across zones if capacity is tight.
- **The gateway Service is `ClusterIP` on purpose.** The endpoint has no authentication, so the demo chart keeps it off the internet, and the load generator runs inside the cluster.
- **[K]inference's policy status is worth reading.** It warned us, with the fix, when an exclusion used a term that only applies to local workers.
