# Memora AI Personal Knowledge Assistant 技术架构方案

版本：0.1  
日期：2026-07-07  
阶段：MVP 快速验证

## 1. 产品技术理解

Memora 是一个基于微信入口的个人 AI 知识助手。它不是传统笔记软件，也不是知识社区，而是一个低摩擦的信息收集与自动整理系统。

核心理念：

```text
Don't organize, just save.
```

用户只需要把内容发给 AI 助手，系统负责理解、摘要、分类、打标签并保存到个人知识库。

### 核心用户问题

- 信息分散在微信、小红书、抖音、公众号、网页、截图和学习资料里。
- 收藏内容越来越多，但未来很难找到。
- 用户不愿意手动整理，整理成本太高。
- 有价值的信息没有沉淀成个人知识资产。

### 核心用户流程

```text
用户看到内容
→ 转发或发送给微信/企业微信 AI 助手
→ 系统识别内容类型
→ AI 提取标题、摘要、分类、标签、关键词
→ 保存到个人知识库
→ 用户未来通过搜索或问答重新找到内容
```

### MVP 第一阶段实现范围

第一版只验证一个核心闭环：

```text
文字/链接输入
→ DeepSeek 自动整理
→ 保存到飞书多维表格
→ 返回保存成功和摘要
```

### 当前不开发的功能

- 手机 App
- 社交功能
- 知识社区
- 自动发布内容
- 复杂知识图谱
- 主动推荐
- 多用户商业化后台
- 小红书/抖音正文自动抓取
- 完整 RAG 问答系统

当前阶段不能扩大项目范围。第一版目标是验证用户是否愿意持续把信息发给 Memora，以及 AI 自动整理后的知识卡片是否有用。

## 2. 系统整体架构设计

```text
+------------------+
| 用户微信/企微入口 |
+---------+--------+
          |
          v
+------------------+        +-------------------+
| 微信回调/Webhook | -----> | 消息接收服务       |
| 验签/解密/去重    |        | normalize message |
+---------+--------+        +---------+---------+
                                      |
                                      v
                            +-------------------+
                            | Backend API       |
                            | 用户/任务/路由     |
                            +---------+---------+
                                      |
                                      v
                            +-------------------+
                            | AI Agent 处理层   |
                            | 分类/摘要/标签提取 |
                            +---------+---------+
                                      |
                +---------------------+---------------------+
                |                                           |
                v                                           v
      +-------------------+                       +-------------------+
      | 数据存储层         |                       | 文件存储层         |
      | 飞书/未来Postgres  |                       | 图片/原始文件/附件  |
      +---------+---------+                       +---------+---------+
                |                                           |
                v                                           v
      +-------------------+                       +-------------------+
      | 搜索/RAG层         | <-------------------- | Embedding/索引任务 |
      | 未来向量检索       |                       | 未来扩展           |
      +-------------------+                       +-------------------+
```

第三方 API：

- DeepSeek API：MVP 默认 AI 模型。
- 飞书开放平台：MVP 知识库存储。
- 企业微信：消息入口和回复。
- 阿里云 OSS：未来保存图片、附件、原始文件。
- GitHub：代码云端保存和版本管理。

### 各层职责

微信入口层：

- 用户发送文字、链接、图片。
- MVP 优先企业微信自建应用。

消息接收服务：

- 接收企业微信回调。
- 验签、解密、消息去重。
- 转换为统一内部消息结构。

后端服务：

- 编排完整业务流程。
- 调用 AI 分析器。
- 调用飞书保存。
- 给用户返回保存结果。

AI Agent 处理层：

- 当前不是复杂多 Agent。
- MVP 只实现一个 Knowledge Analyzer。
- 输入非结构化内容，输出结构化知识卡片 JSON。

数据存储层：

- MVP 使用飞书多维表格。
- 未来迁移 PostgreSQL 作为主数据库。

文件存储层：

- MVP 暂不强依赖。
- 图片阶段引入阿里云 OSS。

搜索/RAG 层：

- MVP 暂不做。
- Phase 5 再加入 embedding、向量库和语义检索。

### 数据流

```text
用户发送文字到企业微信应用
→ 企业微信推送 webhook 到 /api/wechat/callback
→ 后端验签、解密、解析 user_id、msg_id、content
→ 消息去重
→ 调用 DeepSeek 分析接口
→ 得到 title、summary、category、tags、keywords、source
→ 写入飞书多维表格 Knowledge 表
→ 后端返回“已保存 + 摘要 + 分类标签”
→ 企业微信把结果推送给用户
```

## 3. 技术选型方案

### 后端框架

推荐：FastAPI。

原因：

- Python 生态更适合 AI API、RAG、文档解析和数据处理。
- FastAPI 原生适合 API 服务、Webhook 和结构化 schema。
- 单人开发效率高。
- 自动生成 OpenAPI 文档，方便调试。

对比：

- FastAPI：最适合当前 MVP。
- Node.js：适合 I/O 和前端同栈，但 AI/RAG 生态对个人开发者不如 Python 顺手。
- Django：偏重。
- Flask：太轻，后续类型、文档、校验需要自己补。

结论：

```text
FastAPI + Pydantic + Uvicorn
```

### AI 模型

推荐：DeepSeek API。

原因：

- token 成本低，适合大量“收藏内容整理”场景。
- API 兼容 OpenAI SDK，接入成本低。
- 支持 JSON Output，适合输出知识卡片。
- MVP 整理任务通常不需要最强推理模型，低成本模型更重要。

默认模型：

```text
deepseek-v4-flash
```

选择策略：

- 默认使用 `deepseek-v4-flash`，用于摘要、分类、标签生成。
- 复杂长文、研究报告、推理类任务可临时切到 `deepseek-v4-pro`。
- 不建议继续以 `deepseek-chat` 作为长期配置名，因为官方已标注其将在 2026-07-24 弃用。

### 数据库

MVP 推荐：飞书多维表格。

原因：

- 开发快。
- 不需要先做后台管理页面。
- 用户可以直接在飞书查看、筛选和修改知识卡片。
- 符合 PRD 的 Phase 1：“文字输入、AI 整理、飞书保存”。

长期方案：

```text
MVP：飞书多维表格
增长期：PostgreSQL 主库 + 飞书作为运营视图或导出视图
```

不建议 MVP 直接上 PostgreSQL，除非马上要做多用户权限、复杂检索和正式商业化。

### 向量数据库

MVP 不做向量数据库。

未来路线：

```text
Phase 5 初期：Chroma
数据增长后：PostgreSQL + pgvector
规模化后：Milvus 或 Pinecone
```

选择逻辑：

- Chroma：适合个人开发、本地验证。
- Milvus：适合大规模向量检索。
- Pinecone：适合托管生产环境，但早期会增加成本。

### 部署方案

MVP 推荐：

```text
阿里云 ECS
→ Docker Compose
→ Nginx
→ FastAPI backend
→ HTTPS
→ DeepSeek / 飞书 / 企业微信
```

暂时不使用 Kubernetes，不拆微服务。

## 4. 项目目录结构设计

```text
memora/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── core/
│   │   ├── integrations/
│   │   ├── models/
│   │   ├── services/
│   │   └── workers/
│   ├── tests/
│   └── pyproject.toml
├── frontend/
├── docs/
├── config/
├── scripts/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

目录说明：

- `backend/`：FastAPI 后端主服务。
- `backend/app/api/`：HTTP 接口。
- `backend/app/agents/`：AI 整理器、Prompt、schema。
- `backend/app/integrations/`：DeepSeek、飞书、企业微信、OSS 等第三方集成。
- `backend/app/services/`：业务流程编排。
- `backend/tests/`：后端测试。
- `frontend/`：MVP 暂时为空，未来做管理后台。
- `docs/`：产品文档、架构文档、开发计划、部署说明。
- `config/`：Nginx、部署配置。
- `scripts/`：初始化、迁移、部署脚本。

## 5. MVP 开发计划

### Phase 0：环境准备

开发目标：

- 项目可以本地启动。
- 环境变量可配置。
- API 健康检查可用。

输入：

- Python
- Docker
- DeepSeek API Key
- 飞书应用配置

输出：

- FastAPI 服务
- `/health` 接口
- `.env.example`

验收标准：

```text
GET /health 返回 ok
```

### Phase 1：基础 AI 整理能力

开发目标：

- 输入文字，输出结构化知识卡片。

输入：

- 用户文字
- 链接文本
- 用户备注

输出：

- title
- summary
- category
- tags
- keywords

验收标准：

- 10 条测试内容字段完整率 100%。
- 摘要可读。
- 分类和标签基本可用。

### Phase 2：飞书数据库连接

开发目标：

- 将知识卡片保存到飞书多维表格。

输入：

- AI 分析结果。

输出：

- 飞书记录 ID。

验收标准：

- 调用接口后，飞书表出现正确记录。

### Phase 3：企业微信接入

开发目标：

- 用户可以在微信/企微中发送内容。

输入：

- 企业微信 webhook 消息。

输出：

- 保存成功回复。

验收标准：

- 手机发送文字后，30 秒内收到摘要和保存确认。

### Phase 4：图片理解

开发目标：

- 支持截图、图片 OCR 和视觉摘要。

输入：

- 图片消息。

输出：

- 图片内容摘要、分类、标签。

验收标准：

- 常见文章截图、课程图、资料图能提取主要信息。

### Phase 5：RAG 搜索

开发目标：

- 用户询问历史收藏内容，系统召回相关知识。

输入：

- 自然语言问题。

输出：

- 相关知识列表。
- AI 综合回答。

验收标准：

- 能通过关键词和语义找到历史保存内容。

## 6. MVP API 设计

### 健康检查

```text
GET /health
```

返回：

```json
{
  "status": "ok",
  "service": "memora-backend"
}
```

### 消息接收接口

```text
POST /api/message
```

用途：

- 接收内部统一消息。
- 本地调试时可绕过企业微信。

请求：

```json
{
  "user_id": "u_001",
  "content_type": "text",
  "content": "原始内容",
  "source_url": "https://example.com",
  "user_note": "可选备注"
}
```

返回：

```json
{
  "saved": true,
  "knowledge_id": "rec_xxx",
  "analysis": {
    "title": "标题",
    "summary": "摘要",
    "category": "AI工具",
    "tags": ["AI", "效率"],
    "keywords": ["知识库", "自动整理"]
  }
}
```

### AI 分析接口

```text
POST /api/ai/analyze
```

用途：

- 单独调试 AI 知识整理能力。

### 知识保存接口

```text
POST /api/knowledge
```

用途：

- 保存结构化知识到飞书。

### 查询接口

```text
GET /api/knowledge/search?q=xxx&user_id=u_001&limit=10
```

用途：

- MVP 可先保留接口。
- Phase 5 接入 RAG 后正式启用。

## 7. 环境变量需求

```env
APP_ENV=development
APP_NAME=memora-backend
APP_SECRET_KEY=
PUBLIC_BASE_URL=https://your-domain.com

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_MAX_TOKENS=1200
DEEPSEEK_TEMPERATURE=0.2

FEISHU_APP_ID=
FEISHU_APP_SECRET=
FEISHU_BITABLE_APP_TOKEN=
FEISHU_BITABLE_TABLE_ID=

WECHAT_CORP_ID=
WECHAT_AGENT_ID=
WECHAT_SECRET=
WECHAT_TOKEN=
WECHAT_AES_KEY=

ALIYUN_ACCESS_KEY_ID=
ALIYUN_ACCESS_KEY_SECRET=
ALIYUN_OSS_BUCKET=
ALIYUN_OSS_ENDPOINT=

DATABASE_URL=
REDIS_URL=
LOG_LEVEL=INFO
```

## 8. 开发前准备清单

账号：

- DeepSeek 开放平台
- 企业微信
- 飞书开放平台
- 阿里云
- GitHub

软件环境：

- Python 3.11 或 3.12
- Docker + Docker Compose
- Git
- Node.js LTS，未来做前端时再用

API：

- DeepSeek API Key
- 飞书 App ID、App Secret、多维表格 app token、table id
- 企业微信 Corp ID、Agent ID、Secret、Token、EncodingAESKey
- 阿里云 ECS、域名、HTTPS 证书、OSS

## 9. 技术风险分析

### 企业微信接口限制

风险：

- 验签和加解密复杂。
- 回调有超时要求。
- 消息可能重复推送。

方案：

- 先做文本消息。
- 保存 `msg_id` 去重。
- 后续将 AI 处理异步化，先快速 ACK，再主动回复。

### 小红书/抖音内容获取

风险：

- 平台限制强。
- 直接抓正文不稳定。

方案：

- MVP 不抓平台正文。
- 只保存用户转发文本、链接、截图。
- 截图理解放 Phase 4。

### 图片理解成本

风险：

- 图片多时 token 和视觉成本会上升。

方案：

- 默认压缩图片。
- 限制单用户频率。
- 图片摘要字段保持短。

### AI 分类准确率

风险：

- 分类漂移。
- 标签不一致。

方案：

- 固定分类枚举。
- Prompt 中提供 JSON 示例。
- 用户可用“分类：xxx”覆盖。

### 数据安全

风险：

- 用户知识库可能包含隐私和商业信息。

方案：

- 密钥只放后端。
- 日志不打印原文。
- 飞书权限最小化。
- 后期迁移 PostgreSQL 做用户级权限隔离。

## 10. 最终建议

如果一个人开发，第一版只做：

```text
企业微信文字入口
+ DeepSeek 结构化整理
+ 飞书多维表格保存
+ 保存成功回复
```

第一版不要做：

- RAG
- 图片理解
- 网页正文抓取
- 知识图谱
- 前端管理后台
- 多用户权限系统

技术组合：

```text
FastAPI 单体服务
+ DeepSeek deepseek-v4-flash
+ 飞书多维表格
+ 阿里云 ECS + Docker + Nginx
+ GitHub 版本管理
```

这个组合开发复杂度最低，MVP 闭环最快，同时不会堵住后续扩展路线。
