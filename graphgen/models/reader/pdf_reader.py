import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from graphgen.bases.base_reader import BaseReader
from graphgen.models.reader.txt_reader import TXTReader
from graphgen.utils import logger


class PDFReader(BaseReader):
    """
    PDF files are converted using MinerU, see [MinerU](https://github.com/opendatalab/MinerU).
    After conversion, the generated markdown file is read using TxtReader and pictures can be used for VQA tasks.
    """

    def __init__(
        self,
        *,
        output_dir: Optional[Union[str, Path]] = None,
        method: str = "auto",  # auto | txt | ocr
        lang: Optional[str] = None,  # ch / en / ja / ...
        backend: Optional[
            str
        ] = None,  # pipeline | vlm-transformers | vlm-sglang-engine | vlm-sglang-client
        device: Optional[str] = None,  # cpu | cuda | cuda:0 | npu | mps
        source: Optional[str] = None,  # huggingface | modelscope | local
        vlm_url: Optional[str] = None,  # 当 backend=vlm-sglang-client 时必填
        start_page: Optional[int] = None,  # 0-based
        end_page: Optional[int] = None,  # 0-based， inclusive
        formula: bool = True,
        table: bool = True,
        return_assets: bool = True,
        **other_mineru_kwargs: Any,
    ):
        super().__init__()
        self.output_dir = os.path.join(output_dir, "mineru") if output_dir else None

        self._default_kwargs: Dict[str, Any] = {
            "method": method,
            "lang": lang,
            "backend": backend,
            "device": device,
            "source": source,
            "vlm_url": vlm_url,
            "start_page": start_page,
            "end_page": end_page,
            "formula": formula,
            "table": table,
            **other_mineru_kwargs,
        }
        self._default_kwargs = {
            k: v for k, v in self._default_kwargs.items() if v is not None
        }
        self.return_assets = return_assets
        self.parser = MinerUParser()
        self.txt_reader = TXTReader()

    def read(self, file_path: str, **override) -> List[Dict[str, Any]]:
        """
        file_path
        **override: override MinerU parameters
        """
        pdf_path = Path(file_path).expanduser().resolve()
        if not pdf_path.is_file():
            raise FileNotFoundError(pdf_path)

        kwargs = {**self._default_kwargs, **override}

        mineru_result = self._call_mineru(pdf_path, kwargs)
        return mineru_result

    def _call_mineru(
        self, pdf_path: Path, kwargs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        output_dir: Optional[str] = None
        if self.output_dir:
            output_dir = str(self.output_dir)

        return self.parser.parse_pdf(pdf_path, output_dir=output_dir, **kwargs)

    def _locate_md(self, pdf_path: Path, kwargs: Dict[str, Any]) -> Optional[Path]:
        out_dir = (
            Path(self.output_dir) if self.output_dir else Path(tempfile.gettempdir())
        )
        method = kwargs.get("method", "auto")
        backend = kwargs.get("backend", "")
        if backend.startswith("vlm-"):
            method = "vlm"

        candidate = Path(
            os.path.join(out_dir, pdf_path.stem, method, f"{pdf_path.stem}.md")
        )
        if candidate.exists():
            return candidate
        candidate = Path(os.path.join(out_dir, f"{pdf_path.stem}.md"))
        if candidate.exists():
            return candidate
        return None


class MinerUParser:
    def __init__(self) -> None:
        self._check_bin()

    @staticmethod
    def parse_pdf(
        pdf_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        method: str = "auto",
        device: str = "cpu",
        **kw: Any,
    ) -> List[Dict[str, Any]]:
        pdf = Path(pdf_path).expanduser().resolve()
        if not pdf.is_file():
            raise FileNotFoundError(pdf)

        out = (
            Path(output_dir) if output_dir else Path(tempfile.mkdtemp(prefix="mineru_"))
        )
        out.mkdir(parents=True, exist_ok=True)

        cached = MinerUParser._try_load_cached_result(str(out), pdf.stem, method)
        if cached is not None:
            return cached

        MinerUParser._run_mineru(pdf, out, method, device, **kw)

        cached = MinerUParser._try_load_cached_result(str(out), pdf.stem, method)
        return cached if cached is not None else []

    @staticmethod
    def _try_load_cached_result(
        out_dir: str, pdf_stem: str, method: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        try to load cached json result from MinerU output.
        :param out_dir:
        :param pdf_stem:
        :param method:
        :return:
        """
        json_file = os.path.join(
            out_dir, pdf_stem, method, f"{pdf_stem}_content_list.json"
        )
        if not os.path.exists(json_file):
            return None

        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Failed to load cached MinerU result: %s", exc)
            return None

        base = os.path.dirname(json_file)
        results = []
        for item in data:
            for key in ("img_path", "table_img_path", "equation_img_path"):
                rel_path = item.get(key)
                if rel_path:
                    item[key] = str(Path(base).joinpath(rel_path).resolve())
            if item["type"] == "text":
                item["content"] = item["text"]
                del item["text"]
            for key in ("page_idx", "bbox", "text_level"):
                if item.get(key) is not None:
                    del item[key]
            if item["type"] == "text" and not item["content"].strip():
                continue
            results.append(item)
        return results

    @staticmethod
    def _run_mineru(
        pdf: Path,
        out: Path,
        method: str,
        device: str,
        **kw: Any,
    ) -> None:
        cmd = [
            "mineru",
            "-p",
            str(pdf),
            "-o",
            str(out),
            "-m",
            method,
            "-d",
            device,
        ]
        for k, v in kw.items():
            if v is None:
                continue
            if isinstance(v, bool):
                cmd += [f"--{k}", str(v).lower()]
            else:
                cmd += [f"--{k}", str(v)]

        logger.info("Parsing PDF with MinerU: %s", pdf)
        logger.debug("Running MinerU command: %s", " ".join(cmd))

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"MinerU failed: {proc.stderr or proc.stdout}")

    @staticmethod
    def _check_bin() -> None:
        try:
            subprocess.run(
                ["mineru", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise RuntimeError(
                "MinerU is not installed or not found in PATH. Please install it from pip: \n"
                "pip install -U 'mineru[core]'"
            ) from exc
