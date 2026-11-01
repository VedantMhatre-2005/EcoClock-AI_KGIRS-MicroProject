import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class DocumentLoader:
    @staticmethod
    def load_file(file_path: str) -> Dict[str, Any]:
        """
        Loads document text and metadata from PDF, DOCX, TXT, CSV, or JSON.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        title = path.stem.replace("_", " ").title()
        content = ""

        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        elif ext == ".json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    title = data.get("title", title)
                    content = data.get("content", json.dumps(data, indent=2))
                elif isinstance(data, list):
                    content = json.dumps(data, indent=2)

        elif ext == ".csv":
            import pandas as pd
            df = pd.read_csv(path)
            content = df.to_string(index=False)

        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(path))
                pages = [page.extract_text() or "" for page in reader.pages]
                content = "\n\n".join(pages)
            except Exception as e:
                # Fallback if pypdf fails
                content = f"Error extracting PDF content from {path.name}: {e}"

        elif ext == ".docx":
            try:
                import docx
                doc = docx.Document(str(path))
                paragraphs = [p.text for p in doc.paragraphs if p.text]
                content = "\n\n".join(paragraphs)
            except Exception as e:
                content = f"Error extracting DOCX content from {path.name}: {e}"

        else:
            raise ValueError(f"Unsupported document format: {ext}. Supported: PDF, DOCX, TXT, CSV, JSON.")

        return {
            "title": title,
            "content": content,
            "file_path": str(path),
            "file_size": path.stat().st_size,
            "extension": ext
        }

