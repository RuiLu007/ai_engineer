# 运行train.py文件
(MLOps) lurui@LAPTOP-15J211ON:~/00ai_engineer/ai_engineer_github202602/projects/project3_1$ python train.py 
开始构建FAQ索引...
错误：请设置DASHSCOPE_API_KEY环境变量
project3_1/config.py

你这个问题非常关键！`os.getenv("DASHSCOPE_API_KEY", "")` 是从 **操作系统的环境变量** 中读取 `DASHSCOPE_API_KEY` 的值。

那么，**在哪里设置这个环境变量？** 有多种方式，下面按推荐顺序详细说明：

---

## ✅ 推荐方式 1：使用 `.env` 文件（最常用、最安全）

> 适用于本地开发，避免把密钥写进代码或提交到 Git

### 步骤：

#### 1. 在项目根目录创建 `.env` 文件
```
your_project/
├── .env          ← 新建这个文件
├── main.py
└── requirements.txt
```

#### 2. 在 `.env` 中写入：
```ini
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> 🔒 注意：
> - 不要加引号
> - 不要加分号
> - 文件名是 `.env`（前面有个点）

#### 3. 安装 `python-dotenv` 库（让 Python 能读 `.env`）
```bash
pip install python-dotenv
```

#### 4. 在 Python 代码最开头加载 `.env`
```python
# main.py 或 app.py 的最顶部
from dotenv import load_dotenv
import os

load_dotenv()  # ← 这行会自动读取 .env 并加载到环境变量

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
print("API Key:", DASHSCOPE_API_KEY[:10] + "...")  # 打印前10位验证
```

✅ **优点**：
- 密钥不进代码
- 可通过 `.gitignore` 忽略 `.env`，防止泄露
- 团队协作时每人有自己的 `.env`

> 📌 记得在 `.gitignore` 中加上：
> ```
> .env
> ```

---

## ✅ 方式 2：直接在终端设置环境变量（临时）

### Linux / macOS / WSL：
```bash
export DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
python your_script.py
```

### Windows (CMD)：
```cmd
set DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
python your_script.py
```

### Windows (PowerShell)：
```powershell
$env:DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxx"
python your_script.py
```

> ⚠️ 缺点：关闭终端后失效，不适合长期使用。

---

## ✅ 方式 3：系统级环境变量（长期但不灵活）

- **Windows**：  
  设置 → 系统 → 关于 → 高级系统设置 → 环境变量 → 用户变量 → 新建

- **Linux/macOS**：  
  把 `export DASHSCOPE_API_KEY=...` 加到 `~/.bashrc` 或 `~/.zshrc`

> ❌ 不推荐用于项目密钥，因为：
> - 多个项目密钥会冲突
> - 难以管理不同环境（dev/staging/prod）

---

## ✅ 方式 4：部署时（如服务器、Docker、云平台）

| 平台 | 设置方式 |
|------|--------|
| **Docker** | `docker run -e DASHSCOPE_API_KEY=sk-xxx ...` |
| **Docker Compose** | 在 `docker-compose.yml` 的 `environment:` 中设置 |
| **Vercel / Render / Railway** | 在 Web 控制台的 "Environment Variables" 中添加 |
| **Linux 服务器** | 用 `systemd` 服务文件或 `.env` + `dotenv` |

---

## 🛑 绝对不要这样做！

```python
# ❌ 千万不要硬编码在代码里！
DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxxxxxx"  # 会被 Git 提交，极度危险！
```

---

## ✅ 最佳实践总结

| 场景 | 推荐方式 |
|------|--------|
| **本地开发** | `.env` + `python-dotenv` |
| **团队协作** | `.env.example` 提供模板，每人填自己的 `.env` |
| **Docker** | 用 `-e` 或 `env_file` |
| **生产部署** | 云平台的环境变量管理界面 |

---

## 📁 项目结构示例

```
ai_project/
├── .gitignore          # 包含 .env
├── .env                # ← 你的密钥在这里（不提交！）
├── .env.example        # ← 示例文件（可提交）
├── main.py
└── requirements.txt
```

`.env.example` 内容（供团队参考）：
```ini
# Rename to .env and fill in your keys
DASHSCOPE_API_KEY=your_api_key_here
```

---

现在你可以安全地配置 DashScope API Key 了！🔐  
记得：**永远不要把密钥提交到 Git！**


