# Fluid Network Solver

稳态不可压缩流体网络的 TOML 驱动求解、工况分析和静态可视化示例。

## 快速运行

```bash
python3 -m pip install -e '.[dev]'
fluid-network validate examples/demo_network.toml
fluid-network analyze examples/demo_network.toml --scenario normal
fluid-network export examples/demo_network.toml --out web/data
python3 backend_server.py --port 8080
```

打开 http://localhost:8080，可切换 `normal` 与 `cooling_off` 工况。

运行测试：

```bash
pytest -q
```

## Docker

```bash
docker compose up --build
```

求解器支持线性 `ΔP=R·Q` 和二次 `ΔP=R·Q·|Q|` 阻力模型；结果包含收敛状态、压力、流量、流速和诊断信息。当前版本使用显式列出的 scenarios，避免遍历全部控制组合。

网页通过同源 API 实时切换阀门；也可用 `python3 -m http.server 8080 --directory web` 查看预计算结果。需要 Python 3.11+。`reliability` 表示当前工况功能通过率，不是概率可靠度。

发布前剩余事项见 [发布验收清单](docs/release-checklist.md)。
