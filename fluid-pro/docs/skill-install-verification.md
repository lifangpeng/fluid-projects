# Skill 独立安装验证记录

日期：2026-10-29（Asia/Shanghai）
结果：通过，验证范围为“独立 Skill 目录 + 显式安装的项目依赖”。

## 隔离方式

- 使用全新 `python:3.12-slim` Linux 容器，不复用运行中的项目容器。
- 宿主项目以只读方式挂载到 `/input`；复制源文件到容器临时目录，排除虚拟环境、缓存、egg-info 和构建产物。
- Skill 单独复制到 `/tmp/skill-install-verification/skills/fluid-network`。
- 按 SKILL.md 执行 `python -m pip install -e <项目目录>`。
- 从 `/tmp/skill-install-verification/work` 执行 CLI，没有设置 PYTHONPATH，不使用宿主机安装的包。
- 验证结束自动删除容器；不修改本机 Skill 安装目录和现有服务。

## 验证内容

| 检查 | 结果 |
|---|---|
| Skill frontmatter 与相对文件引用 | 通过 |
| 从 Skill 包内复制示例 TOML | 通过 |
| 安装项目并使用 fluid-network 命令 | 通过 |
| validate / solve / analyze / export | 通过 |
| --json 写文件并解析 | 通过 |
| 正常工况功能通过率 1.0 | 通过 |
| 关闭冷却阀功能通过率 0.5、不可达、零流量 | 通过 |
| 流量与独立串并联解析解比较 | 通过，rtol=1e-6、atol=1e-10 |
| 静态 HTML、JS、CSS、索引和结果 HTTP 访问 | 全部 200 |
| 后端健康检查与阀门覆盖参数 | 通过 |

## 复现

在项目根目录执行（需要 Docker 运行并可下载 Python 构建依赖）：

```bash
bash scripts/verify_skill_install.sh
```

末尾预期输出：

```text
PASS: isolated Skill references, editable install, CLI, independent analytic baseline, static HTTP, live API
```

脚本在临时容器中安装依赖及启动 HTTP 服务，不映射宿主端口。

## 验证边界

这不是 Clawhub 下载/安装测试，也不是 Claude Code、Cursor 或 Codex 自动发现 Skill 的测试；没有发布 Skill 或模拟自然语言 Agent 行为。

当前 Skill 是指令与示例包，Python 求解器和网页仍来自单独安装的项目。只下载 Skill 而没有项目时不能执行计算；SKILL.md 已明确说明此依赖。发布后仍需补入真实的版本化仓库地址，并验证一次从发布地址获取的完整流程。
