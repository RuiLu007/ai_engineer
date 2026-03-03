# 新的Ubuntu如何安装miniconda，管理环境？
在 **全新的 Ubuntu 系统**（包括 WSL 中的 Ubuntu）上安装 Miniconda 并管理 Python 环境，是科学计算、AI 开发和项目隔离的最佳实践之一。以下是 **2026 年最新、最简洁、最推荐的操作流程**，适用于 Ubuntu 22.04 / 24.04 及 WSL。

---

## ✅ 一、为什么用 Miniconda？

- 比 Anaconda 轻量（只含 `conda` + Python，无预装包）
- 强大的环境管理能力（可同时存在 Python 3.8、3.11、3.12 等）
- 支持 `pip` 和 `conda` 双包管理
- 适合 AI/数据科学项目（如 PyTorch、TensorFlow、Jupyter）

> 💡 注意：你之前用了 `uv`，它更快更现代；但如果你需要 `conda-forge` 的特定包（如 `gdal`、`bioconda` 工具），Miniconda 仍是首选。

---

## 📥 二、安装 Miniconda（官方推荐方式）

### 步骤 1：下载安装脚本（使用清华镜像加速）

```bash
# 进入家目录
cd ~

# 从清华镜像站下载最新 Miniconda（Linux 64位）
wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

> 🔁 如果你想指定 Python 版本（如 py311），可替换为：
> ```bash
> wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py311_25.7.0-2-Linux-x86_64.sh
> ```

---

### 步骤 2：运行安装脚本

```bash
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
```

- `-b`：batch 模式（无需交互）
- `-p`：指定安装路径为 `~/miniconda3`

---

### 步骤 3：初始化 conda（自动配置 PATH）

```bash
# 初始化 shell（支持 bash/zsh）
~/miniconda3/bin/conda init

# 重新加载 shell 配置
source ~/.bashrc
```

> ✅ 验证是否成功：
> ```bash
> conda --version
> # 输出类似：conda 25.7.0
> ```

---

### 步骤 4（可选）：关闭 base 环境自动激活

避免每次打开终端都进入 `(base)`：

```bash
conda config --set auto_activate_base false
```

---

## 🧪 三、基本环境管理命令

| 操作 | 命令 |
|------|------|
| **创建新环境**（如 `myai`，Python 3.11） | `conda create -n myai python=3.11 -y` |
| **激活环境** | `conda activate myai` |
| **查看当前环境** | `conda info --envs` 或 `conda env list` |
| **列出已安装包** | `conda list` |
| **安装包**（来自 conda-forge） | `conda install -c conda-forge numpy pandas jupyter` |
| **安装 pip 包** | `pip install torch torchvision` |
| **退出环境** | `conda deactivate` |
| **删除环境** | `conda env remove -n myai` |

---

## 🛠️ 四、实战：为你的 AI 项目创建环境

假设你要为 `week03` 项目创建独立环境：

```bash
# 1. 创建环境（Python 3.11）
conda create -n week03 python=3.11 -y

# 2. 激活环境
conda activate week03

# 3. 安装基础工具
conda install -c conda-forge jupyter ipykernel -y

# 4. 注册 Jupyter 内核（这样 Lab 能识别）
python -m ipykernel install --user --name=week03 --display-name="AI工程化(week03)"

# 5. 安装项目依赖（如果有 requirements.txt）
pip install -r requirements.txt

# 6. 运行代码
cd ~/00ai_engineer/ai_engineer_github202602/week03/code
python p18-logging.py
```

---

## 🔄 五、与 `uv` 对比（供你选择）

| 特性 | `uv` | `Miniconda` |
|------|------|-------------|
| 速度 | ⚡ 极快（Rust 编写） | 较慢 |
| Python 管理 | 自动下载 CPython | 需手动指定或用 `conda` 安装 |
| 包来源 | PyPI（pip 兼容） | conda + pip（支持非 Python 依赖）|
| 生信/AI 生态 | 一般 | 强（conda-forge / bioconda）|
| 学习成本 | 低 | 中 |

> ✅ **建议**：
> - 纯 Python 项目 → 用 `uv`
> - 需要 `gdal`、`samtools`、`pytorch-cuda` 等复杂依赖 → 用 **Miniconda**

---

## 🧹 六、卸载 Miniconda（如需）

```bash
# 删除安装目录
rm -rf ~/miniconda3

# 清理 ~/.bashrc 中的 conda 配置
nano ~/.bashrc  # 手动删除 conda 相关行
# 或用 sed（谨慎！）
sed -i '/# >>> conda initialize >>>/,/# <<< conda initialize <<</d' ~/.bashrc

# 重载配置
source ~/.bashrc
```

---

## ✅ 总结：新 Ubuntu 安装 Miniconda 三步走

```bash
# 1. 下载
wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 2. 安装
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

# 3. 初始化
~/miniconda3/bin/conda init
source ~/.bashrc
conda config --set auto_activate_base false  # 推荐
```

然后就可以用 `conda create -n xxx` 管理你的开发环境了！

> 🎯 **提示**：你可以在不同项目中使用不同环境，彻底告别 `ModuleNotFoundError` 和版本冲突！

如需我帮你写一个 **Miniconda + Jupyter + PyTorch 的一键环境脚本**，也可以告诉我！

# 我已经用conda创建了MLOps，如何用venv在创建一个环境？想要图中的效果，2层激活的虚拟环境吗？没有找到scrips

你现在的目标是：

> ✅ 在已有的 `conda` 环境（如 `MLOps`）中，**再创建一个 `venv` 虚拟环境**，实现 **“双层激活”** 的效果（类似图中 `(venv) (MLOps)`），并安装 `requirements.txt` 中的包。

---

## 🧩 一、为什么需要双层环境？

- **外层：conda 环境（MLOps）**  
  → 管理 Python 版本（3.12）、全局依赖（如 CUDA、Jupyter）
- **内层：venv 虚拟环境（project1_1）**  
  → 隔离项目依赖（如 langchain、tavily），避免污染 conda 环境

✅ 这种结构常见于：
- 多项目共享同一个 conda 环境
- 每个项目有独立的 `requirements.txt`
- 使用 VS Code + Terminal 时显示清晰层级

---

## 🔧 二、如何在 conda 环境中创建 venv？

### 步骤 1：进入你的 conda 环境（确保激活）

```bash
conda activate MLOps
```

> ✅ 查看是否激活成功：
> ```bash
> python --version
> # 应输出 Python 3.12.x
> ```

---

### 步骤 2：在项目目录下创建 venv

假设你的项目路径是：
```
~/workspace/project/project1_1
```

进入该目录并创建虚拟环境：

```bash
cd ~/workspace/project/project1_1
python -m venv venv
```

> ✅ 创建后会生成 `venv/` 文件夹（Windows 是 `Scripts`，Linux/macOS 是 `bin`）

---

### 步骤 3：激活 venv（双层激活）

#### ✅ Linux / macOS（你的情况）：

```bash
source venv/bin/activate
```

#### ⚠️ Windows（如果用的是 CMD 或 PowerShell）：

```cmd
venv\Scripts\activate.bat
```

> 💡 注意：`venv\Scripts\` 是 Windows 上的路径，Linux/macOS 是 `venv/bin/`

---

### 步骤 4：验证双层激活状态

你应该看到终端提示符变成：

```bash
(venv) (MLOps) lurui@LAPTOP-15J211ON:~/workspace/project/project1_1$
```

> ✅ 表示：
> - 外层：`MLOps`（conda 环境）
> - 内层：`venv`（Python 虚拟环境）

---

### 步骤 5：安装项目依赖

```bash
pip install -r requirements.txt
```

> ✅ 安装完成后，`pip list` 只会显示 `requirements.txt` 中的包。

---

### 步骤 6：查看 pip 和 Python 版本

```bash
python --version
# 输出：Python 3.12.11（与 conda 一致）

pip list
# 显示 langchain-core, tavily-python 等
```

---

## 📂 三、文件结构说明（以 Linux 为例）

```
~/workspace/project/project1_1/
├── requirements.txt
├── venv/                  ← 由 python -m venv 创建
│   ├── bin/
│   │   └── python         ← 实际调用的是 conda 的 Python
│   └── lib/
└── your_code.py
```

> 💡 `venv/bin/python` 是符号链接，指向 conda 的 Python，但包只安装在 `venv/lib/python3.12/site-packages/`

---

## 🔄 四、退出环境

```bash
deactivate  # 先退出 venv
conda deactivate  # 再退出 conda
```

---

## 🤔 五、为什么没有 `Scripts`？（你问的问题）

- **Linux/macOS**：`venv/bin/`（不是 Scripts）
- **Windows**：`venv\Scripts\`（你截图中的情况）

你在 Linux 上运行 `venv/bin/activate` 就对了，不需要找 `Scripts`。

---

## ✅ 总结：完整流程

```bash
# 1. 激活 conda 环境
conda activate MLOps

# 2. 进入项目目录
cd ~/workspace/project/project1_1

# 3. 创建 venv
python -m venv venv

# 4. 激活 venv（Linux/macOS）
source venv/bin/activate

# 5. 安装依赖
pip install -r requirements.txt

# 6. 验证
python --version
pip list
```

现在你就拥有了：
- `(venv) (MLOps)` 的双层提示
- 项目隔离的依赖
- 与图中完全一致的效果！

---

## 💡 建议：简化操作

你可以写个脚本 `setup.sh`：

```bash
#!/bin/bash
conda activate MLOps
cd ~/workspace/project/project1_1
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✅ 环境搭建完成！"
```

运行：
```bash
chmod +x setup.sh
./setup.sh
```

这样下次快速复现！

如有需要，我也可以帮你生成 Windows 版本的批处理脚本。

# 安装太慢，如何配置pip 的清华源
在 Ubuntu（或任何 Linux 系统）中，**pip 安装慢**通常是因为默认使用了国外的 PyPI 源。你可以通过配置 **清华大学 PyPI 镜像源**（国内最快之一）来大幅提升下载速度。

---

## ✅ 方法一：临时使用清华源（单次命令）

在 `pip install` 时加上 `-i` 参数：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> ✅ 优点：不用改配置，适合偶尔使用  
> ❌ 缺点：每次都要加参数

---

## ✅ 方法二：永久配置清华源（推荐！）

### 步骤 1：创建 pip 配置目录（如果不存在）

```bash
mkdir -p ~/.config/pip
```

### 步骤 2：创建或编辑配置文件

```bash
nano ~/.config/pip/pip.conf
```

### 步骤 3：粘贴以下内容

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
```

> 💡 说明：
> - `index-url`：指定默认源
> - `trusted-host`：避免 HTTPS 警告（因为有些旧系统证书问题）
> - `timeout`：延长超时时间，防止网络波动中断

按 `Ctrl+O` → 回车保存，`Ctrl+X` 退出。

---

## ✅ 验证是否生效

```bash
pip config list
```

输出应包含：
```
global.index-url='https://pypi.tuna.tsinghua.edu.cn/simple'
```

然后随便装个小包测试速度：
```bash
pip install requests
```
→ 你会看到下载地址是 `pypi.tuna.tsinghua.edu.cn`，速度飞快！

---

## 🧪 特别注意：在虚拟环境中也生效吗？

✅ **是的！**  
`~/.config/pip/pip.conf` 是**用户级配置**，对所有环境（包括 conda、venv、uv 的 .venv）都生效。

> 除非你在某个项目里有 `pip.conf` 覆盖它（一般不会）。

---

## 🔁 其他国内镜像源（备选）

| 镜像 | 地址 |
|------|------|
| 清华大学 | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| 阿里云 | `https://mirrors.aliyun.com/pypi/simple/` |
| 豆瓣 | `https://pypi.douban.com/simple/` |
| 中科大 | `https://pypi.mirrors.ustc.edu.cn/simple/` |

> ⚠️ 推荐优先用 **清华源**，稳定且同步及时。

---

## 🛠️ 如果你用的是 `uv`（你之前用过）

`uv` 也支持镜像源！配置方式不同：

```bash
# 临时
uv pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 永久（设置环境变量）
echo 'export UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"' >> ~/.bashrc
source ~/.bashrc
```

但既然你现在用 `pip`，先配好 `pip.conf` 即可。

---

## ✅ 总结

```bash
# 1. 创建配置目录
mkdir -p ~/.config/pip

# 2. 写入清华源配置
cat > ~/.config/pip/pip.conf <<EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
EOF

# 3. 验证
pip config list
```

✅ 配置完成后，**所有 `pip install` 命令都会自动走清华源**，速度提升 5~10 倍！

现在你可以愉快地安装 `requirements.txt` 了：

```bash
pip install -r requirements.txt
```

如有其他问题（如 conda 源、npm 源），也可以继续问我！