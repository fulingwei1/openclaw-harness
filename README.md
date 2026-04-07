# OpenClaw Harness

<div align="center">
  <img src="docs/logo.png" alt="Logo" width="200">
</div>

<p align="center">
  <a href="https://github.com/fulingwei1/openclaw-harness">
    <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python Version">
    <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/Status-Alpha-yellow" alt="Status">
  </a>
</p>

<p align="center">
  <b>基于 Harness Engineering 理念构建的 AI 任务执行框架</b>
</p>

<p align="center">
  <i>关键词: AI Agent, Harness Engineering, LLM, Planning, Generation, Evaluation</ Skill Extraction
</p>

<p align="center">
  <b>English</b> | <b>中文文档</b>
</p>

## 🎯 设计理念

基于 **Harness Engineering** 的核心思想：

- **Prompt Engineering** → 说什么
- **Context Engineering** → 给它看什么
- **Harness Engineering** → 在什么系统里跑

## ✨ 核心特性

- 🔄 **三智能体闭环**: 自动拆解任务 → 生成内容 → 评估质量
- 🔧 **自动技能提取**: 复杂任务后自动沉淀可可复用技能
- 📏 **黄金法则系统**: 持续积累约束和确保输出一致性
- 💾 **状态外部化**: 不依赖模型记忆，所有状态存储在文件中
- 🔍 **可观测性**: 完整的执行日志和评估记录

## 🚀 快速开始

pip install openclaw-harness
# 或使用 poetry
poetry install openclaw-harness

# 初始化
harness init

# 运行任务（自动闭环）
harness run "Build a REST API for todos"

# 添加黄金法则
harness add-rule "所有输出必须使用中文" --category global --priority 5

