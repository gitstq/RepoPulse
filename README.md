# RepoPulse

> **轻量级 Git 仓库智能管理 TUI 引擎 / Lightweight Git Repository Intelligence Management TUI Engine**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-v1.0.0-orange.svg)](https://github.com/gitstq/RepoPulse)

---

**🌐 语言切换 / Language Switch：** [简体中文](#简体中文) · [繁體中文](#繁體中文) · [English](#english)

---

<a id="简体中文"></a>

# 🇨🇳 简体中文

## 🎉 项目介绍

在 GitHub 上管理大量仓库是一件令人头疼的事情 —— 哪些仓库还在活跃维护？哪些已经沦为「僵尸仓库」？哪些仓库存在安全隐患？哪些值得投入更多精力？

**RepoPulse** 正是为了解决这些痛点而诞生的。它是一款基于终端的智能 Git 仓库管理引擎，通过 GitHub API 获取你的仓库数据，利用多维度健康评分体系为每个仓库「把脉」，再用精美的终端界面（TUI）将一切可视化呈现。

无论你是个人开发者想要梳理自己的项目矩阵，还是团队负责人需要监控组织下的代码资产，RepoPulse 都能成为你得力的命令行助手。

### 🎯 适用场景

- **个人项目矩阵管理** —— 一目了然地掌握自己所有仓库的健康状况
- **组织代码资产审计** —— 快速识别需要关注或归档的仓库
- **开源贡献者分析** —— 评估目标仓库的活跃度和社区健康度
- **依赖安全巡检** —— 批量检查项目依赖是否存在已知漏洞

---

## ✨ 核心特性

### 📊 仓库列表展示
通过 GitHub API 获取用户或组织的全部仓库，以精美的终端表格呈现。支持排序、分页，让你对仓库全貌了然于胸。

### 🏥 仓库健康评分
独创 **5 维度 100 分制** 评分体系，科学量化每个仓库的健康状况：

| 维度 | 满分 | 评估指标 |
|------|------|----------|
| 🔄 更新活跃度 | 25 分 | 最近提交时间、提交频率、Release 频率 |
| 👥 社区参与度 | 25 分 | Star 增长趋势、Fork 数量、Issue 活跃度、PR 数量 |
| 💎 代码质量 | 20 分 | 代码行数合理性、测试覆盖率、CI/CD 配置 |
| 📚 文档完整度 | 15 分 | README 完整性、Wiki 存在性、API 文档 |
| 🛠️ 维护响应度 | 15 分 | Issue 关闭率、PR 合并速度、维护者活跃度 |

### 🏷️ 智能标签管理
基于健康评分和仓库元数据，自动为仓库打上语义化标签：

| 标签 | 含义 | 触发条件 |
|------|------|----------|
| `active` | 活跃维护中 | 近 30 天有提交且健康分 ≥ 60 |
| `stale` | 长期未更新 | 超过 180 天无提交 |
| `archived` | 已归档 | GitHub 标记为 archived |
| `rising_star` | 新星项目 | 创建不足 1 年且 Star 增速 ≥ 50/月 |
| `high_impact` | 高影响力 | Star ≥ 1000 或 Fork ≥ 200 |
| `needs_attention` | 需要关注 | 健康分 < 40 且非 archived |
| `well_documented` | 文档完善 | 文档完整度 ≥ 12/15 |
| `popular` | 受欢迎 | Star ≥ 100 |
| `personal` | 个人项目 | Fork 数为 0 且无协作者 |
| `mature` | 成熟稳定 | 创建超 2 年且活跃度 ≥ 20/25 |

### ⚡ 批量操作
支持批量 Star/Unstar 操作，以及将仓库数据导出为 JSON 或 CSV 格式，方便后续分析和归档。

### 🔒 依赖安全检查
自动解析 `requirements.txt` 和 `package.json`，对照内置漏洞数据库进行安全扫描，及时发现潜在风险。

### 🔍 搜索与过滤
强大的多条件组合过滤能力 —— 按编程语言、Stars 范围、Forks 范围、更新时间、关键词等维度精准筛选。

### 🖥️ 交互式 TUI 仪表盘
基于 **Rich** 库构建的精美终端仪表盘，支持键盘导航、实时刷新，让数据展示赏心悦目。

---

## 🚀 快速开始

### 📋 环境要求

- **Python** ≥ 3.9
- **pip**（Python 包管理器）
- **Git** ≥ 2.0
- **GitHub Token**（用于 API 访问，建议使用 Personal Access Token）

> 💡 **提示：** GitHub API 对未认证请求有速率限制（60 次/小时），建议设置 Token 以提升至 5000 次/小时。

### 🔧 安装

```bash
# 从 PyPI 安装（推荐）
pip install repopulse

# 从源码安装
git clone https://github.com/gitstq/RepoPulse.git
cd RepoPulse
pip install -e .
```

### ⚙️ 配置 GitHub Token

```bash
# 设置环境变量
export GITHUB_TOKEN="your_personal_access_token_here"

# 或通过 RepoPulse 配置命令
repopulse config set token "your_personal_access_token_here"

# 验证配置
repopulse config show
```

### 🎮 快速体验

```bash
# 启动交互式仪表盘（最推荐的使用方式）
repopulse dashboard --user your_username

# 快速查看仓库健康评分
repopulse health --user your_username

# 搜索特定语言的仓库
repopulse search --user your_username --lang python --min-stars 50
```

---

## 📖 详细使用指南

### `repopulse dashboard` —— 交互式仪表盘

启动 RepoPulse 的核心交互界面，以终端仪表盘的形式展示所有仓库数据。

```bash
# 查看个人仓库仪表盘
repopulse dashboard --user your_username

# 查看组织仓库仪表盘
repopulse dashboard --user your_org_name --org

# 指定刷新间隔（秒）
repopulse dashboard --user your_username --interval 30
```

**仪表盘功能：**
- 📈 实时展示仓库健康评分排行
- 🏷️ 标签分布统计图
- ⌨️ 键盘导航（上下选择、回车查看详情、`q` 退出）
- 🔄 自动刷新数据

---

### `repopulse list` —— 仓库列表

以表格形式列出指定用户或组织的所有仓库。

```bash
# 基本用法
repopulse list --user your_username

# 按语言过滤
repopulse list --user your_username --lang python

# 按排序方式输出
repopulse list --user your_username --sort stars --order desc

# 限制显示数量
repopulse list --user your_username --limit 20

# 输出为 JSON 格式
repopulse list --user your_username --format json
```

**可用参数：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `--user` | GitHub 用户名或组织名 | `--user gitstq` |
| `--org` | 指定为组织模式 | `--org` |
| `--lang` | 按编程语言过滤 | `--lang python` |
| `--sort` | 排序字段（stars/forks/updated/size） | `--sort stars` |
| `--order` | 排序方向（asc/desc） | `--order desc` |
| `--limit` | 限制返回数量 | `--limit 50` |
| `--format` | 输出格式（table/json） | `--format json` |

---

### `repopulse health` —— 健康评分

对仓库进行全面的 5 维度健康评分，生成详细的评分报告。

```bash
# 对所有仓库进行健康评分
repopulse health --user your_username

# 评分指定仓库
repopulse health --user your_username --repo specific-repo

# 仅显示低于阈值的仓库
repopulse health --user your_username --below 50

# 导出评分报告
repopulse health --user your_username --output report.json
```

**评分报告示例：**

```
╭─────────────────────────────────────────────────────────╮
│                  RepoPulse 健康评分报告                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📦 awesome-project                        总分: 78/100 │
│  ├─ 🔄 更新活跃度  ████████████████░░░░  20/25          │
│  ├─ 👥 社区参与度  ██████████████░░░░░░  18/25          │
│  ├─ 💎 代码质量    ████████████████░░░░  16/20          │
│  ├─ 📚 文档完整度  ████████████████░░░░  12/15          │
│  └─ 🛠️ 维护响应度  ████████████░░░░░░░░  12/15          │
│                                                         │
│  🏷️ 标签: active, well_documented, popular              │
│  💡 建议: 可适当提升 Issue 响应速度以提高维护响应度分      │
│                                                         │
╰─────────────────────────────────────────────────────────╯
```

---

### `repopulse search` —— 搜索与过滤

强大的多条件组合搜索，精准定位目标仓库。

```bash
# 按语言和 Stars 过滤
repopulse search --user your_username --lang python --min-stars 100

# 按时间范围过滤
repopulse search --user your_username --updated-after 2024-01-01

# 按关键词搜索
repopulse search --user your_username --keyword "web framework"

# 组合条件搜索
repopulse search --user your_username \
  --lang python \
  --min-stars 50 \
  --max-forks 500 \
  --updated-after 2024-06-01 \
  --keyword "cli tool"
```

**可用过滤条件：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `--lang` | 编程语言 | `--lang rust` |
| `--min-stars` | 最少 Stars 数 | `--min-stars 100` |
| `--max-stars` | 最多 Stars 数 | `--max-stars 10000` |
| `--min-forks` | 最少 Forks 数 | `--min-forks 10` |
| `--max-forks` | 最多 Forks 数 | `--max-forks 1000` |
| `--updated-after` | 最近更新时间 | `--updated-after 2024-01-01` |
| `--updated-before` | 最早更新时间 | `--updated-before 2024-12-31` |
| `--keyword` | 关键词（匹配名称和描述） | `--keyword "machine learning"` |

---

### `repopulse tags` —— 智能标签

自动为仓库分配语义化标签，帮助你快速了解仓库状态。

```bash
# 为所有仓库生成标签
repopulse tags --user your_username

# 按标签筛选仓库
repopulse tags --user your_username --filter stale

# 按标签筛选并显示详情
repopulse tags --user your_username --filter needs_attention --detail

# 导出标签数据
repopulse tags --user your_username --output tags.json
```

---

### `repopulse batch` —— 批量操作

支持批量 Star/Unstar 和数据导出。

```bash
# 批量导出为 JSON
repopulse batch export --user your_username --format json --output repos.json

# 批量导出为 CSV
repopulse batch export --user your_username --format csv --output repos.csv

# 批量 Star（按标签筛选后）
repopulse batch star --user your_username --filter "lang:python AND stars:>100"

# 批量 Unstar
repopulse batch unstar --user your_username --filter "tag:stale"
```

---

### `repopulse deps` —— 依赖安全检查

扫描项目依赖文件，检测已知安全漏洞。

```bash
# 检查 Python 项目依赖
repopulse deps requirements.txt

# 检查 Node.js 项目依赖
repopulse deps package.json

# 指定漏洞严重等级阈值
repopulse deps requirements.txt --severity high

# 输出详细报告
repopulse deps requirements.txt --detail --output deps_report.json
```

**安全报告示例：**

```
╭──────────────────────────────────────────────────╮
│           🔒 依赖安全检查报告                      │
├──────────────────────────────────────────────────┤
│                                                  │
│  📄 requirements.txt                             │
│  ├─ ✅ requests==2.31.0     安全                 │
│  ├─ ✅ flask==3.0.0        安全                 │
│  ├─ ⚠️ django==2.2.28      中危 CVE-2023-XXXXX  │
│  └─ 🔴 pillow==8.1.0       高危 CVE-2021-XXXXX  │
│                                                  │
│  📊 摘要: 2 安全 / 1 中危 / 1 高危               │
│  💡 建议: 立即升级 pillow 至 ≥ 8.1.2              │
│                                                  │
╰──────────────────────────────────────────────────╯
```

---

### `repopulse config` —— 配置管理

管理 RepoPulse 的全局配置。

```bash
# 查看当前配置
repopulse config show

# 设置 GitHub Token
repopulse config set token "ghp_xxxxxxxxxxxx"

# 设置默认用户名
repopulse config set default_user "your_username"

# 设置 API 请求超时时间（秒）
repopulse config set timeout 30

# 重置为默认配置
repopulse config reset
```

**配置文件位置：**
- Linux/macOS: `~/.config/repopulse/config.json`
- Windows: `%APPDATA%\RepoPulse\config.json`

---

## 💡 设计思路与迭代规划

### 🏗️ 架构设计理念

RepoPulse 的核心设计理念是 **「数据驱动 + 终端优先」**：

1. **分层架构** —— 数据采集层（GitHub API）、分析引擎层（评分/标签）、展示层（Rich TUI）三层解耦，各层可独立演进
2. **离线优先** —— 支持缓存机制，减少不必要的 API 调用，在网络不佳时仍可查看历史数据
3. **渐进式复杂度** —— 简单场景一条命令搞定，复杂场景提供丰富的参数组合

### 📊 健康评分算法设计

评分算法遵循以下原则：
- **客观性** —— 所有指标均基于可量化的 GitHub 数据，避免主观判断
- **可解释性** —— 每个维度的评分依据清晰透明，用户可以理解为什么某个仓库得了某个分数
- **可配置性** —— 各维度权重可通过配置文件调整，适应不同场景的需求

### 🗺️ 迭代规划

**v1.0.0（当前版本）**
- ✅ 仓库列表展示与基础过滤
- ✅ 5 维度健康评分体系
- ✅ 10 种智能标签
- ✅ 批量操作与数据导出
- ✅ 依赖安全检查
- ✅ 交互式 TUI 仪表盘

**v1.1.0（计划中）**
- 🔲 GitLab/Gitee 多平台支持
- 🔲 仓库对比功能（并排对比两个仓库的评分）
- 🔲 自定义评分权重模板
- 🔲 Webhook 集成（仓库事件实时推送）

**v1.2.0（远期规划）**
- 🔲 仓库趋势分析（历史评分变化曲线）
- 🔲 团队协作功能（共享评分报告）
- 🔲 插件系统（支持自定义分析模块）
- 🔲 AI 驱动的维护建议

---

## 📦 打包与部署指南

### 🐍 使用 PyPI 分发

RepoPulse 作为 CLI 工具/开发工具库，无需传统的 Release 发布流程，直接通过 PyPI 分发即可。

```bash
# 1. 安装构建工具
pip install build twine

# 2. 构建分发包
python -m build

# 3. 检查包内容
twine check dist/*

# 4. 上传到 PyPI（TestPyPI 先测试）
twine upload --repository testpypi dist/*
twine upload dist/*
```

### 📁 项目结构

```
RepoPulse/
├── repopulse/                # 主包
│   ├── __init__.py
│   ├── cli/                  # CLI 命令定义
│   │   ├── dashboard.py
│   │   ├── list.py
│   │   ├── health.py
│   │   ├── search.py
│   │   ├── tags.py
│   │   ├── batch.py
│   │   ├── deps.py
│   │   └── config.py
│   ├── core/                 # 核心逻辑
│   │   ├── api.py            # GitHub API 封装
│   │   ├── scorer.py         # 健康评分引擎
│   │   ├── tagger.py         # 智能标签引擎
│   │   └── security.py       # 依赖安全检查
│   ├── ui/                   # TUI 界面
│   │   ├── dashboard.py
│   │   ├── tables.py
│   │   └── panels.py
│   └── utils/                # 工具函数
│       ├── cache.py
│       ├── config.py
│       └── export.py
├── tests/                    # 测试
├── pyproject.toml            # 项目配置
└── README.md                 # 项目文档
```

### 🔧 本地开发

```bash
# 克隆仓库
git clone https://github.com/gitstq/RepoPulse.git
cd RepoPulse

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 代码格式化
black repopulse/
isort repopulse/

# 代码检查
flake8 repopulse/
mypy repopulse/
```

---

## 🤝 贡献指南

我们欢迎并感谢每一位贡献者！无论是提交 Bug 报告、改进文档，还是贡献代码，都是对项目的宝贵支持。

### 🐛 提交 Bug

1. 在 [Issues](https://github.com/gitstq/RepoPulse/issues) 中搜索是否已有相同问题
2. 若没有，创建新 Issue，并附上：
   - RepoPulse 版本号（`repopulse --version`）
   - Python 版本和操作系统
   - 复现步骤和错误日志

### 💻 提交代码

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 提交更改：`git commit -m "feat: 添加你的功能描述"`
4. 推送分支：`git push origin feature/your-feature-name`
5. 提交 **Pull Request**

**Commit 规范：** 遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式调整（不影响逻辑） |
| `refactor` | 代码重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具链相关 |

### 📝 改进文档

文档的改进同样重要！如果你发现文档有不清晰或遗漏的地方，欢迎直接提交 PR 修正。

---

## 📄 开源协议

本项目基于 **[MIT License](https://opensource.org/licenses/MIT)** 开源。

```
MIT License

Copyright (c) 2024 RepoPulse Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<a id="繁體中文"></a>

# 🇹🇼 繁體中文

## 🎉 專案介紹

在 GitHub 上管理大量倉庫是一件令人頭疼的事情 —— 哪些倉庫還在活躍維護？哪些已經淪為「殭屍倉庫」？哪些倉庫存在安全隱患？哪些值得投入更多精力？

**RepoPulse** 正是為了解決這些痛點而誕生的。它是一款基於終端的智慧 Git 倉庫管理引擎，透過 GitHub API 取得你的倉庫資料，利用多維度健康評分體系為每個倉庫「把脈」，再用精美的終端介面（TUI）將一切視覺化呈現。

無論你是個人開發者想要梳理自己的專案矩陣，還是團隊負責人需要監控組織下的程式碼資產，RepoPulse 都能成為你得力的命令列助手。

### 🎯 適用場景

- **個人專案矩陣管理** —— 一目了然地掌握自己所有倉庫的健康狀況
- **組織程式碼資產審計** —— 快速識別需要關注或歸檔的倉庫
- **開源貢獻者分析** —— 評估目標倉庫的活躍度與社群健康度
- **依賴安全巡檢** —— 批量檢查專案依賴是否存在已知漏洞

---

## ✨ 核心特性

### 📊 倉庫列表展示
透過 GitHub API 取得使用者或組織的全部倉庫，以精美的終端表格呈現。支援排序、分頁，讓你對倉庫全貌了然於胸。

### 🏥 倉庫健康評分
獨創 **5 維度 100 分制** 評分體系，科學量化每個倉庫的健康狀況：

| 維度 | 滿分 | 評估指標 |
|------|------|----------|
| 🔄 更新活躍度 | 25 分 | 最近提交時間、提交頻率、Release 頻率 |
| 👥 社群參與度 | 25 分 | Star 成長趨勢、Fork 數量、Issue 活躍度、PR 數量 |
| 💎 程式碼品質 | 20 分 | 程式碼行數合理性、測試覆蓋率、CI/CD 配置 |
| 📚 文件完整度 | 15 分 | README 完整性、Wiki 存在性、API 文件 |
| 🛠️ 維護回應度 | 15 分 | Issue 關閉率、PR 合併速度、維護者活躍度 |

### 🏷️ 智慧標籤管理
基於健康評分和倉庫元資料，自動為倉庫打上語義化標籤：

| 標籤 | 含義 | 觸發條件 |
|------|------|----------|
| `active` | 活躍維護中 | 近 30 天有提交且健康分 ≥ 60 |
| `stale` | 長期未更新 | 超過 180 天無提交 |
| `archived` | 已歸檔 | GitHub 標記為 archived |
| `rising_star` | 新星專案 | 建立不足 1 年且 Star 增速 ≥ 50/月 |
| `high_impact` | 高影響力 | Star ≥ 1000 或 Fork ≥ 200 |
| `needs_attention` | 需要關注 | 健康分 < 40 且非 archived |
| `well_documented` | 文件完善 | 文件完整度 ≥ 12/15 |
| `popular` | 受歡迎 | Star ≥ 100 |
| `personal` | 個人專案 | Fork 數為 0 且無協作者 |
| `mature` | 成熟穩定 | 建立超 2 年且活躍度 ≥ 20/25 |

### ⚡ 批次操作
支援批次 Star/Unstar 操作，以及將倉庫資料匯出為 JSON 或 CSV 格式，方便後續分析和歸檔。

### 🔒 依賴安全檢查
自動解析 `requirements.txt` 和 `package.json`，對照內建漏洞資料庫進行安全掃描，及時發現潛在風險。

### 🔍 搜尋與篩選
強大的多條件組合篩選能力 —— 按程式語言、Stars 範圍、Forks 範圍、更新時間、關鍵字等維度精準篩選。

### 🖥️ 互動式 TUI 儀表板
基於 **Rich** 函式庫建構的精美終端儀表板，支援鍵盤導航、即時刷新，讓資料展示賞心悅目。

---

## 🚀 快速開始

### 📋 環境需求

- **Python** ≥ 3.9
- **pip**（Python 套件管理器）
- **Git** ≥ 2.0
- **GitHub Token**（用於 API 存取，建議使用 Personal Access Token）

> 💡 **提示：** GitHub API 對未認證請求有速率限制（60 次/小時），建議設定 Token 以提升至 5000 次/小時。

### 🔧 安裝

```bash
# 從 PyPI 安裝（推薦）
pip install repopulse

# 從原始碼安裝
git clone https://github.com/gitstq/RepoPulse.git
cd RepoPulse
pip install -e .
```

### ⚙️ 設定 GitHub Token

```bash
# 設定環境變數
export GITHUB_TOKEN="your_personal_access_token_here"

# 或透過 RepoPulse 設定命令
repopulse config set token "your_personal_access_token_here"

# 驗證設定
repopulse config show
```

### 🎮 快速體驗

```bash
# 啟動互動式儀表板（最推薦的使用方式）
repopulse dashboard --user your_username

# 快速查看倉庫健康評分
repopulse health --user your_username

# 搜尋特定語言的倉庫
repopulse search --user your_username --lang python --min-stars 50
```

---

## 📖 詳細使用指南

### `repopulse dashboard` —— 互動式儀表板

啟動 RepoPulse 的核心互動介面，以終端儀表板的形式展示所有倉庫資料。

```bash
# 查看個人倉庫儀表板
repopulse dashboard --user your_username

# 查看組織倉庫儀表板
repopulse dashboard --user your_org_name --org

# 指定刷新間隔（秒）
repopulse dashboard --user your_username --interval 30
```

**儀表板功能：**
- 📈 即時展示倉庫健康評分排行
- 🏷️ 標籤分佈統計圖
- ⌨️ 鍵盤導航（上下選擇、Enter 查看詳情、`q` 退出）
- 🔄 自動刷新資料

---

### `repopulse list` —— 倉庫列表

以表格形式列出指定使用者或組織的所有倉庫。

```bash
# 基本用法
repopulse list --user your_username

# 按語言篩選
repopulse list --user your_username --lang python

# 按排序方式輸出
repopulse list --user your_username --sort stars --order desc

# 限制顯示數量
repopulse list --user your_username --limit 20

# 輸出為 JSON 格式
repopulse list --user your_username --format json
```

**可用參數：**

| 參數 | 說明 | 範例 |
|------|------|------|
| `--user` | GitHub 使用者名稱或組織名 | `--user gitstq` |
| `--org` | 指定為組織模式 | `--org` |
| `--lang` | 按程式語言篩選 | `--lang python` |
| `--sort` | 排序欄位（stars/forks/updated/size） | `--sort stars` |
| `--order` | 排序方向（asc/desc） | `--order desc` |
| `--limit` | 限制回傳數量 | `--limit 50` |
| `--format` | 輸出格式（table/json） | `--format json` |

---

### `repopulse health` —— 健康評分

對倉庫進行全面的 5 維度健康評分，產生詳細的評分報告。

```bash
# 對所有倉庫進行健康評分
repopulse health --user your_username

# 評分指定倉庫
repopulse health --user your_username --repo specific-repo

# 僅顯示低於閾值的倉庫
repopulse health --user your_username --below 50

# 匯出評分報告
repopulse health --user your_username --output report.json
```

**評分報告範例：**

```
╭─────────────────────────────────────────────────────────╮
│                  RepoPulse 健康評分報告                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📦 awesome-project                        總分: 78/100 │
│  ├─ 🔄 更新活躍度  ████████████████░░░░  20/25          │
│  ├─ 👥 社群參與度  ██████████████░░░░░░  18/25          │
│  ├─ 💎 程式碼品質  ████████████████░░░░  16/20          │
│  ├─ 📚 文件完整度  ████████████████░░░░  12/15          │
│  └─ 🛠️ 維護回應度  ████████████░░░░░░░░  12/15          │
│                                                         │
│  🏷️ 標籤: active, well_documented, popular              │
│  💡 建議: 可適當提升 Issue 回應速度以提高維護回應度分      │
│                                                         │
╰─────────────────────────────────────────────────────────╯
```

---

### `repopulse search` —— 搜尋與篩選

強大的多條件組合搜尋，精準定位目標倉庫。

```bash
# 按語言和 Stars 篩選
repopulse search --user your_username --lang python --min-stars 100

# 按時間範圍篩選
repopulse search --user your_username --updated-after 2024-01-01

# 按關鍵字搜尋
repopulse search --user your_username --keyword "web framework"

# 組合條件搜尋
repopulse search --user your_username \
  --lang python \
  --min-stars 50 \
  --max-forks 500 \
  --updated-after 2024-06-01 \
  --keyword "cli tool"
```

**可用篩選條件：**

| 參數 | 說明 | 範例 |
|------|------|------|
| `--lang` | 程式語言 | `--lang rust` |
| `--min-stars` | 最少 Stars 數 | `--min-stars 100` |
| `--max-stars` | 最多 Stars 數 | `--max-stars 10000` |
| `--min-forks` | 最少 Forks 數 | `--min-forks 10` |
| `--max-forks` | 最多 Forks 數 | `--max-forks 1000` |
| `--updated-after` | 最近更新時間 | `--updated-after 2024-01-01` |
| `--updated-before` | 最早更新時間 | `--updated-before 2024-12-31` |
| `--keyword` | 關鍵字（匹配名稱和描述） | `--keyword "machine learning"` |

---

### `repopulse tags` —— 智慧標籤

自動為倉庫分配語義化標籤，幫助你快速了解倉庫狀態。

```bash
# 為所有倉庫產生標籤
repopulse tags --user your_username

# 按標籤篩選倉庫
repopulse tags --user your_username --filter stale

# 按標籤篩選並顯示詳情
repopulse tags --user your_username --filter needs_attention --detail

# 匯出標籤資料
repopulse tags --user your_username --output tags.json
```

---

### `repopulse batch` —— 批次操作

支援批次 Star/Unstar 和資料匯出。

```bash
# 批次匯出為 JSON
repopulse batch export --user your_username --format json --output repos.json

# 批次匯出為 CSV
repopulse batch export --user your_username --format csv --output repos.csv

# 批次 Star（按標籤篩選後）
repopulse batch star --user your_username --filter "lang:python AND stars:>100"

# 批次 Unstar
repopulse batch unstar --user your_username --filter "tag:stale"
```

---

### `repopulse deps` —— 依賴安全檢查

掃描專案依賴檔案，偵測已知安全漏洞。

```bash
# 檢查 Python 專案依賴
repopulse deps requirements.txt

# 檢查 Node.js 專案依賴
repopulse deps package.json

# 指定漏洞嚴重等級閾值
repopulse deps requirements.txt --severity high

# 輸出詳細報告
repopulse deps requirements.txt --detail --output deps_report.json
```

**安全報告範例：**

```
╭──────────────────────────────────────────────────╮
│           🔒 依賴安全檢查報告                      │
├──────────────────────────────────────────────────┤
│                                                  │
│  📄 requirements.txt                             │
│  ├─ ✅ requests==2.31.0     安全                 │
│  ├─ ✅ flask==3.0.0        安全                 │
│  ├─ ⚠️ django==2.2.28      中危 CVE-2023-XXXXX  │
│  └─ 🔴 pillow==8.1.0       高危 CVE-2021-XXXXX  │
│                                                  │
│  📊 摘要: 2 安全 / 1 中危 / 1 高危               │
│  💡 建議: 立即升級 pillow 至 ≥ 8.1.2              │
│                                                  │
╰──────────────────────────────────────────────────╯
```

---

### `repopulse config` —— 設定管理

管理 RepoPulse 的全域設定。

```bash
# 查看目前設定
repopulse config show

# 設定 GitHub Token
repopulse config set token "ghp_xxxxxxxxxxxx"

# 設定預設使用者名稱
repopulse config set default_user "your_username"

# 設定 API 請求逾時時間（秒）
repopulse config set timeout 30

# 重設為預設設定
repopulse config reset
```

**設定檔位置：**
- Linux/macOS: `~/.config/repopulse/config.json`
- Windows: `%APPDATA%\RepoPulse\config.json`

---

## 💡 設計思路與迭代規劃

### 🏗️ 架構設計理念

RepoPulse 的核心設計理念是 **「資料驅動 + 終端優先」**：

1. **分層架構** —— 資料採集層（GitHub API）、分析引擎層（評分/標籤）、展示層（Rich TUI）三層解耦，各層可獨立演進
2. **離線優先** —— 支援快取機制，減少不必要的 API 呼叫，在網路不佳時仍可檢視歷史資料
3. **漸進式複雜度** —— 簡單場景一條命令搞定，複雜場景提供豐富的參數組合

### 📊 健康評分演算法設計

評分演算法遵循以下原則：
- **客觀性** —— 所有指標均基於可量化的 GitHub 資料，避免主觀判斷
- **可解釋性** —— 每個維度的評分依據清晰透明，使用者可以理解為什麼某個倉庫得了某個分數
- **可配置性** —— 各維度權重可透過設定檔調整，適應不同場景的需求

### 🗺️ 迭代規劃

**v1.0.0（目前版本）**
- ✅ 倉庫列表展示與基礎篩選
- ✅ 5 維度健康評分體系
- ✅ 10 種智慧標籤
- ✅ 批次操作與資料匯出
- ✅ 依賴安全檢查
- ✅ 互動式 TUI 儀表板

**v1.1.0（規劃中）**
- 🔲 GitLab/Gitee 多平台支援
- 🔲 倉庫對比功能（並排對比兩個倉庫的評分）
- 🔲 自訂評分權重範本
- 🔲 Webhook 整合（倉庫事件即時推送）

**v1.2.0（遠期規劃）**
- 🔲 倉庫趨勢分析（歷史評分變化曲線）
- 🔲 團隊協作功能（共享評分報告）
- 🔲 外掛系統（支援自訂分析模組）
- 🔲 AI 驅動的維護建議

---

## 📦 打包與部署指南

### 🐍 使用 PyPI 分發

RepoPulse 作為 CLI 工具/開發工具庫，無需傳統的 Release 發布流程，直接透過 PyPI 分發即可。

```bash
# 1. 安裝建置工具
pip install build twine

# 2. 建置分發包
python -m build

# 3. 檢查包內容
twine check dist/*

# 4. 上傳到 PyPI（先在 TestPyPI 測試）
twine upload --repository testpypi dist/*
twine upload dist/*
```

### 📁 專案結構

```
RepoPulse/
├── repopulse/                # 主套件
│   ├── __init__.py
│   ├── cli/                  # CLI 命令定義
│   │   ├── dashboard.py
│   │   ├── list.py
│   │   ├── health.py
│   │   ├── search.py
│   │   ├── tags.py
│   │   ├── batch.py
│   │   ├── deps.py
│   │   └── config.py
│   ├── core/                 # 核心邏輯
│   │   ├── api.py            # GitHub API 封裝
│   │   ├── scorer.py         # 健康評分引擎
│   │   ├── tagger.py         # 智慧標籤引擎
│   │   └── security.py       # 依賴安全檢查
│   ├── ui/                   # TUI 介面
│   │   ├── dashboard.py
│   │   ├── tables.py
│   │   └── panels.py
│   └── utils/                # 工具函式
│       ├── cache.py
│       ├── config.py
│       └── export.py
├── tests/                    # 測試
├── pyproject.toml            # 專案配置
└── README.md                 # 專案文件
```

### 🔧 本地開發

```bash
# 複製倉庫
git clone https://github.com/gitstq/RepoPulse.git
cd RepoPulse

# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest tests/

# 程式碼格式化
black repopulse/
isort repopulse/

# 程式碼檢查
flake8 repopulse/
mypy repopulse/
```

---

## 🤝 貢獻指南

我們歡迎並感謝每一位貢獻者！無論是提交 Bug 回報、改進文件，還是貢獻程式碼，都是對專案的寶貴支持。

### 🐛 提交 Bug

1. 在 [Issues](https://github.com/gitstq/RepoPulse/issues) 中搜尋是否已有相同問題
2. 若沒有，建立新 Issue，並附上：
   - RepoPulse 版本號（`repopulse --version`）
   - Python 版本和作業系統
   - 重現步驟和錯誤日誌

### 💻 提交程式碼

1. **Fork** 本倉庫
2. 建立特性分支：`git checkout -b feature/your-feature-name`
3. 提交變更：`git commit -m "feat: 新增你的功能描述"`
4. 推送分支：`git push origin feature/your-feature-name`
5. 提交 **Pull Request**

**Commit 規範：** 遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

| 類型 | 說明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修復 |
| `docs` | 文件更新 |
| `style` | 程式碼格式調整（不影響邏輯） |
| `refactor` | 程式碼重構 |
| `test` | 測試相關 |
| `chore` | 建置/工具鏈相關 |

### 📝 改進文件

文件的改進同樣重要！如果你發現文件有不清晰或遺漏的地方，歡迎直接提交 PR 修正。

---

## 📄 開源協議

本專案基於 **[MIT License](https://opensource.org/licenses/MIT)** 開源。

```
MIT License

Copyright (c) 2024 RepoPulse Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<a id="english"></a>

# 🇬🇧 English

## 🎉 Introduction

Managing a large number of repositories on GitHub can be a headache. Which repos are still actively maintained? Which ones have become "zombie repos"? Which ones have security vulnerabilities? Which ones deserve more of your attention?

**RepoPulse** was born to solve these exact pain points. It is a terminal-based intelligent Git repository management engine that fetches your repository data via the GitHub API, runs a multi-dimensional health scoring system to "diagnose" each repo, and presents everything through a beautifully crafted Terminal User Interface (TUI).

Whether you are an individual developer looking to organize your project portfolio, or a team lead who needs to monitor your organization's code assets, RepoPulse serves as a powerful command-line assistant.

### 🎯 Use Cases

- **Personal Project Portfolio Management** — Get a clear overview of all your repositories' health at a glance
- **Organization Code Asset Auditing** — Quickly identify repos that need attention or should be archived
- **Open Source Contributor Analysis** — Evaluate the activity level and community health of target repositories
- **Dependency Security Scanning** — Batch-check project dependencies for known vulnerabilities

---

## ✨ Core Features

### 📊 Repository Listing
Fetches all repositories for a user or organization via the GitHub API and displays them in a polished terminal table. Supports sorting and pagination so you can get the full picture at a glance.

### 🏥 Repository Health Scoring
A proprietary **5-dimension, 100-point** scoring system that scientifically quantifies the health of each repository:

| Dimension | Max Score | Evaluation Metrics |
|-----------|-----------|-------------------|
| 🔄 Update Activity | 25 pts | Last commit time, commit frequency, release cadence |
| 👥 Community Engagement | 25 pts | Star growth trend, fork count, issue activity, PR count |
| 💎 Code Quality | 20 pts | Code size reasonableness, test coverage, CI/CD configuration |
| 📚 Documentation Completeness | 15 pts | README completeness, Wiki presence, API documentation |
| 🛠️ Maintenance Responsiveness | 15 pts | Issue close rate, PR merge speed, maintainer activity |

### 🏷️ Smart Tag Management
Automatically assigns semantic tags to repositories based on health scores and metadata:

| Tag | Meaning | Trigger Condition |
|-----|---------|-------------------|
| `active` | Actively maintained | Commits within 30 days AND health score >= 60 |
| `stale` | Long-term inactive | No commits for over 180 days |
| `archived` | Archived | Marked as archived on GitHub |
| `rising_star` | Rising star project | Created < 1 year ago AND star growth >= 50/month |
| `high_impact` | High impact | Stars >= 1000 OR Forks >= 200 |
| `needs_attention` | Needs attention | Health score < 40 AND not archived |
| `well_documented` | Well documented | Documentation score >= 12/15 |
| `popular` | Popular | Stars >= 100 |
| `personal` | Personal project | 0 forks AND no collaborators |
| `mature` | Mature and stable | Created > 2 years ago AND activity >= 20/25 |

### ⚡ Batch Operations
Supports batch Star/Unstar operations and exporting repository data to JSON or CSV format for further analysis and archiving.

### 🔒 Dependency Security Check
Automatically parses `requirements.txt` and `package.json`, cross-referencing against a built-in vulnerability database to detect security risks in a timely manner.

### 🔍 Search & Filter
Powerful multi-condition filtering — precisely narrow down repositories by programming language, Stars range, Forks range, update time, and keywords.

### 🖥️ Interactive TUI Dashboard
A beautifully crafted terminal dashboard built with the **Rich** library, featuring keyboard navigation and real-time refresh for a delightful data visualization experience.

---

## 🚀 Quick Start

### 📋 Prerequisites

- **Python** >= 3.9
- **pip** (Python package manager)
- **Git** >= 2.0
- **GitHub Token** (for API access; a Personal Access Token is recommended)

> 💡 **Tip:** The GitHub API rate-limits unauthenticated requests to 60 requests/hour. Setting a token raises this to 5,000 requests/hour.

### 🔧 Installation

```bash
# Install from PyPI (recommended)
pip install repopulse

# Install from source
git clone https://github.com/gitstq/RepoPulse.git
cd RepoPulse
pip install -e .
```

### ⚙️ Configuring Your GitHub Token

```bash
# Set via environment variable
export GITHUB_TOKEN="your_personal_access_token_here"

# Or use the RepoPulse config command
repopulse config set token "your_personal_access_token_here"

# Verify your configuration
repopulse config show
```

### 🎮 Quick Demo

```bash
# Launch the interactive dashboard (the recommended way to use RepoPulse)
repopulse dashboard --user your_username

# Quickly check repository health scores
repopulse health --user your_username

# Search for repositories in a specific language
repopulse search --user your_username --lang python --min-stars 50
```

---

## 📖 Detailed Usage Guide

### `repopulse dashboard` — Interactive Dashboard

Launches RepoPulse's core interactive interface, displaying all repository data as a terminal dashboard.

```bash
# View personal repository dashboard
repopulse dashboard --user your_username

# View organization repository dashboard
repopulse dashboard --user your_org_name --org

# Specify refresh interval (in seconds)
repopulse dashboard --user your_username --interval 30
```

**Dashboard Features:**
- 📈 Real-time repository health score rankings
- 🏷️ Tag distribution statistics
- ⌨️ Keyboard navigation (up/down to select, Enter for details, `q` to quit)
- 🔄 Auto-refresh data

---

### `repopulse list` — Repository List

Lists all repositories for a given user or organization in a table format.

```bash
# Basic usage
repopulse list --user your_username

# Filter by language
repopulse list --user your_username --lang python

# Sort output
repopulse list --user your_username --sort stars --order desc

# Limit the number of results
repopulse list --user your_username --limit 20

# Output in JSON format
repopulse list --user your_username --format json
```

**Available Parameters:**

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--user` | GitHub username or organization name | `--user gitstq` |
| `--org` | Enable organization mode | `--org` |
| `--lang` | Filter by programming language | `--lang python` |
| `--sort` | Sort field (stars/forks/updated/size) | `--sort stars` |
| `--order` | Sort direction (asc/desc) | `--order desc` |
| `--limit` | Limit number of results | `--limit 50` |
| `--format` | Output format (table/json) | `--format json` |

---

### `repopulse health` — Health Scoring

Performs a comprehensive 5-dimension health assessment on repositories and generates a detailed scoring report.

```bash
# Score all repositories
repopulse health --user your_username

# Score a specific repository
repopulse health --user your_username --repo specific-repo

# Show only repositories below a threshold
repopulse health --user your_username --below 50

# Export the scoring report
repopulse health --user your_username --output report.json
```

**Sample Scoring Report:**

```
╭─────────────────────────────────────────────────────────╮
│                RepoPulse Health Score Report              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📦 awesome-project                        Total: 78/100│
│  ├─ 🔄 Update Activity   ████████████████░░░░  20/25    │
│  ├─ 👥 Community          ██████████████░░░░░░  18/25    │
│  ├─ 💎 Code Quality       ████████████████░░░░  16/20    │
│  ├─ 📚 Documentation      ████████████████░░░░  12/15    │
│  └─ 🛠️ Maintenance        ████████████░░░░░░░░  12/15    │
│                                                         │
│  🏷️ Tags: active, well_documented, popular              │
│  💡 Tip: Improve Issue response time to boost maintenance│
│                                                         │
╰─────────────────────────────────────────────────────────╯
```

---

### `repopulse search` — Search & Filter

Powerful multi-condition search to pinpoint target repositories with precision.

```bash
# Filter by language and Stars
repopulse search --user your_username --lang python --min-stars 100

# Filter by time range
repopulse search --user your_username --updated-after 2024-01-01

# Search by keyword
repopulse search --user your_username --keyword "web framework"

# Combine multiple conditions
repopulse search --user your_username \
  --lang python \
  --min-stars 50 \
  --max-forks 500 \
  --updated-after 2024-06-01 \
  --keyword "cli tool"
```

**Available Filter Conditions:**

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--lang` | Programming language | `--lang rust` |
| `--min-stars` | Minimum Stars | `--min-stars 100` |
| `--max-stars` | Maximum Stars | `--max-stars 10000` |
| `--min-forks` | Minimum Forks | `--min-forks 10` |
| `--max-forks` | Maximum Forks | `--max-forks 1000` |
| `--updated-after` | Updated after date | `--updated-after 2024-01-01` |
| `--updated-before` | Updated before date | `--updated-before 2024-12-31` |
| `--keyword` | Keyword (matches name and description) | `--keyword "machine learning"` |

---

### `repopulse tags` — Smart Tags

Automatically assigns semantic tags to repositories, helping you quickly understand the status of each repo.

```bash
# Generate tags for all repositories
repopulse tags --user your_username

# Filter repositories by tag
repopulse tags --user your_username --filter stale

# Filter by tag and show details
repopulse tags --user your_username --filter needs_attention --detail

# Export tag data
repopulse tags --user your_username --output tags.json
```

---

### `repopulse batch` — Batch Operations

Supports batch Star/Unstar operations and data export.

```bash
# Batch export to JSON
repopulse batch export --user your_username --format json --output repos.json

# Batch export to CSV
repopulse batch export --user your_username --format csv --output repos.csv

# Batch Star (after filtering by tag)
repopulse batch star --user your_username --filter "lang:python AND stars:>100"

# Batch Unstar
repopulse batch unstar --user your_username --filter "tag:stale"
```

---

### `repopulse deps` — Dependency Security Check

Scans project dependency files to detect known security vulnerabilities.

```bash
# Check Python project dependencies
repopulse deps requirements.txt

# Check Node.js project dependencies
repopulse deps package.json

# Set vulnerability severity threshold
repopulse deps requirements.txt --severity high

# Output a detailed report
repopulse deps requirements.txt --detail --output deps_report.json
```

**Sample Security Report:**

```
╭──────────────────────────────────────────────────╮
│           🔒 Dependency Security Report            │
├──────────────────────────────────────────────────┤
│                                                  │
│  📄 requirements.txt                             │
│  ├─ ✅ requests==2.31.0     Safe                 │
│  ├─ ✅ flask==3.0.0        Safe                 │
│  ├─ ⚠️ django==2.2.28      Medium CVE-2023-XXXXX│
│  └─ 🔴 pillow==8.1.0       High   CVE-2021-XXXXX│
│                                                  │
│  📊 Summary: 2 Safe / 1 Medium / 1 High          │
│  💡 Tip: Upgrade pillow to >= 8.1.2 immediately  │
│                                                  │
╰──────────────────────────────────────────────────╯
```

---

### `repopulse config` — Configuration Management

Manages RepoPulse's global configuration.

```bash
# View current configuration
repopulse config show

# Set GitHub Token
repopulse config set token "ghp_xxxxxxxxxxxx"

# Set default username
repopulse config set default_user "your_username"

# Set API request timeout (seconds)
repopulse config set timeout 30

# Reset to default configuration
repopulse config reset
```

**Configuration File Locations:**
- Linux/macOS: `~/.config/repopulse/config.json`
- Windows: `%APPDATA%\RepoPulse\config.json`

---

## 💡 Design Philosophy & Roadmap

### 🏗️ Architecture Design Principles

RepoPulse's core design philosophy centers on **"Data-Driven + Terminal-First"**:

1. **Layered Architecture** — The data collection layer (GitHub API), analysis engine layer (scoring/tagging), and presentation layer (Rich TUI) are fully decoupled, allowing each layer to evolve independently
2. **Offline-First** — A caching mechanism reduces unnecessary API calls, so you can still browse historical data when connectivity is poor
3. **Progressive Complexity** — Simple tasks are handled with a single command; complex scenarios offer rich parameter combinations

### 📊 Health Scoring Algorithm Design

The scoring algorithm follows these principles:
- **Objectivity** — All metrics are based on quantifiable GitHub data, avoiding subjective judgment
- **Explainability** — The scoring rationale for each dimension is clear and transparent, so users understand why a repository received a particular score
- **Configurability** — Dimension weights can be adjusted via the configuration file to suit different use cases

### 🗺️ Roadmap

**v1.0.0 (Current Release)**
- ✅ Repository listing with basic filtering
- ✅ 5-dimension health scoring system
- ✅ 10 smart tags
- ✅ Batch operations and data export
- ✅ Dependency security check
- ✅ Interactive TUI dashboard

**v1.1.0 (Planned)**
- 🔲 GitLab/Gitee multi-platform support
- 🔲 Repository comparison (side-by-side scoring comparison)
- 🔲 Custom scoring weight templates
- 🔲 Webhook integration (real-time repository event push)

**v1.2.0 (Long-term Vision)**
- 🔲 Repository trend analysis (historical score change curves)
- 🔲 Team collaboration features (shared scoring reports)
- 🔲 Plugin system (custom analysis modules)
- 🔲 AI-driven maintenance recommendations

---

## 📦 Packaging & Deployment Guide

### 🐍 Distribution via PyPI

As a CLI tool / developer utility library, RepoPulse does not require a traditional Release workflow. Distribution through PyPI is sufficient.

```bash
# 1. Install build tools
pip install build twine

# 2. Build distribution packages
python -m build

# 3. Verify package contents
twine check dist/*

# 4. Upload to PyPI (test on TestPyPI first)
twine upload --repository testpypi dist/*
twine upload dist/*
```

### 📁 Project Structure

```
RepoPulse/
├── repopulse/                # Main package
│   ├── __init__.py
│   ├── cli/                  # CLI command definitions
│   │   ├── dashboard.py
│   │   ├── list.py
│   │   ├── health.py
│   │   ├── search.py
│   │   ├── tags.py
│   │   ├── batch.py
│   │   ├── deps.py
│   │   └── config.py
│   ├── core/                 # Core logic
│   │   ├── api.py            # GitHub API wrapper
│   │   ├── scorer.py         # Health scoring engine
│   │   ├── tagger.py         # Smart tagging engine
│   │   └── security.py       # Dependency security check
│   ├── ui/                   # TUI interface
│   │   ├── dashboard.py
│   │   ├── tables.py
│   │   └── panels.py
│   └── utils/                # Utility functions
│       ├── cache.py
│       ├── config.py
│       └── export.py
├── tests/                    # Tests
├── pyproject.toml            # Project configuration
└── README.md                 # Project documentation
```

### 🔧 Local Development

```bash
# Clone the repository
git clone https://github.com/gitstq/RepoPulse.git
cd RepoPulse

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black repopulse/
isort repopulse/

# Lint code
flake8 repopulse/
mypy repopulse/
```

---

## 🤝 Contributing

We welcome and appreciate every contributor! Whether it is filing a bug report, improving documentation, or contributing code, every contribution is valuable to the project.

### 🐛 Reporting Bugs

1. Search [Issues](https://github.com/gitstq/RepoPulse/issues) to see if the problem has already been reported
2. If not, create a new Issue and include:
   - RepoPulse version (`repopulse --version`)
   - Python version and operating system
   - Steps to reproduce and error logs

### 💻 Submitting Code

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature description"`
4. Push the branch: `git push origin feature/your-feature-name`
5. Submit a **Pull Request**

**Commit Convention:** Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation update |
| `style` | Code formatting (no logic changes) |
| `refactor` | Code refactoring |
| `test` | Test-related |
| `chore` | Build/toolchain-related |

### 📝 Improving Documentation

Documentation improvements are just as important! If you find anything unclear or missing in the docs, feel free to submit a PR to fix it.

---

## 📄 License

This project is licensed under the **[MIT License](https://opensource.org/licenses/MIT)**.

```
MIT License

Copyright (c) 2024 RepoPulse Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
