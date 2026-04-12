"""
ImageOCRReader: 基于 PaddleOCR 的图像文本加载器
将含文字的图像转换为 LlamaIndex 可处理的 Document 对象
"""

import os
from pathlib import Path
from typing import List, Union

from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document


class ImageOCRReader(BaseReader):
    """使用 PP-OCR 从图像中提取文本并返回 Document"""

    def __init__(self, lang: str = "ch", use_gpu: bool = False, **kwargs):
        """
        Args:
            lang: OCR 语言 ('ch', 'en', 'fr', etc.)
            use_gpu: 是否使用 GPU 加速
            **kwargs: 其他传递给 PaddleOCR 的参数
        """
        super().__init__()
        self.lang = lang
        self.use_gpu = use_gpu
        self.extra_kwargs = kwargs
        self._ocr = None  # 延迟初始化

    def _get_ocr(self):
        """延迟初始化 PaddleOCR 实例"""
        if self._ocr is None:
            # 强制 CPU 使用 paddle 模式 (非 mkldnn)，避免 oneDNN PIR 兼容性问题
            try:
                from paddlex.inference.utils import pp_option
                _orig = pp_option.get_default_run_mode
                def _patched(model_name, device_type):
                    if device_type == "cpu":
                        return "paddle"
                    return _orig(model_name, device_type)
                pp_option.get_default_run_mode = _patched
            except ImportError:
                pass

            from paddleocr import PaddleOCR

            device = "gpu" if self.use_gpu else "cpu"
            self._ocr = PaddleOCR(
                lang=self.lang,
                device=device,
                text_detection_model_name="PP-OCRv5_mobile_det",
                text_recognition_model_name="PP-OCRv5_mobile_rec",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                **self.extra_kwargs,
            )
        return self._ocr

    def _extract_text_from_image(self, image_path: str) -> dict:
        """
        从单张图像中提取文本和元数据

        Returns:
            dict with keys: text, blocks, avg_confidence, num_blocks
        """
        ocr = self._get_ocr()
        result = ocr.predict(image_path)

        all_texts = []
        all_scores = []
        blocks = []

        for res in result:
            # PaddleOCR 3.x 结果解析
            rec_texts = []
            rec_scores = []

            # 尝试不同的访问方式以兼容不同版本
            if hasattr(res, "rec_texts"):
                rec_texts = res.rec_texts
                rec_scores = getattr(res, "rec_scores", [])
            elif isinstance(res, dict):
                inner = res.get("res", res)
                rec_texts = inner.get("rec_texts", [])
                rec_scores = inner.get("rec_scores", [])
            else:
                try:
                    data = res.res if hasattr(res, "res") else res
                    if isinstance(data, dict):
                        rec_texts = data.get("rec_texts", [])
                        rec_scores = data.get("rec_scores", [])
                except Exception:
                    pass

            if not rec_texts:
                # 回退: PaddleOCR 2.x 格式
                try:
                    if isinstance(res, list):
                        for line in res:
                            if isinstance(line, (list, tuple)) and len(line) == 2:
                                text_info = line[1]
                                if isinstance(text_info, (list, tuple)):
                                    rec_texts.append(str(text_info[0]))
                                    rec_scores.append(float(text_info[1]))
                except Exception:
                    pass

            for i, text in enumerate(rec_texts):
                text = str(text).strip()
                if not text:
                    continue
                score = float(rec_scores[i]) if i < len(rec_scores) else 0.0
                all_texts.append(text)
                all_scores.append(score)
                blocks.append({"text": text, "confidence": score, "index": len(blocks)})

        # 构建格式化文本
        formatted_lines = []
        for b in blocks:
            formatted_lines.append(
                f"[Text Block {b['index'] + 1}] (conf: {b['confidence']:.2f}): {b['text']}"
            )
        formatted_text = "\n".join(formatted_lines)

        # 纯文本版本
        plain_text = "\n".join(all_texts)
        avg_confidence = sum(all_scores) / len(all_scores) if all_scores else 0.0

        return {
            "formatted_text": formatted_text,
            "plain_text": plain_text,
            "blocks": blocks,
            "avg_confidence": avg_confidence,
            "num_blocks": len(blocks),
        }

    def load_data(self, file: Union[str, List[str]]) -> List[Document]:
        """
        从单个或多个图像文件中提取文本，返回 Document 列表

        Args:
            file: 图像路径字符串 或 路径列表

        Returns:
            List[Document]
        """
        if isinstance(file, (str, Path)):
            file_list = [str(file)]
        else:
            file_list = [str(f) for f in file]

        documents = []
        for fpath in file_list:
            if not os.path.exists(fpath):
                print(f"警告: 文件不存在，跳过: {fpath}")
                continue

            print(f"正在 OCR 识别: {fpath}")
            result = self._extract_text_from_image(fpath)

            if result["num_blocks"] == 0:
                print(f"  未检测到文本: {fpath}")
                continue

            doc = Document(
                text=result["plain_text"],
                metadata={
                    "image_path": os.path.abspath(fpath),
                    "file_name": os.path.basename(fpath),
                    "ocr_model": "PP-OCRv5",
                    "language": self.lang,
                    "num_text_blocks": result["num_blocks"],
                    "avg_confidence": round(result["avg_confidence"], 4),
                    "formatted_text": result["formatted_text"],
                },
            )
            documents.append(doc)
            print(
                f"  识别完成: {result['num_blocks']} 个文本块, "
                f"平均置信度: {result['avg_confidence']:.4f}"
            )

        return documents

    def load_data_from_dir(self, dir_path: str, extensions: tuple = (".png", ".jpg", ".jpeg", ".bmp", ".tiff")) -> List[Document]:
        """
        批量处理图像目录

        Args:
            dir_path: 图像目录路径
            extensions: 支持的图像扩展名

        Returns:
            List[Document]
        """
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")

        image_files = sorted(
            [str(f) for f in dir_path.iterdir() if f.suffix.lower() in extensions]
        )

        if not image_files:
            print(f"目录中未找到图像文件: {dir_path}")
            return []

        print(f"在目录 {dir_path} 中找到 {len(image_files)} 张图像")
        return self.load_data(image_files)
