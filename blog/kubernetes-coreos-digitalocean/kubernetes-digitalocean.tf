resource "digitalocean_droplet" "master" {
    image = "coreos-alpha"
    name = "master"
    region = "lon1"
    size = "512mb"
    private_networking = true
    user_data = "${file("kubernetes-digitalocean-master.yaml")}"
    ssh_keys = [
      "${var.ssh_fingerprint}"
    ]
}
# Create a new domain record
resource "digitalocean_domain" "default" {
    name = "master.example.com"
    ip_address = "${digitalocean_droplet.master.ipv4_address_private}"
}
resource "digitalocean_droplet" "node-01" {
    image = "coreos-alpha"
    name = "node-01"
    region = "lon1"
    size = "16gb"
    private_networking = true
    user_data = "${file("kubernetes-digitalocean-node.yaml")}"
    ssh_keys = [
      "${var.ssh_fingerprint}"
    ]
}
resource "digitalocean_droplet" "node-02" {
    image = "coreos-alpha"
    name = "node-02"
    region = "lon1"
    size = "16gb"
    private_networking = true
    user_data = "${file("kubernetes-digitalocean-node.yaml")}"
    ssh_keys = [
      "${var.ssh_fingerprint}"
    ]
}
resource "digitalocean_droplet" "node-03" {
    image = "coreos-alpha"
    name = "node-03"
    region = "lon1"
    size = "16gb"
    private_networking = true
    user_data = "${file("kubernetes-digitalocean-node.yaml")}"
    ssh_keys = [
      "${var.ssh_fingerprint}"
    ]
}
