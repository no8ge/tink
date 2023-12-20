# Tink

Testing In Kubernetes，在 K8s 中管理自动化测试。

## 功能

轻松管理测试工作负载([`plugin`](https://github.com/no8ge/plugins "plugin"))

## 要求

- Kubernetes

## 快速开始

### 构建 plugin

> 参考 [`plugin`](https://github.com/no8ge/plugins "plugin")

### 部署环境

> 参考 [`快速开始`](https://github.com/no8ge/atop?tab=readme-ov-file#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B)

### 添加仓库

```shell
# request
curl -X POST -H "Content-Type: application/json" -H "Authorization: admin" http://192.168.228.5:31690/tink/v1.0/repo -d '
{  
  "name":"test",
  "url":"https://no8ge.github.io/chartrepo"
}'

# response:
{
    "outs":"\"test\" has been added to your repositories\n",
    "errs":""
}
```

### 安装 plugin

```shell
# request
curl -X POST -H "Content-Type: application/json" -H "Authorization: admin" http://192.168.228.5:31690/tink/v1.0/chart -d '
{
  "release": "278a0e0f-08a4-47b1-a4a8-582b21fcf694",
  "chart": "pytest",
  "repo": "test",
  "namespace": "default",
  "version": "1.0.0",
  "value": {"command": "pytest --html=report/index.html -s -v; sleep 3600"}
}'

# response:
{
    "outs":{
        "name":"278a0e0f-08a4-47b1-a4a8-582b21fcf694",
        "info":{
            "first_deployed":"2023-12-15T12:37:35.864758824Z",
            "last_deployed":"2023-12-15T12:37:35.864758824Z",
            "deleted":"",
            "description":"Install complete",
            "status":"deployed"
        },
        "config":{
            "command":"pytest --html=report/report.html -s -v; sleep 3600"
        },
        "version":1,
        "namespace":"default"
    },
    "errs":""
}

# status
~ kubectl get pod -A |grep 278a0e0f-08a4-47b1-a4a8-582b21fcf694                              
NAME                                          READY   STATUS      RESTARTS   AGE
pytest-091143e5-464e-4704-8438-04ecc98f4b1a   0/1     Completed   0          86s

```

### 更新 plugin

```shell
curl -X PATCH -H "Content-Type: application/json" -H "Authorization: admin" http://192.168.228.5:31690/tink/v1.0/chart -d '
{
  "release": "278a0e0f-08a4-47b1-a4a8-582b21fcf694",
  "chart": "pytest",
  "repo": "test",
  "namespace": "default",
  "version": "1.0.0",
  "value": {"command": "pytest --html=report/index.html -s -v; sleep 3600"}
}'
```

### 卸载 plugin

```shell
curl -X DELETE -H "Content-Type: application/json" -H "Authorization: admin" http://192.168.228.5:31690/tink/v1.0/chart -d '
{
  "release": "278a0e0f-08a4-47b1-a4a8-582b21fcf694",
  "chart": "pytest",
  "repo": "test",
  "namespace": "default",
  "version": "1.0.0",
  "value": {"command": "pytest --html=report/index.html -s -v; sleep 3600"}
}'
```
