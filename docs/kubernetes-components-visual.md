# Kubernetes Components Visual

This diagram shows the basic Kubernetes components and how a request becomes a running container.

## Cluster Diagram

```mermaid
flowchart TB
  user["User / CI / Terraform / kubectl"]

  subgraph controlPlane["Control Plane - decides and records cluster state"]
    api["kube-apiserver<br/>front door to Kubernetes"]
    etcd["etcd<br/>cluster database / source of truth"]
    scheduler["kube-scheduler<br/>chooses which node runs a Pod"]
    controller["kube-controller-manager<br/>keeps desired state true"]
  end

  subgraph nodeA["Worker Node A - runs workloads"]
    kubeletA["kubelet<br/>node agent"]
    proxyA["kube-proxy<br/>Service networking"]
    runtimeA["container runtime<br/>containerd / CRI-O"]
    podA1["Pod<br/>app container"]
    podA2["Pod<br/>worker container"]
  end

  subgraph nodeB["Worker Node B - runs workloads"]
    kubeletB["kubelet<br/>node agent"]
    proxyB["kube-proxy<br/>Service networking"]
    runtimeB["container runtime<br/>containerd / CRI-O"]
    podB1["Pod<br/>app container"]
  end

  service["Service<br/>stable virtual IP / DNS name"]
  traffic["Client traffic"]

  user -->|"apply / get / delete"| api
  api <-->|"read / write state"| etcd
  controller -->|"watches desired state"| api
  controller -->|"creates Pods when needed"| api
  scheduler -->|"watches unscheduled Pods"| api
  scheduler -->|"binds Pod to a node"| api

  api -->|"Pod assigned to Node A"| kubeletA
  api -->|"Pod assigned to Node B"| kubeletB
  kubeletA -->|"start / stop containers"| runtimeA
  kubeletB -->|"start / stop containers"| runtimeB
  runtimeA --> podA1
  runtimeA --> podA2
  runtimeB --> podB1
  kubeletA -->|"reports status"| api
  kubeletB -->|"reports status"| api

  traffic --> service
  service --> proxyA
  service --> proxyB
  proxyA --> podA1
  proxyA --> podA2
  proxyB --> podB1
```

## Request Flow

```mermaid
sequenceDiagram
  participant U as User / kubectl
  participant API as kube-apiserver
  participant DB as etcd
  participant C as controller-manager
  participant S as scheduler
  participant K as kubelet
  participant R as container runtime

  U->>API: apply Deployment
  API->>DB: store desired state
  C->>API: notice Deployment needs Pods
  C->>API: create Pod objects
  S->>API: watch unscheduled Pods
  S->>API: assign Pod to a node
  K->>API: watch Pods assigned to this node
  K->>R: pull image and start container
  K->>API: report Pod status
```

## Mental Model

```text
User/kubectl
    |
    v
kube-apiserver <----> etcd
    |
    +--> controllers create or repair resources
    |
    +--> scheduler picks a node for each new Pod
    |
    v
kubelet on selected node
    |
    v
container runtime
    |
    v
running Pod

kube-proxy runs on each node and helps Service traffic reach the right Pods.
```

## Component Legend

- `kube-apiserver`: the front door. All Kubernetes requests go through it.
- `etcd`: the database. Stores the cluster source of truth.
- `kube-scheduler`: the placement engine. Decides which node should run a Pod.
- `kube-controller-manager`: the reconciliation engine. Keeps actual state matching desired state.
- `kubelet`: the node agent. Starts Pods assigned to its node and reports status.
- `container runtime`: the actual container runner, usually `containerd` or `CRI-O`.
- `kube-proxy`: the Service networking helper. Routes Service traffic to backend Pods.
- `Pod`: the smallest deployable unit in Kubernetes. Usually wraps one main app container.
- `Service`: a stable network identity for a changing set of Pods.

## One-Sentence Version

You tell the `kube-apiserver` what you want, `etcd` remembers it, controllers create missing objects, the scheduler chooses a node, the kubelet starts the containers, and kube-proxy helps network traffic reach them.
