# Linux 环境部署与演示操作说明

本文以 Ubuntu 22.04/24.04 为例，说明如何在 Linux 主机上部署并演示流体网络求解项目。项目使用 Docker Compose 启动前端静态页面和后端分析 API。

## 1. 环境要求

- Linux x86_64 或 arm64
- Docker Engine 24 或更高版本
- Docker Compose v2（`docker compose` 命令）
- 可访问 Docker Hub 的网络
- 演示机器开放 TCP 8080；如需直接访问 API，再开放 TCP 8000

检查环境：

```bash
uname -m
docker --version
docker compose version
```

Ubuntu 可按 Docker 官方仓库安装 Docker Engine 和 Compose 插件。安装完成后，将当前用户加入 docker 组：

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

## 2. 获取项目

```bash
git clone <GITHUB_REPOSITORY_URL> fluid-network
cd fluid-network
```

也可以把项目目录复制到 Linux 主机后直接进入该目录。确认关键文件存在：

```bash
test -f Dockerfile && test -f docker-compose.yml && test -f examples/demo_network.toml
```

## 3. 构建并启动容器

```bash
docker compose up -d --build
docker compose ps
```

项目启动两个服务：`fluid-network` 提供 8080 前端页面，`fluid-network-api` 提供 8000 求解和分析 API。两个服务应处于 `Up` 或 `running` 状态。

## 4. 部署验证

```bash
curl -I http://127.0.0.1:8080/
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/scenarios/normal
curl http://127.0.0.1:8000/api/scenarios/cooling_off
```

健康检查预期输出：

```json
{"status": "ok", "service": "fluid-network"}
```

正常工况可靠性应为 `1.0`；关闭冷却阀的工况中 cooling 功能应为 `functional: false`。

## 5. 浏览器访问

Linux 图形界面浏览器访问：

```text
http://localhost:8080
```

远程服务器先获取 IP：

```bash
hostname -I
```

然后在演示电脑访问：

```text
http://<SERVER_IP>:8080
```

云服务器或防火墙需要放行 TCP 8080；只有需要从外部直接调用 API 时才放行 TCP 8000。

## 6. 演示流程

1. 打开页面，展示网络拓扑。
2. 选择 `normal` 工况，说明节点压力、管路流量、流速和功能可靠性。
3. 选择 `cooling_off` 工况，说明冷却支路关闭，冷却功能变为不可用。
4. 用 API 展示后端计算结果：

   ```bash
   curl -s http://127.0.0.1:8000/api/scenarios/normal | python3 -m json.tool
   ```

5. 在容器内执行 CLI：

   ```bash
   docker compose exec fluid-network fluid-network validate examples/demo_network.toml
   docker compose exec fluid-network fluid-network analyze examples/demo_network.toml --scenario normal
   ```

## 7. 查看日志与排查

```bash
docker compose logs --tail=100
docker compose logs -f
```

常见问题：

- 端口被占用：`sudo ss -ltnp | grep -E ':8080|:8000'`，停止冲突服务或修改 Compose 左侧端口。
- 容器未启动：查看对应服务日志。
- 无法拉取基础镜像：检查 Docker Hub 网络、代理和 DNS，重试 `docker pull python:3.12-slim`。
- 页面无数据：确认 `web/data/index.json`、`normal.json` 和 `cooling_off.json` 存在，并重新构建。
- 远程无法访问：确认服务器防火墙、安全组和云平台入站规则放行 8080。

## 8. 停止、重启和清理

```bash
docker compose down
docker compose up -d
docker compose down
docker compose up -d --build
```

## 9. 演示结束验收清单

- `docker compose ps` 中两个服务均为运行状态
- 8080 返回页面
- 8000 健康检查返回 `status: ok`
- `normal` 工况可靠性为 100%
- `cooling_off` 工况显示冷却功能失效
- 日志无持续报错
- 演示结束后执行 `docker compose down`
