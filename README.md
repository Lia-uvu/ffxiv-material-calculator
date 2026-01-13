# 魔石精计算器 / FFXIV 材料计算器
[English](README.en.md) | 中文

这是一个面向《最终幻想14》（FFXIV）制作系统的、基于 Vue 3 的开源单页应用（SPA）。
它基于项目内置的静态道具/配方数据，对制作目标进行配方树拆解与材料汇总，用来把“想做哪些成品、各做多少”转换成清晰的材料清单与可制作拆解结果，方便规划采集/购买/制作路线。

## 在线使用
- Live: https://msjcalc.pages.dev

## 详细设计与规范
- [docs/zh-CN/01-architecture-dataflow.md](docs/zh-CN/01-architecture-dataflow.md)：项目结构、模块边界、数据流
- [docs/zh-CN/02-contracts.md](docs/zh-CN/02-contracts.md)：文件/模块之间如何通信（输入输出/事件/状态/数据结构契约）
- [docs/zh-CN/03-deployment-data.md](docs/zh-CN/03-deployment-data.md)：部署与数据更新（数据清洗与更新）
