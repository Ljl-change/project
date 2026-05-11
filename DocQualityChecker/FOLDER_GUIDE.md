# DocQualityChecker 文件夹功能说明

本文档用于说明当前 `DocQualityChecker` 项目根目录下每个文件夹的作用，方便开发、展示、交接和后续维护。

## 1. `assets/`

用途：
用于存放项目展示资源。

当前作用：
- 预留放置界面截图
- 预留放置 Logo
- 预留放置说明图片或演示素材

典型内容：
- `assets/ui_demo.png`
- `assets/README.md`

适用场景：
- GitHub README 展示
- 项目答辩截图
- 演示文档插图

## 2. `docs/`

用途：
用于存放项目文档说明文件。

当前作用：
- 存放检测规则解释文档
- 对规则原理、局限性、可能误报进行说明

当前核心文件：
- `docs/rules_explain.md`

适用场景：
- 向用户解释规则原理
- 向评审展示项目可解释性
- 后续扩展更完整开发文档

## 3. `docx/`

用途：
当前这个目录更像是本地运行环境或依赖环境目录，不属于项目核心源码目录。

当前作用：
- 可能是你本地创建的 Python 虚拟环境
- 其中通常包含 `Scripts/`、`Lib/`、`site-packages/` 等运行环境文件

说明：
- 这个目录不是 DocQualityChecker 的业务逻辑目录
- 如果后续上传 GitHub，通常不建议把这种本地环境目录提交到仓库

适用场景：
- 本地开发运行
- 隔离项目依赖

建议：
- 后续可以确认是否要加入 `.gitignore`

## 4. `doc_quality_checker/`

用途：
这是项目的核心源码目录。

当前作用：
- 存放文档检测后端逻辑
- 存放 CLI 逻辑
- 存放规则引擎
- 存放报告生成逻辑
- 存放 AI 报告优化逻辑

主要内容包括：
- `cli.py`：命令行入口逻辑
- `checker.py`：检测总控制器
- `docx_reader.py`：读取 `.docx`
- `rules.py`：规则检测实现
- `report_generator.py`：Markdown 报告生成
- `models.py`：核心数据结构
- `utils.py`：通用工具函数
- `ai_prompts.py`：AI 提示词模板
- `ai_reporter.py`：AI 总结调用逻辑

适用场景：
- 项目核心功能开发
- 后续扩展新规则
- 扩展更多输入格式

## 5. `examples/`

用途：
用于放置示例输入文档。

当前作用：
- 提供可直接测试的示例 `.docx`
- 让用户安装后能快速运行项目

当前内容：
- `examples/sample.docx`
- `examples/README.md`

适用场景：
- 命令行示例运行
- 前端上传测试
- GitHub 演示

## 6. `outputs/`

用途：
用于存放程序运行后的输出结果。

当前作用：
- 保存 Markdown 报告
- 保存 Streamlit 上传文件
- 保存 Streamlit 生成的报告

当前子目录说明：

### `outputs/uploads/`
用途：
- 保存 Streamlit 前端上传的原始 `.docx` 文件副本

作用：
- 让前端上传文件可以被后端检测逻辑读取

### `outputs/streamlit_reports/`
用途：
- 保存通过前端界面生成的 Markdown 报告

作用：
- 便于用户在网页中下载报告
- 便于保留前端检测历史输出

### `outputs/` 根目录本身
用途：
- 也可保存命令行默认输出的报告，例如 `outputs/check_report.md`

适用场景：
- 检测结果保存
- 报告归档
- 演示成果留存

## 7. `tests/`

用途：
用于存放测试代码和测试资料说明。

当前作用：
- 验证规则检测是否正常
- 验证 CLI 是否正常
- 验证集成流程是否正常
- 验证源码中是否出现中文乱码

当前主要测试文件：
- `tests/test_cli.py`
- `tests/test_rules.py`
- `tests/test_integration.py`
- `tests/test_encoding.py`

当前子目录说明：

### `tests/fixtures/`
用途：
- 预留放置真实或半真实测试样本文档

作用：
- 后续用于补充多种 docx 测试场景

### `tests/expected/`
用途：
- 预留放置预期检测结果说明

作用：
- 后续做回归测试、快照测试时使用

### `tests/__pycache__/`
用途：
- Python 运行测试后自动生成的缓存目录

作用：
- 提升模块加载速度
- 不属于手写业务逻辑

适用场景：
- 规则验证
- 回归测试
- 可靠性增强

## 8. `__pycache__/`

用途：
这是 Python 自动生成的缓存目录。

当前作用：
- 缓存已编译的 `.pyc` 文件
- 提升脚本重复运行时的导入速度

说明：
- 不属于项目业务逻辑目录
- 一般不需要手动维护
- 上传 GitHub 时通常应被忽略

## 9. 总结

当前项目各文件夹可以分成四类：

### 核心开发目录
- `doc_quality_checker/`
- `docs/`
- `tests/`

### 展示与示例目录
- `assets/`
- `examples/`

### 运行输出目录
- `outputs/`

### 环境与缓存目录
- `docx/`
- `__pycache__/`

如果一句话概括：

- `doc_quality_checker/` 负责“功能实现”
- `docs/` 负责“规则说明”
- `tests/` 负责“可靠性验证”
- `examples/` 负责“示例输入”
- `outputs/` 负责“结果输出”
- `assets/` 负责“项目展示”
- `docx/` 和 `__pycache__/` 更偏“本地运行环境与缓存”
