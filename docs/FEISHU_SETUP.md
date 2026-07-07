# 飞书多维表格配置

## 当前 MVP 需要的权限

飞书开放平台应用至少需要开通以下权限之一：

```text
bitable:app
```

如果按细粒度权限配置，则需要：

```text
base:field:read
base:field:write
base:record:create
```

为了 MVP 快速验证，建议先开通 `bitable:app`，跑通后再收敛到细粒度权限。

## 环境变量

```env
FEISHU_APP_ID=
FEISHU_APP_SECRET=
FEISHU_BITABLE_APP_TOKEN=
FEISHU_BITABLE_TABLE_ID=
```

`FEISHU_BITABLE_APP_TOKEN` 来自多维表格 URL：

```text
https://xxx.feishu.cn/base/<APP_TOKEN>?table=<TABLE_ID>
```

`FEISHU_BITABLE_TABLE_ID` 来自 URL 查询参数 `table`。

## 初始化字段

开通权限后运行：

```powershell
python scripts\setup_feishu_fields.py
```

脚本会自动补齐 MVP 字段：

```text
user_id
title
source
original_url
raw_content
summary
category
tags
keywords
user_note
model
prompt_tokens
completion_tokens
total_tokens
```

## 验证集成

```powershell
python scripts\validate_integrations.py
```
