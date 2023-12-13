# Tink

Testing In Kubernetes.

helm upgrade --install apisix apisix/apisix --version 1.3.1  --create-namespace --namespace apisix --set gateway.http.nodePort=31690 --set dashboard.enabled=true --set ingress-controller.enabled=true --set ingress-controller.config.apisix.serviceNamespace=apisix

{
  "username": "admin",
  "plugins": {
    "key-auth": {
      "_meta": {
        "disable": false
      },
      "key": "admin"
    }
  }
}
