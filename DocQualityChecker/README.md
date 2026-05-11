# DocQualityChecker

DocQualityChecker 是一个面向中文文档场景的文档规范性与质量检测工具。它适用于论文、课程报告、比赛材料、软著说明书、项目报告等 `.docx` 文档的提交前自查，可以自动发现结构缺失、段落过长、标题层级异常、图表编号异常、未完成标记残留和基础排版问题，并生成 Markdown 检测报告。

当前项目已经具备三层能力：

- 规则检测引擎：负责结构化、可解释的启发式检测
- Streamlit 可视化界面：适合普通用户上传文档直接使用
- AI 报告优化：基于规则结果生成更自然的中文总结与修改建议

> DocQualityChecker 当前采用启发式规则检测，适合用于提交前自查和格式初筛。检测结果具有参考价值，但不能替代人工审阅、正式查重、排版软件或专业审稿流程。

## 功能概览

| 功能 | 说明 |
|---|---|
| 文档结构检查 | 检查摘要、关键词、引言/绪论、结论/总结、参考文献等章节是否存在 |
| 段落质量检查 | 检测过长段落、过短段落、连续空段 |
| 未完成标记检测 | 识别 `TODO`、`待补充`、`XXX`、`这里写` 等残留占位内容 |
| 标题层级检查 | 检测标题过长、只有编号、跳级、编号不连续 |
| 图表编号检查 | 检测图表编号重复、不连续，以及“如图所示”但附近无图号的情况 |
| 基础格式检查 | 识别多空格、重复标点、括号不匹配、中英文标点混用 |
| Markdown 报告输出 | 生成适合留档、分享和版本管理的检测报告 |
| AI 报告优化 | 基于规则检测结果生成总体评价、主要问题和修改优先级 |

## 安装方法

推荐使用 Python 3.9 及以上版本。

```bash
git clone <your-repo-url>
cd DocQualityChecker
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux / macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 快速开始

### 命令行模式

检测示例文档：

```bash
python main.py --file examples/sample.docx
```

指定输出路径：

```bash
python main.py --file examples/sample.docx --output outputs/report.md
```

修改段落长度阈值：

```bash
python main.py --file examples/sample.docx --max-paragraph-length 300
```

启用 AI 报告优化：

```bash
python main.py --file examples/sample.docx --enable-ai
```

### 可视化界面模式

启动前端：

```bash
streamlit run app.py
```

然后在浏览器打开：

```text
http://localhost:8501
```

前端适合普通用户直接上传 `.docx` 文档，查看评分、问题列表、分类统计和 Markdown 报告，并可选择是否启用 AI 优化。

## 项目目录说明

当前项目根目录下主要文件夹作用如下：

| 文件夹 | 作用 |
|---|---|
| `doc_quality_checker/` | 核心源码目录，包含读取、规则、CLI、报告生成和 AI 模块 |
| `docs/` | 存放项目说明文档，例如规则解释文档 |
| `examples/` | 存放示例输入文档，例如 `sample.docx` |
| `outputs/` | 存放程序输出结果、上传文件和生成的报告 |
| `tests/` | 存放自动化测试代码 |
| `assets/` | 存放项目展示资源，例如界面截图 |
| `docx/` | 当前更像本地运行环境目录，不属于核心业务源码 |
| `__pycache__/` | Python 自动生成的缓存目录 |

如果你想看更详细的文件夹说明，可以查看：

- [FOLDER_GUIDE.md](C:/Users/pc/Desktop/DocQualityChecker/FOLDER_GUIDE.md)

## 检测规则说明

当前版本重点覆盖以下规则：

1. 文档结构完整性：摘要、关键词、引言/绪论、结论/总结、参考文献
2. 段落长度与空段：过长段落、过短段落、连续空段
3. 未完成内容标记：`TODO`、`待补充`、`XXX`、`待确认` 等
4. 标题层级与标题编号：标题过长、编号后无标题、层级跳跃、编号不连续
5. 图表编号：图/表编号重复、简单不连续、引用无图号
6. 基础格式问题：多空格、重复标点、括号不匹配、中英文标点混用

每条问题都会附带：

- `rule_id`：规则编号，例如 `STRUCTURE_005`
- `confidence`：可信度，取值为 `high / medium / low`
- `principle`：简要说明该问题的检测原理

更完整的规则说明见：

- [docs/rules_explain.md](C:/Users/pc/Desktop/DocQualityChecker/docs/rules_explain.md)

## 可靠性说明

DocQualityChecker 当前采用启发式规则检测，适合用于提交前自查和格式初筛。检测结果具有参考价值，但不能替代人工审阅、正式查重、排版软件或专业审稿流程。

可以这样理解问题可信度：

- 高可信度问题：通常由明确规则触发，例如 TODO、括号不匹配、明显段落过长
- 中可信度问题：通常由关键词或编号规则触发，例如章节缺失、图表编号不连续
- 低可信度问题：通常需要人工判断，例如标题命名特殊、文档类型特殊

## AI 报告优化功能

AI 功能不会替代规则检测，也不会保证文档完全合格。AI 只基于规则引擎输出的结构化检测结果进行语言总结和修改建议生成。

AI 优化内容包括：

- 总体评价
- 主要问题概括
- 修改优先级
- 面向用户的自然语言建议
- 可直接写入报告末尾的 AI 优化建议

AI 功能特点：

- 默认关闭，需用户主动启用
- 未配置 API Key 时自动跳过
- 调用失败时不影响原始规则检测
- 不会覆盖原始问题列表
- 默认不会发送完整原文，只发送统计信息、结构检查结果、问题列表和必要短片段

## API Key 配置方法

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="你的 API Key"
```

macOS / Linux:

```bash
export OPENAI_API_KEY="你的 API Key"
```

可选模型环境变量：

```bash
DOC_QUALITY_CHECKER_AI_MODEL=gpt-4.1-mini
```

## 隐私说明

- AI 优化功能默认不会上传整篇原始文档
- 上传到 AI 的内容仅限文档统计信息、结构检查结果、问题列表和必要短片段
- 如果你计划公网部署该工具，请不要上传包含敏感信息、未脱敏数据或保密材料的文档

## AI 功能限制说明

AI 仅做“规则结果总结”，不是“全文审稿器”。因此：

- AI 不会新增规则引擎没有发现的问题
- AI 不会声称已经人工审阅全文
- AI 不会给出“文档一定合格”的绝对结论
- AI 输出仍然建议结合人工复核一起使用

## 测试方法

安装依赖后运行：

```bash
pytest tests/
```

当前测试包括：

- `tests/test_rules.py`：不依赖真实 `.docx`，验证规则函数与报告生成
- `tests/test_integration.py`：使用示例文档验证完整检测流程
- `tests/test_cli.py`：验证 CLI 的友好异常提示
- `tests/test_encoding.py`：验证源码中没有典型中文乱码

## 输出目录说明

- 命令行默认报告：`outputs/check_report.md`
- 前端上传文件：`outputs/uploads/`
- 前端生成报告：`outputs/streamlit_reports/`

## 重要文件说明

| 文件 | 作用 |
|---|---|
| `main.py` | 项目入口，负责调用 CLI |
| `app.py` | Streamlit 前端入口 |
| `USER_GUIDE.md` | 面向使用者的详细操作说明 |
| `FOLDER_GUIDE.md` | 面向开发/交接的文件夹功能说明 |
| `requirements.txt` | 项目依赖 |
| `.gitignore` | Git 忽略规则 |

## 项目结构

```text
DocQualityChecker/
├── app.py
├── assets/
├── docs/
│   └── rules_explain.md
├── doc_quality_checker/
│   ├── __init__.py
│   ├── ai_prompts.py
│   ├── ai_reporter.py
│   ├── checker.py
│   ├── cli.py
│   ├── docx_reader.py
│   ├── models.py
│   ├── report_generator.py
│   ├── rules.py
│   └── utils.py
├── examples/
│   └── sample.docx
├── outputs/
│   ├── streamlit_reports/
│   └── uploads/
├── tests/
│   ├── expected/
│   ├── fixtures/
│   ├── test_cli.py
│   ├── test_encoding.py
│   ├── test_integration.py
│   └── test_rules.py
├── FOLDER_GUIDE.md
├── USER_GUIDE.md
├── .editorconfig
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## 界面截图

你可以在运行后自行截图并保存到 `assets/` 目录，例如：

```text
assets/ui_demo.png
```

README 展示写法如下：

```md
![界面示例](assets/ui_demo.png)
```

如果暂时没有截图，可以先保留下面这段注释：

<!-- ![界面示例](assets/ui_demo.png) -->

## 免责声明

DocQualityChecker 的定位是“提交前自检工具”，用于帮助用户发现常见文档质量风险。它不能替代：

- 正式论文审稿
- 学术查重
- 专业排版工具
- 人工校对与内容审核

建议在正式提交前，将本工具结果与人工复核结合使用。
