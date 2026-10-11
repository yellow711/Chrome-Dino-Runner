# 🦖 Chrome Dino Runner (Python / Pygame 复刻版)

基于 Python 和 Pygame 精准复刻的经典 Google Chrome 断网彩蛋小游戏（Project Bolan / T-Rex Runner）。

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6%2B-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ 核心特性

- **1:1 原版官方素材**：基于 Chromium 官方 100% LDPI 精灵切片制作，还原经典的像素质感。
- **生动的帧动画**：
  - 恐龙双腿交替奔跑踏步动画
  - 空中蜷缩双腿跳跃动画
  - 贴地匍匐流线型下蹲动画
  - 翼龙双翅上下扑动飞行动画
  - 死亡定格震惊大眼表情
  - 鼠标悬停重玩按钮的齿轮旋转动效
- **真实物理引擎**：具有重力加速度、初速度阻尼和宽容碰撞箱（Forgiving Hitbox），支持空中按向下键快速下坠（Fast-Fall）。
- **无缝地面与视差云朵**：双段地表接力无限循环滚动，远处云朵以较慢速度飘移营造 2D 视差景深。
- **阶梯式动态难度**：
  - 速度随分数增长平滑递增（从 7.0 逐步飙升至 14.0）。
  - 前 300 分只刷地面仙人掌，300 分后引入低空、中空与高空翼龙。
  - 障碍物生成间距随奔跑速度自适应拉伸，保证可跳跃性。
- **复古计分系统**：
  - 官方 5 位数字字模，实时记录本局分数与历史最高分（HI）。
  - 每到 100 分触发经典的整百定格闪烁彩蛋。
- **沉浸式昼夜交替**：
  - 每 1000 分中，700 ~ 900 分自动切换至 Google 经典暗黑夜景（`#202124`）。
  - 全要素自适应反色，900 分后重迎黎明破晓。
- **开箱即用与独立打包**：支持通过 `PyInstaller` 打包为完全脱离 Python 环境的独立 `.exe` 单文件。

---

## 🎮 操作控制

| 按键 / 操作 | 动作功能 |
| :--- | :--- |
| <kbd>Space</kbd> / <kbd>↑</kbd> 或 **鼠标左键点击** | 开始游戏 / 起跳跨越障碍物 / 死亡后重新开局 |
| <kbd>↓</kbd>（地面按住） | 贴地匍匐下蹲（避开低空翼龙） |
| <kbd>↓</kbd>（空中按下） | 极速下坠（Fast-Fall 操作） |
| <kbd>Esc</kbd> | 安全退出游戏 |

---

## 🚀 快速启动

### 1. 运行源码
需要安装 Python 3.10+ 及 Pygame：

```bash
# 安装依赖
pip install pygame

# 启动游戏
python main.py
```

Windows 用户亦可在文件夹内直接双击 `run.bat` 免终端快捷启动。

### 2. 打包为单文件 `.exe`（发给他人免安装运行）

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --add-data "sprite.png;." --name "ChromeDino" main.py
```
打包生成的可执行文件将位于 `dist/ChromeDino.exe`。

---

## 📂 项目结构

```text
├── main.py          # 游戏主逻辑入口与各个实体类实现
├── sprite.png       # 官方 Chrome Dino 精灵素材贴图
├── run.bat          # Windows 双击静默启动脚本
├── .gitignore       # Git 忽略规则
└── README.md        # 项目说明文档
```

---

## 📄 开源许可

本项目遵循 [MIT License](LICENSE) 开源协议。
