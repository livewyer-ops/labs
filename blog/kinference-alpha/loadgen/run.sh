#!/usr/bin/env bash
# Runs loadgen.py as a Job inside the cluster, waits for it, saves every
# request to results/<name>.jsonl, and prints the summary line.
#
#   loadgen/run.sh <name> [loadgen.py arguments...]
#   loadgen/run.sh kinference-p24 --url http://llm-gw-gatewayd --workload shared-prefix --prefixes 24
set -euo pipefail
name=$1; shift
here=$(dirname "$0")

kubectl create configmap loadgen --from-file=loadgen.py="$here/loadgen.py" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl delete job "lg-$name" --ignore-not-found >/dev/null
args=$(printf '"%s",' --label "$name" "$@"); args=${args%,}

kubectl apply -f - >/dev/null <<EOF
apiVersion: batch/v1
kind: Job
metadata: { name: lg-$name }
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: loadgen
          image: python:3.13-slim
          command: ["python", "-u", "/app/loadgen.py", $args]
          volumeMounts: [{ name: app, mountPath: /app }]
      volumes: [{ name: app, configMap: { name: loadgen } }]
EOF

kubectl wait --for=condition=complete "job/lg-$name" --timeout=3600s >/dev/null
mkdir -p results
kubectl logs "job/lg-$name" > "results/$name.jsonl"
tail -1 "results/$name.jsonl"
