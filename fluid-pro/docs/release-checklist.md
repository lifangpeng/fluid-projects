# 发布验收记录（2026-10-29）

## 本次已修复

- 定压负载不再作为连通性搜索源；负载统计流入量，避免把流出量重复相加。
- 非收敛结果不能判定功能正常。返回具体失败原因和一条拓扑路径。
- 求解收敛同时要求流量变化和节点质量残差低于 1e-9 m³/s。
- CLI 的 --json 写入文件；增加独立解析解与回归测试。
- 网页同源调用 API，支持工况和控制状态覆盖；布局由节点列表生成，显示节点压力和管路流速。
- 增加 Git/Docker 排除规则；安装元数据统一在 pyproject.toml。
- Skill 增加 frontmatter、包内示例、前置安装要求与使用限制；完善 JSON Schema 字段定义。

## 发布前尚需完成

- 更广泛复杂网络的数值稳健性验证；环网、无边界分量、反向流、迭代耗尽已有回归测试。
- 完整的输入语义校验（Schema 不能代替跨字段引用、继承环和有限数校验）。
- 独立解析基准已完成并纳入回归（详见 algorithm.md）。
- 浏览器阀门交互已验证：关闭后冷却流量为零、功能通过率 50%；窄窗口布局已修复。
- 关键失效边/瓶颈分析。当前 topology_path 仅表示一条无向可达路径。
- Docker 已增加非 root 用户和健康检查；依赖与基础镜像版本锁定仍待完成。
- Skill 在全新 Linux 容器中独立目录安装与端到端调用已通过（见 skill-install-verification.md）；发布后仍需补充固定版本仓库地址并验证 Clawhub 获取流程。
- 选定许可证、GitHub 仓库地址和公开/私有设置；当前未初始化 Git，未上传。
- 安装并认证 GitHub/Clawhub 发布工具；当前命令不在 PATH，尚无发布链接。

## 发布文件

GitHub：src、tests、examples、web、docs、skill、README、pyproject.toml、setup.py、backend_server.py、Dockerfile、docker-compose.yml、.gitignore、.dockerignore，以及确定后的许可证。

Clawhub：skill 目录（SKILL.md、Schema 参考、Schema JSON、assets 示例）。该包依赖另行安装的 Python 项目，发布前须补齐可用的版本化获取方式。

排除：缓存、egg-info、虚拟环境、构建产物、日志、PID、密钥和本地 Docker 配置。
