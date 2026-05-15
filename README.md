![labs](https://github.com/user-attachments/assets/856f1491-1aff-48a4-9f31-3ede2a093b50)
<h1 align="center">LiveWyer Labs</h1>

At [LiveWyer](https://livewyer.io), we believe that solving complex challenges starts with curiosity and a commitment to growth. That’s why we’ve formalised our internal R&D efforts into LiveWyer Labs. This is now our public GitHub space where we can share our innovation, deep technical exploration, and continuous learning in the [Cloud Native and Open Source](https://livewyer.io/blog/cloud-native-is-not-the-destination.-its-the-journey/) world.

**Table of Contents**

- [Contributions](#contributions)
  - [CNOE Azure](#cnoe-azure)
  - [CNOE GCP](#cnoe-gcp)
  - [CNOE AI](#cnoe-ai)
  - [Crossplane Piraeus](#crossplane-piraeus)
- [livewyer.io Tutorial Series](#livewyerio-tutorial-series)
  - [Kubernetes HPA](#kubernetes-hpa)
  - [KEDA series](#keda-series)
  - [Kubernetes Vertical Pod Autoscaler](#kubernetes-vertical-pod-autoscaler)
  - [Kubernetes Autoscaling with Datadog](#kubernetes-autoscaling-with-datadog)
- [livewyer.io Blog posts](#livewyerio-blog-posts)
  - [Istio vs Linkerd vs Cilium](#istio-vs-linkerd-vs-cilium)
  - [Is Istio Ambient worth it?](#is-istio-ambient-worth-it)
  - [LitmusChaos](#litmuschaos)
  - [KubeVirt](#kubevirt)
  - [Kubernetes on DigitalOcean](#kubernetes-on-digitalocean)
  - [Docker and Apache Aurora](#docker-and-apache-aurora)
  - [Mesos in Docker on CoreOS](#mesos-in-docker-on-coreos)
- [Contributing](#contributing)

## Contributions

### CNOE Azure

A reference implementation of Cloud Native Operational Excellence and its toolings on Azure

[[Code]](https://github.com/livewyer-ops/cnoe-reference-implementation-azure)

### CNOE GCP

A reference implementation of Cloud Native Operational Excellence and its toolings on Google Compute Cloud

[[Code]](https://github.com/livewyer-ops/cnoe-reference-implementation-gcp)

### CNOE AI

Contributing to CAIPE (Community AI Platform Engineering), an open source project building multi-agent systems for AI-assisted platform engineering workflows.

[[Code]](https://github.com/cnoe-io/ai-platform-engineering)

### Crossplane Piraeus

Crossplane Composite Resource Definitions (XRDs) package for Piraeus / Linbit Datastore on Kubernetes

[[Code]](https://github.com/livewyer-ops/crossplane-configuration-piraeus)

## livewyer.io Tutorial Series

Our tutorial series are in-depth, multi-part guides covering key topics in the Cloud Native landscape. Each series walks through concepts, configuration, and hands-on examples, from foundational principles through to production-ready implementation patterns. They are written to remain relevant over time and are periodically reviewed to reflect changes in the tools, projects, and practices they cover. The full index is available at [livewyer.io/tutorials](https://livewyer.io/tutorials/).

### Kubernetes HPA

A four-part series introducing Horizontal Pod Autoscaling in Kubernetes, covering built-in CPU / memory metrics, custom and external metrics via Metrics Adapters, and scaling with Prometheus using the Prometheus Adapter.

[[Blog 1]](https://livewyer.io/blog/introduction-to-horizontal-pod-autoscaling-in-kubernetes/) | [[Blog 2]](https://livewyer.io/blog/how-to-use-custom-external-metrics-for-kubernetes-hpa/) | [[Blog 3]](https://livewyer.io/blog/set-up-kubernetes-scaling-via-prometheus-custom-metrics/) | [[Blog 4]](https://livewyer.io/blog/leveraging-kubernetes-hpa-and-prometheus-adapter/)

### KEDA series

A four-part series introducing the CNCF project Kubernetes Event-driven Autoscaling (KEDA), a tool built on top of the Kubernetes Horizontal Pod Autoscaler (HPA) without replacing it. The series covers KEDA concepts and installation, scaling workloads with the Prometheus scaler, and autoscaling jobs with the Redis List scaler.

[[Blog 1]](https://livewyer.io/blog/introducing-kubernetes-event-driven-autoscaling-keda/) | [[Blog 2]](https://livewyer.io/blog/getting-started-with-autoscaling-in-kubernetes-with-keda/) | [[Blog 3]](https://livewyer.io/blog/autoscaling-workloads-with-keda-and-the-prometheus-scaler/) | [[Blog 4]](https://livewyer.io/blog/autoscaling-jobs-with-kedas-redis-list-scaler/) | [[Code]](./blog/keda/)

### Kubernetes Vertical Pod Autoscaler

A four-part series covering Kubernetes Vertical Pod Autoscaling from first principles through to production deployment. The series explains why manual resource allocation falls short, performs a deep dive into the VPA Recommender, Updater, and Admission Controller components, covers safe production rollout strategies, and concludes with advanced configuration patterns and ecosystem tooling.

[[Blog 1]](https://livewyer.io/blog/understanding-kubernetes-vpa-why-manual-resource-allocation-is-costing-you-thousands/) | [[Blog 2]](https://livewyer.io/blog/vpa-component-deep-dive-how-kubernetes-vertical-pod-autoscaler-works/) | [[Blog 3]](https://livewyer.io/blog/vpa-production-deployment-avoiding-pitfalls-for-safe-and-effective-scaling/) | [[Blog 4]](https://livewyer.io/blog/advanced-vpa-implementation-production-patterns-ecosystem-tools-and-real-world-configuration/)

### Kubernetes Autoscaling with Datadog

A three-part series on scaling Kubernetes workloads with Datadog metrics. The series covers getting started with the Datadog Cluster Agent and HPA, scaling with Datadog external metrics, and consolidating autoscaling with the DatadogPodAutoscaler CRD.

[[Blog 1]](https://livewyer.io/blog/kubernetes-autoscaling-getting-started-with-datadog/) | [[Blog 2]](https://livewyer.io/blog/kubernetes-autoscaling-with-datadog-external-metrics/) | [[Blog 3]](https://livewyer.io/blog/kubernetes-autoscaling-using-the-datadogpodautoscaler/)

## livewyer.io Blog posts

These posts are carefully curated to provide practical examples and insights into the topics we explored. Whether you're looking for inspiration, learning, or contributing, this list serves as a hub for developers to dive deeper into the ideas and technologies covered in our writings.

### Istio vs Linkerd vs Cilium

(2024) Service Meshes Decoded: compare the performance of Istio, Linkerd, and Cilium to choose the best service mesh for Kubernetes.

[[Blog]](https://livewyer.io/blog/service-meshes-decoded-istio-vs-linkerd-vs-cilium/) | [[Code]](https://github.com/livewyer-ops/poc-servicemesh2024)

### Is Istio Ambient worth it?

(2024) Service Meshes Decoded: Explore Istio Ambient and evaluate its features, benefits, and value in Kubernetes Platform environments.

[[Blog]](https://livewyer.io/blog/service-meshes-decoded-is-istio-ambient-worth-it/) | [[Code]](https://github.com/livewyer-ops/poc-servicemesh2024)

### LitmusChaos

(2021) Explore how LitmusChaos uses Helm charts to enable chaos engineering for resilient Kubernetes systems.

[[Blog]](https://livewyer.io/blog/litmuschaos-chaos-engineering-with-helm-chart-test-suite/) | [[Code]](./blog/litmuschaos-demo/)

### KubeVirt

(2021) Learn how KubeVirt enables Kubernetes clusters to run virtualised workloads within Kubernetes itself.

[[Blog]](https://livewyer.io/blog/kubevirt-running-kubernetes-clusters-inside-kubernetes/) | [[Code]](./blog/kubevirt-demo/)

### Kubernetes on DigitalOcean

(2015) Learn how to deploy Kubernetes on DigitalOcean for scalable, efficient, and cost-effective applications.

[[Blog]](https://livewyer.io/blog/deploy-kubernetes-on-digitalocean-a-beginner-friendly-guide/) | [[Code]](./blog/kubernetes-coreos-digitalocean/)

### Docker and Apache Aurora

(2015) Discover how to deploy Docker containers efficiently using Apache Aurora for scalable applications.

[[Blog]](https://livewyer.io/blog/deploy-docker-containers-with-apache-aurora-quick-guide/) | [[Code]](./blog/aurora-web-containers/)

### Mesos in Docker on CoreOS

(2015) Learn how to set up Apache Mesos in Docker on CoreOS with a concise guide for cluster management.

[[Blog]](https://livewyer.io/blog/running-apache-mesos-in-docker-on-coreos-a-beginners-guide/) | [[Code]](./blog/mesos-coreos-cluster/)

## Contributing

We value your feedback and suggestions!
If you have any ideas or want to report issues, please create an [issue](https://github.com/livewyer-ops/labs/issues/new/choose).
Additionally, you can submit your contributions by opening a [pull request](https://github.com/livewyer-ops/labs/pulls).

> [!IMPORTANT]
> Unless required by applicable law or agreed to in writing, software distributed under the [License](LICENSE) is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the [License](LICENSE) for the specific language governing permissions and limitations.

<p align="center">
  <a href="http://livewyer.io" target="_blank">
    <picture>
      <!-- lw-city-banner-dark -->
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/6a3fe769-410a-40db-9dcb-3bc2eb440219">
      <!-- lw-city-banner-light -->
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/dcd3324a-2688-43cb-bce2-2bc50d71209c">
      <img alt="LiveWyer logo" src="https://github.com/user-attachments/assets/dcd3324a-2688-43cb-bce2-2bc50d71209c">
    </picture>
  </a>
</p>

Copyright © 2012-2025 LiveWyer, Licensed under the `MIT` [License](LICENSE).
