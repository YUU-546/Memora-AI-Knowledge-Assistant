# 企业微信回调配置排查

企业微信保存回调 URL 时，会立刻请求：

```text
GET /api/wechat/callback?msg_signature=...&timestamp=...&nonce=...&echostr=...
```

服务端必须：

1. 使用 `WECHAT_TOKEN`、`timestamp`、`nonce`、`echostr` 校验签名。
2. 使用 `WECHAT_AES_KEY` 解密 `echostr`。
3. 返回解密后的明文字符串。

普通 JSON 响应会导致企业微信报错。

## 当前推荐 URL

```text
https://econ-lab.xyz/api/wechat/callback
```

## 阿里云侧必须确认

### 1. DNS 解析

`econ-lab.xyz` 需要解析到 ECS 公网 IP。

### 2. ECS 安全组

至少放行：

```text
80/tcp
443/tcp
```

### 3. Nginx HTTPS

企业微信要求公网可访问的 URL。建议使用 HTTPS，并由 Nginx 反向代理到本机后端：

```text
https://econ-lab.xyz
→ nginx:443
→ 127.0.0.1:8000
→ FastAPI
```

### 4. 后端服务

服务器上需要运行：

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

或用 Docker Compose / systemd 常驻。

## 本地检查命令

```powershell
Invoke-WebRequest -Uri "https://econ-lab.xyz/health" -UseBasicParsing
Invoke-WebRequest -Uri "https://econ-lab.xyz/api/wechat/callback" -UseBasicParsing
```

第二个命令如果不带企业微信参数，返回 422 是正常的；说明服务已经通了。

## 常见错误

### openapi 回调地址请求不通过

常见原因：

- 域名没有解析到 ECS。
- ECS 安全组未开放 443。
- Nginx 没配置 HTTPS 证书。
- Nginx 没反向代理到 FastAPI。
- FastAPI 没运行。
- 后端没有实现企业微信 GET 验证协议。
- `.env` 中 `WECHAT_TOKEN` 或 `WECHAT_AES_KEY` 与企业微信后台不一致。

### HTTP 502

说明请求到了 Nginx，但 Nginx 找不到后端服务。检查：

```text
127.0.0.1:8000 是否运行
proxy_pass 是否正确
```

### HTTPS 连接关闭

通常是：

- 443 未放行。
- 证书未配置。
- Nginx 443 server block 有问题。
- 证书和域名不匹配。
