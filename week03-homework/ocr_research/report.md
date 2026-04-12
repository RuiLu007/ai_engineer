# 作业二：为 LlamaIndex 构建 OCR 图像文本加载器

## 1. 架构设计

### 核心组件

```
test_images/           PaddleOCR          ImageOCRReader         LlamaIndex
  *.png      ───────>  PP-OCRv5    ───>   load_data()     ───>  Document[]
  *.jpg                mobile_det         load_data_from_dir()     │
                       mobile_rec                                  v
                                                            VectorStoreIndex
                                                                   │
                                                                   v
                                                            QueryEngine
```

**ImageOCRReader** 继承自 `llama_index.core.readers.base.BaseReader`，负责：
1. 延迟初始化 PaddleOCR 引擎
2. 对图像执行 OCR 文本检测 + 识别
3. 将识别结果封装为 LlamaIndex `Document` 对象（含丰富元数据）

### 关键设计决策

| 决策 | 选型 | 理由 |
|------|------|------|
| OCR 引擎 | PaddleOCR PP-OCRv5 mobile | 百度开源中文 OCR，准确率高，CPU 兼容性好 |
| 推理模式 | paddle (非 mkldnn) | PaddlePaddle 3.x 的 oneDNN 在部分 CPU 上有 PIR 兼容性问题 |
| 初始化 | 延迟加载 | 避免导入时即加载模型，提升模块导入速度 |
| 结果格式 | 纯文本 + 格式化文本 | text 字段存纯文本便于检索，metadata 存格式化文本便于分析 |

## 2. 核心代码说明

### ImageOCRReader 类

```python
class ImageOCRReader(BaseReader):
    def __init__(self, lang="ch", use_gpu=False, **kwargs):
        self._ocr = None  # 延迟初始化

    def _get_ocr(self):
        # 关键：monkey-patch paddlex，强制 CPU 使用 paddle 模式（非 mkldnn）
        from paddlex.inference.utils import pp_option
        pp_option.get_default_run_mode = lambda m, d: "paddle" if d == "cpu" else ...

        self._ocr = PaddleOCR(
            text_detection_model_name="PP-OCRv5_mobile_det",
            text_recognition_model_name="PP-OCRv5_mobile_rec",
            device="cpu", ...
        )

    def _extract_text_from_image(self, image_path):
        # 调用 ocr.predict()，兼容 3.x 和 2.x 结果格式
        result = ocr.predict(image_path)
        # 解析 rec_texts / rec_scores，构建 blocks

    def load_data(self, file) -> List[Document]:
        # 遍历图像文件，OCR 提取，返回 Document 列表
        # Document.text = 纯文本，Document.metadata 含详细信息
```

### Document 元数据设计

每个 Document 包含以下 metadata：

| 字段 | 类型 | 说明 |
|------|------|------|
| `image_path` | str | 图像文件绝对路径 |
| `file_name` | str | 文件名 |
| `ocr_model` | str | 使用的 OCR 模型名称 |
| `language` | str | OCR 语言设置 |
| `num_text_blocks` | int | 检测到的文本块数量 |
| `avg_confidence` | float | 平均置信度 |
| `formatted_text` | str | 带置信度的格式化文本 |

## 3. 实验结果

### 3.1 OCR 识别准确率

| 图像类型 | 文件名 | 文本块数 | 平均置信度 | 说明 |
|----------|--------|----------|------------|------|
| 扫描文档 | scanned_document.png | 32 | 0.9792 | 登机牌图片，中英文混合 |
| 自然场景 | scene.png | 7 | 0.9806 | PIL 生成的路标/店招场景 |
| 截图 | screenshot.png | 16 | 0.9758 | PIL 生成的系统设置界面 |

**总结**：PP-OCRv5 mobile 模型在三种不同类型的图像上均达到 97%+ 的平均置信度，表现优秀。

### 3.2 识别文本示例

**扫描文档 (scanned_document.png)**:
```
[Text Block 1] (conf: 1.00): www.997788.com
[Text Block 2] (conf: 1.00): 登机牌
[Text Block 3] (conf: 0.97): BOARDING PASS
[Text Block 4] (conf: 0.99): 舱位CLASS
[Text Block 5] (conf: 0.94): 序号 SERIAL NO.
```

### 3.3 RAG 集成查询结果

| 查询问题 | 回答摘要 | 主要来源 | 来源得分 |
|----------|----------|----------|----------|
| 图片中提到了什么航班信息？ | MU 2379, 03DEC, 太原→福州, G11 登机口 | scanned_document.png | 0.6970 |
| 图片中有哪些系统配置信息？ | Ubuntu 22.04 LTS, Python 3.11.5, PostgreSQL 15.2, 8.2GB/16GB 内存 | screenshot.png | 0.6536 |
| 图片中提到了什么地名或位置？ | 北京, 福州, 太原, G11 登机口 | scene.png | 0.5645 |

## 4. 遇到的问题与解决方案

### 4.1 PaddlePaddle 3.x oneDNN 兼容性问题

**问题**：PaddlePaddle 3.x 在 CPU 推理时默认启用 oneDNN (mkldnn) 加速，但在部分 CPU 上会触发 `NotImplementedError: ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]` 错误。

**尝试过的方案**：
1. ❌ 设置环境变量 `FLAGS_use_mkldnn=0` — 无效
2. ❌ `paddle.set_flags({'FLAGS_use_mkldnn': 0})` — 无效
3. ❌ 降级到 PaddlePaddle 2.x — PyPI 上没有 Python 3.11 的 wheel
4. ❌ 从百度源安装 paddlepaddle 2.6.2 — 与 paddleocr 2.10+ 仍不兼容
5. ✅ **Monkey-patch paddlex 的 `get_default_run_mode`** 函数，强制 CPU 返回 `"paddle"` 而非 `"mkldnn"`

**最终方案**：在 `_get_ocr()` 中注入 monkey-patch：
```python
from paddlex.inference.utils import pp_option
_orig = pp_option.get_default_run_mode
def _patched(model_name, device_type):
    if device_type == "cpu":
        return "paddle"
    return _orig(model_name, device_type)
pp_option.get_default_run_mode = _patched
```

### 4.2 PaddleOCR API 版本差异

PaddleOCR 2.10+ 虽然版本号是 2.x，但已采用 3.x 架构（依赖 paddlex），API 为 `ocr.predict()` 而非旧版的 `ocr.ocr()`。代码中实现了两种格式的兼容解析。

## 5. 局限性与改进方向

### 当前局限
- **表格/复杂排版**：OCR 按文本块顺序返回结果，无法保留表格的行列结构
- **手写体**：PP-OCRv5 主要针对印刷体优化，手写识别可能精度不足
- **大图片处理**：单张大图的 OCR 延迟较高（首次推理约 5-10s）

### 改进方向
1. **Layout 分析**：结合 PaddleX 的版面分析模型，先识别文档区域再分别 OCR
2. **文本排序优化**：按坐标位置对文本块排序，还原阅读顺序
3. **批处理优化**：利用 PaddleOCR 的批处理能力提升吞吐量
4. **缓存机制**：对已处理图像缓存 OCR 结果，避免重复计算
5. **GPU 加速**：在有 CUDA 的环境下启用 GPU 推理

## 6. 运行方式

```bash
cd week03-homework
uv sync
PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True uv run python -m ocr_research.main
```
