---
id: synthesis-slug
title: 综述标题
type: synthesis
# kind: convergent=汇总型(沿单一轴值收敛梳理) | divergent=碰撞型(故意跨轴混合找空白)
kind: convergent
# axis: collection | tag | mixed(碰撞型常为 mixed)
axis: collection
# scope: 本页实际汇总/碰撞的轴值列表。
#   汇总型一般一个值，如 ["CD&R问题可解释性研究"] 或 ["鲁棒强化学习"];
#   碰撞型多个值，如 ["鲁棒强化学习", "扇区优化研究"]。混合必须在此留痕。
scope: []
covered_citation_keys: []
tags: []
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
status: needs-review
related: []
---

# 综述标题

> 本页是 scoped 编译产物：开头一句话声明 kind 与 scope，让读者知道它汇总/碰撞了什么范围。
> 汇总型忠实梳理单一方向；碰撞型故意跨领域找火花，但范围必须与 frontmatter 的 scope 一致。

## 1. 研究问题谱系

把这一组论文实际处理的问题拆清楚，不只按关键词堆叠。

## 2. 发展脉络（双轴）

> 按两条平行轴梳理，对应 `catalog/MATRIX.md` 的方法轴与问题轴、`catalog/BY-YEAR.md` 的年份切片。

### 2.1 求解方法的演进

按年份梳理方法/模型/算法路线如何更替（如数学规划 → DRL → MARL → 可解释化）。

### 2.2 解决问题的演进

按年份梳理所解问题、场景、约束与评价重点如何变化（如静态→动态、单机→多智能体、性能→可信）。

## 3. 创新点汇总

列出各路线真正新增的判断、机制或证据。

## 4. 分歧与矛盾

记录互相冲突的结论、假设和实验设置。

## 5. 待创新改进的空白

区分“库内暂未覆盖”和“可能有研究价值的空白”。碰撞型在此重点回答“这次跨领域组合是否撞出真空白”。

## 6. 各论文在本 scope 下的可引用点

> 语境相关判断只活在这里，按本页 scope 推导，不写回单篇 note。
> 同一篇论文在不同 synthesis 下可有不同可引用点，这是“论文一文多义”的正确表达。

- `citationKey`：在本方向可用于（引言 / 方法对比 / 讨论局限）……
