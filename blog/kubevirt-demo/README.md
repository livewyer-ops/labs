# kubevirt-demo

- [kubevirt-demo](#kubevirt-demo)
  - [Kubernetes Cluster Setup](#kubernetes-cluster-setup)
    - [Kind Cluster](#kind-cluster)
    - [Install Kubevirt's Operator and Custom Resource Definitions](#install-kubevirts-operator-and-custom-resource-definitions)
    - [Install Kubevirt's Containerized Data Importer](#install-kubevirts-containerized-data-importer)
  - [Deployment](#deployment)
    - [Ubuntu 20.04 VM](#ubuntu-2004-vm)
      - [Import the Ubuntu 20.04 Cloud Image](#import-the-ubuntu-2004-cloud-image)
      - [Deploy the Ubuntu VM using the DataVolume](#deploy-the-ubuntu-vm-using-the-datavolume)
      - [Connect to the Console of the Ubuntu VMI](#connect-to-the-console-of-the-ubuntu-vmi)
      - [Possible Issue](#possible-issue)

## Kubernetes Cluster Setup

### Kind Cluster

Setup Local Kubernetes Cluster with Kind Cluster

```bash
kind create cluster --config examples/kind-cluster/kind-multi-node.yaml
```

### Install Kubevirt's Operator and Custom Resource Definitions

This demo was tested with kubevirt version v0.38.1. You may choose to run `export VERSION=v0.38.1` instead of the export command below.

```bash
export VERSION=$(curl -s https://api.github.com/repos/kubevirt/kubevirt/releases | grep tag_name | grep -v -- '-rc' | head -1 | awk -F': ' '{print $2}' | sed 's/,//' | xargs)
echo $VERSION
kubectl create -f https://github.com/kubevirt/kubevirt/releases/download/${VERSION}/kubevirt-operator.yaml
kubectl create -f https://github.com/kubevirt/kubevirt/releases/download/${VERSION}/kubevirt-cr.yaml
```

Wait until the kubevirt status is `Deployed`

```bash
kubectl get all -n kubevirt
```

### Install Kubevirt's Containerized Data Importer

This demo was tested with CDI version v1.30.0. You may choose to run `export VERSION=v1.30.0` instead of the export command below.

```bash
export VERSION=$(curl -s https://github.com/kubevirt/containerized-data-importer/releases/latest | grep -o "v[0-9]\.[0-9]*\.[0-9]*")
kubectl create -f https://github.com/kubevirt/containerized-data-importer/releases/download/$VERSION/cdi-operator.yaml
kubectl create -f https://github.com/kubevirt/containerized-data-importer/releases/download/$VERSION/cdi-cr.yaml
```

## Deployment

### Ubuntu 20.04 VM

#### Import the Ubuntu 20.04 Cloud Image

Open the `examples/ubuntu/data-volume.yaml` file and confirm the URL for the cloud image still exists at <https://cloud-images.ubuntu.com/>.
If it doesn't exist you'll have to update it.

If it exists, import the disk image using a `DataVolume`

```bash
kubectl apply -f examples/ubuntu/data-volume.yaml
```

Wait for the import process to complete

```bash
kubectl get datavolume
```

#### Deploy the Ubuntu VM using the DataVolume

```bash
kubectl apply -f examples/ubuntu/vm.yaml
```

Check the Virtual Machine Instance (VMI) has been created

```bash
kubectl get vm, vmi, pod
```

#### Connect to the Console of the Ubuntu VMI

```bash
kubectl virt connect ubuntuvm
```

Login with the `ubuntu` user. The user details can be found in the `examples/ubuntu/vm.yaml`. You'll have to decode the value of `userDataBase64` with `echo "<STRING> | base64 --decode`.

#### Possible Issue

After connecting to the console, you may get the following error that usually shows up if you delete a VM and recreate it using the same `DataVolume`

*Error check 1*

```bash
ubuntu@ubuntuvm:~$ ping 8.8.8.8
ping: connect: Network is unreachable
```

*Error check 2*

```bash
ubuntu@ubuntuvm:~$ ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: enp1s0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 6a:84:90:ca:0a:41 brd ff:ff:ff:ff:ff:ff
root@ubuntuvm:~#
```

Take note of the mac address, it is next to `link/ether`. In this example it is `6a:84:90:ca:0a:41`

*Error check 3*

```bash
root@ubuntuvm:~# netplan try
Warning: Stopping systemd-networkd.service, but it can still be activated by:
  systemd-networkd.socket
[]
Cannot find unique matching interface for enp1s0: {'macaddress': '8a:ff:02:a4:29:e4'}
Do you want to keep these settings?


Press ENTER before the timeout to accept the new configuration
```

To solve the error, you need edit the contents of the `/etc/netplan/50-cloud-init.yaml` and replace the mac address with the correct one. Once `netplan try` shows no errors you can run `network apply` to apply the fix.
