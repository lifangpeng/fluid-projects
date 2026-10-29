# Algorithm Notes

Linear edges use conductance `1/R` and node mass conservation to assemble a pressure matrix. Quadratic edges use `ΔP = R Q |Q|`; the solver iteratively updates an effective conductance from the previous flow and resolves the pressure system until flow change is below `1e-9` or 100 iterations are reached. Fixed-pressure nodes provide Dirichlet boundaries. After solving, the analyzer performs graph reachability and compares each load's flow and pressure with its thresholds.

## 独立基准推导

示例各负载出口背压均为 100000 Pa，入口 500000 Pa。令开启支路的 `g = Σ 1/√R_i`，支路共同压降 `d = 400000 / (1 + R_main × g²)`，则 `P_j = 100000 + d`、`Q_i = √(d/R_i)`、`Q_main = Σ Q_i`。expected_demo_result.json 使用此独立串并联解析公式生成，测试以相对容差 1e-6 比较压力与流量，并验证关闭支路为零。

当前 residual 表示未知压力节点的最大质量守恒误差（m³/s）；收敛同时要求此误差与流量变化小于 1e-9。无参考压力的分量返回非收敛诊断；不可求得的残差序列化为 null。密度作为输入元数据，当前经验阻力公式不单独使用密度。源/泵是理想定压边界，不实现泵曲线。
