# .gitignore テンプレート

スキャフォールドで生成される `.gitignore` の内容。

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.venv/
venv/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Build
dist/
*.skill

# Test
test-output/
workspace/
```

## カスタマイズのポイント

- Node.js プロジェクトの場合: `node_modules/` を追加
- Rust プロジェクトの場合: `target/` を追加
- `.skill` は配布用パッケージ。git管理したい場合は除外行を削除
