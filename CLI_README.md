# GraphGen 命令行工具使用说明

## 概述

`graphgen_cli.py` 是 GraphGen Demo web app 的命令行版本，提供了相同的功能但通过命令行界面使用。

## 安装依赖

确保已安装所有必要的依赖：

```bash
pip install -r requirements.txt
```

## 配置设置

### 环境变量配置

脚本支持通过环境变量配置所有参数，推荐使用 `.env` 文件进行配置：

1. **复制配置模板**：
```bash
cp config.example.env .env
```

2. **编辑配置文件**：
```bash
# 编辑 .env 文件，填入你的 API Key 和其他配置
nano .env
```

3. **主要配置项**：
```bash
# 必需配置
SYNTHESIZER_API_KEY=your_api_key_here

# 可选配置（有默认值）
SYNTHESIZER_BASE_URL=https://api.siliconflow.cn/v1
SYNTHESIZER_MODEL=Qwen/Qwen2.5-7B-Instruct
CHUNK_SIZE=1024
MAX_DEPTH=2
# ... 更多配置项
```

### 配置优先级

配置的优先级从高到低：
1. 命令行参数
2. 环境变量
3. 默认值

例如：
```bash
# 命令行参数会覆盖环境变量
python graphgen_cli.py -i input.txt -k new_api_key --chunk-size 2048
```

## 基本用法

### 1. 单个文件处理

```bash
python graphgen_cli.py -i input.txt -k your_api_key
```

### 2. 批量处理多个文件

```bash
python graphgen_cli.py -b file1.txt file2.json file3.csv -k your_api_key
```

### 3. 从文件列表批量处理

```bash
python graphgen_cli.py -l file_list.txt -k your_api_key
```

### 4. 使用 Trainee 模型

```bash
python graphgen_cli.py -i input.txt -k your_api_key --use-trainee-model --trainee-api-key your_trainee_key
```

### 5. 自定义输出文件（仅单个文件）

```bash
python graphgen_cli.py -i input.txt -k your_api_key -o custom_output.jsonl
```

### 6. 测试 API 连接

```bash
python graphgen_cli.py -k your_api_key --test-connection
```

### 7. 使用环境变量配置

如果已经配置了 `.env` 文件，可以直接运行：

```bash
# 单个文件处理（从 .env 读取配置）
python graphgen_cli.py -i input.txt

# 批量处理（从 .env 读取配置）
python graphgen_cli.py -b file1.txt file2.txt

# 测试连接（从 .env 读取配置）
python graphgen_cli.py --test-connection
```

## 参数说明

### 输入参数（三选一）

- `-i, --input-file`: 单个输入文件路径 (支持 .txt, .json, .jsonl, .csv)
- `-b, --batch-files`: 批量处理多个文件路径
- `-l, --file-list`: 包含文件路径列表的文本文件

### 必需参数

- `-k, --api-key`: SiliconFlow API Key (可通过环境变量 `SYNTHESIZER_API_KEY` 设置)

### 可选参数

- `-o, --output-file`: 单个文件的输出路径 (批量处理时忽略)
- `--test-connection`: 仅测试 API 连接

### 模型配置

- `--use-trainee-model`: 使用 Trainee 模型
- `--synthesizer-url`: Synthesizer API URL (环境变量: `SYNTHESIZER_BASE_URL`)
- `--synthesizer-model`: Synthesizer 模型名称 (环境变量: `SYNTHESIZER_MODEL`)
- `--trainee-url`: Trainee API URL (环境变量: `TRAINEE_BASE_URL`)
- `--trainee-model`: Trainee 模型名称 (环境变量: `TRAINEE_MODEL`)
- `--trainee-api-key`: Trainee 模型的 API Key (环境变量: `TRAINEE_API_KEY`)

### 生成配置

- `--chunk-size`: 文本块大小 (默认: 1024)
- `--chunk-overlap`: 文本块重叠大小 (默认: 100)
- `--tokenizer`: Tokenizer 名称 (默认: cl100k_base)
- `--output-data-type`: 输出数据类型 (默认: aggregated)
  - 选项: atomic, multi_hop, aggregated
- `--output-data-format`: 输出数据格式 (默认: Alpaca)
  - 选项: Alpaca, Sharegpt, ChatML
- `--quiz-samples`: 测验样本数量 (默认: 2)

### 遍历策略

- `--bidirectional`: 双向遍历
- `--expand-method`: 扩展方法 (默认: max_tokens)
  - 选项: max_width, max_tokens
- `--max-extra-edges`: 最大额外边数 (默认: 5)
- `--max-tokens`: 最大 token 数 (默认: 256)
- `--max-depth`: 最大深度 (默认: 2)
- `--edge-sampling`: 边采样策略 (默认: max_loss)
  - 选项: max_loss, min_loss, random
- `--isolated-node-strategy`: 孤立节点策略 (默认: ignore)
  - 选项: add, ignore
- `--loss-strategy`: 损失策略 (默认: only_edge)
  - 选项: only_edge, both

### 限制配置

- `--rpm`: 每分钟请求数 (默认: 1000)
- `--tpm`: 每分钟 token 数 (默认: 50000)

## 示例

### 示例 1: 处理单个文本文件

```bash
python graphgen_cli.py \
  -i example_input.txt \
  -k sk-your-api-key-here \
  --chunk-size 2048 \
  --max-depth 3
```

### 示例 2: 批量处理多个文件

```bash
python graphgen_cli.py \
  -b example_input.txt example_input2.txt example_input3.txt \
  -k sk-your-api-key-here \
  --chunk-size 1024
```

### 示例 3: 从文件列表批量处理

```bash
python graphgen_cli.py \
  -l file_list.txt \
  -k sk-your-api-key-here \
  --use-trainee-model
```

### 示例 4: 使用 Trainee 模型处理 JSON 文件

```bash
python graphgen_cli.py \
  -i data/input.json \
  -k sk-your-api-key-here \
  --use-trainee-model \
  --trainee-api-key sk-your-trainee-key-here \
  --output-data-type atomic \
  --quiz-samples 5
```

### 示例 5: 自定义所有参数

```bash
python graphgen_cli.py \
  -i input.csv \
  -k sk-your-api-key-here \
  -o custom_output.jsonl \
  --use-trainee-model \
  --synthesizer-model "Qwen/Qwen2.5-14B-Instruct" \
  --trainee-model "Qwen/Qwen2.5-7B-Instruct" \
  --chunk-size 1536 \
  --chunk-overlap 200 \
  --tokenizer cl100k_base \
  --output-data-type multi_hop \
  --output-data-format Sharegpt \
  --bidirectional \
  --expand-method max_width \
  --max-extra-edges 8 \
  --max-depth 4 \
  --edge-sampling min_loss \
  --isolated-node-strategy add \
  --loss-strategy both \
  --rpm 500 \
  --tpm 25000
```

## 输出

### 单个文件处理输出

脚本会输出以下信息：

1. **进度信息**: 各个处理步骤的状态
2. **Token 统计**: 源文本 token 数量和预计使用量
3. **API 连接状态**: 连接测试结果
4. **运行结果**: 成功/失败状态和输出文件位置
5. **实际使用统计**: Synthesizer 和 Trainee 模型的实际 token 使用量

### 批量处理输出

批量处理会提供更详细的信息：

1. **进度条**: 显示当前处理进度和正在处理的文件
2. **详细日志**: 自动生成带时间戳的日志文件
3. **统计总结**: 处理完成后显示总体统计信息
4. **错误处理**: 单个文件失败不会影响其他文件的处理

#### 日志文件内容

批量处理会自动生成日志文件，包含：

- **配置信息**: 所有处理参数的详细记录
- **文件处理结果**: 每个文件的处理状态、token使用量、处理时间
- **错误信息**: 失败文件的详细错误原因
- **统计总结**: 总体处理统计和性能指标

## 错误处理

脚本包含完整的错误处理机制：

- 输入文件验证
- API 连接测试
- 参数验证
- 运行时错误捕获

## 注意事项

1. 确保有足够的 API 配额
2. 大文件处理可能需要较长时间
3. 使用 Trainee 模型会增加 token 消耗
4. 输出文件格式为 JSONL，包含生成的知识图谱训练数据

## 批量处理功能

### 批量处理特性

1. **多种输入方式**:
   - 直接指定多个文件: `-b file1.txt file2.json file3.csv`
   - 从文件列表加载: `-l file_list.txt`

2. **进度显示**: 使用进度条实时显示处理进度

3. **详细日志**: 自动生成带时间戳的详细日志文件

4. **错误容错**: 单个文件处理失败不会影响其他文件

5. **统计信息**: 提供详细的处理统计和性能指标

### 文件列表格式

文件列表文件（`-l` 参数）支持以下格式：

```
# 这是注释行
example_input.txt
example_input2.txt
example_input3.txt
# 更多文件...
```

- 每行一个文件路径
- 以 `#` 开头的行为注释
- 空行会被忽略

### 批量处理输出

每个输入文件会生成对应的输出文件：
- 输入: `example_input.txt`
- 输出: `example_input_graphgen_output.jsonl`

### 性能建议

1. **并发限制**: 根据API限制调整 `--rpm` 和 `--tpm` 参数
2. **文件大小**: 大文件建议增加 `--chunk-size` 和 `--max-tokens`
3. **内存使用**: 批量处理时会为每个文件创建独立的工作空间

## 从 Web App 迁移

如果你之前使用 web app，以下是主要差异：

1. **参数设置**: 通过命令行参数而非 UI 界面设置
2. **文件处理**: 支持单个文件和批量处理
3. **输出**: 自动保存到指定文件，无需手动下载
4. **进度显示**: 通过控制台输出和进度条显示进度
5. **日志记录**: 批量处理提供详细的日志文件

## 支持的文件格式

- **.txt**: 纯文本文件
- **.json**: JSON 格式文件
- **.jsonl**: JSON Lines 格式文件  
- **.csv**: CSV 格式文件 (需要包含 content 列或使用第一列)
