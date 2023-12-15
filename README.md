# Tink

Testing In Kubernetes.

k3d cluster create three-node-cluster -p "31690:31690@agent:0"  --agents 2

helm upgrade --install apisix apisix/apisix --version 1.3.1  --create-namespace --namespace apisix --set gateway.http.nodePort=31690 --set dashboard.enabled=true --set ingress-controller.enabled=true --set ingress-controller.config.apisix.serviceNamespace=apisix

{
  "key": "admin",
  "header": "Authorization"
}
