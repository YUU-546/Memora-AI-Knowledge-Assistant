# GitHub 云端保存指南

当前项目已经初始化为本地 Git 仓库，并创建了初始提交。

## 1. 在 GitHub 创建仓库

建议仓库名：

```text
memora
```

创建时保持空仓库即可，不要勾选 README、.gitignore 或 license，因为本地已经有这些文件。

## 2. 绑定远程仓库

替换下面的地址为你的真实仓库地址：

```powershell
git remote add origin https://github.com/<your-name>/memora.git
```

## 3. 推送到 GitHub

```powershell
git push -u origin main
```

## 4. 后续开发流程

```powershell
git status
git add .
git commit -m "Describe the change"
git push
```

## 5. 注意事项

- 不要提交 `.env`。
- API Key 只放本地 `.env` 或云服务器环境变量。
- `.env.example` 只保留变量名和示例值。
- 如果要公开仓库，确认 `1.0/` 下的产品文档可以公开。
