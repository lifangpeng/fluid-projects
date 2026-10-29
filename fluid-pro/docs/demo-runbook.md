# Linux / Docker 演示手册

## 本机运行

```bash
python3 -m pip install -e '.[dev]'
PYTHONPATH=src python3 -m pytest -q
PYTHONPATH=src python3 -m fluid_network.cli validate examples/demo_network.toml
PYTHONPATH=src python3 -m fluid_network.cli export examples/demo_network.toml --out web/data
python3 -m http.server 8080 --directory web
```

访问 `http://localhost:8080`，切换 `normal` 和 `cooling_off`。正常工况应显示可靠性 100%；关闭冷却阀后 cooling 功能失效。

## Docker 运行

```bash
docker compose up --build -d
curl http://localhost:8080/
docker compose logs
```

结束演示：`docker compose down`。
