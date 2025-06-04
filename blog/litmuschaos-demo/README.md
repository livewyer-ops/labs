# litmuschaos-demo

This demo was tested with litmuschaos `v1.13.0`.

## Install the Litmuschaos Operator

```bash
helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/
kubectl create ns litmus
helm install chaos litmuschaos/litmus --namespace=litmus
```

## Install the Chaos Experiments

```bash
kubectl create ns $DEMO-NAMESPACE
kubectl apply -f https://hub.litmuschaos.io/api/chaos/1.13.0?file=charts/generic/experiments.yaml -n $DEMO-NAMESPACE
```

## Deploy the Demo Chart

```bash
helm install $RELEASE_NAME ./demo-chart -n $DEMO-NAMESPACE
```

## Run the Helm Chart Test

```bash
helm test $RELEASE_NAME -n $DEMO-NAMESPACE --logs --debug
```

## References

* <https://docs.litmuschaos.io/docs/getstarted/>
* <https://helm.sh/docs/intro/install/>
* <https://helm.sh/docs/topics/chart_tests/>
