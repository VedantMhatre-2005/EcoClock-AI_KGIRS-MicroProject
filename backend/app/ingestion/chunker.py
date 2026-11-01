import re
from typing import List, Dict, Any, Optional

class TextChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        document_id: str,
        text: str,
        title: str = "",
        source_type: str = "SYNTHETIC",
        page_number: int = 1,
        section: str = "General"
    ) -> List[Dict[str, Any]]:
        """
        Splits document text into overlapping chunks, preserving sentence and paragraph
        boundaries wherever possible, and attaching required provenance metadata.
        """
        if not text or not text.strip():
            return []

        # Split text into paragraphs first
        paragraphs = re.split(r'\n\s*\n', text.strip())
        chunks: List[Dict[str, Any]] = []
        current_chunk_text = ""
        current_section = section
        chunk_index = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if paragraph looks like a section header (e.g. "1. VISION AND MANDATE", "## SECTION")
            header_match = re.match(r'^(?:[0-9]+[\.\)]|#+)\s+([A-Z\s]{3,50})', para)
            if header_match:
                current_section = header_match.group(1).strip().title()

            # If paragraph itself is larger than chunk_size, split by sentences
            if len(para) > self.chunk_size:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    if len(current_chunk_text) + len(sentence) + 1 <= self.chunk_size:
                        current_chunk_text += (" " if current_chunk_text else "") + sentence
                    else:
                        if current_chunk_text:
                            chunk_id = f"{document_id}_chk_{chunk_index:03d}"
                            chunks.append({
                                "chunk_id": chunk_id,
                                "document_id": document_id,
                                "document_title": title,
                                "chunk_index": chunk_index,
                                "content": current_chunk_text,
                                "char_length": len(current_chunk_text),
                                "page_number": page_number,
                                "section": current_section,
                                "source_type": source_type
                            })
                            chunk_index += 1
                            # Retain overlap from end of current chunk
                            overlap_start = max(0, len(current_chunk_text) - self.chunk_overlap)
                            overlap_text = current_chunk_text[overlap_start:].strip()
                            current_chunk_text = (overlap_text + " " + sentence).strip()
                        else:
                            current_chunk_text = sentence[:self.chunk_size]
            else:
                if len(current_chunk_text) + len(para) + 2 <= self.chunk_size:
                    current_chunk_text += ("\n\n" if current_chunk_text else "") + para
                else:
                    if current_chunk_text:
                        chunk_id = f"{document_id}_chk_{chunk_index:03d}"
                        chunks.append({
                            "chunk_id": chunk_id,
                            "document_id": document_id,
                            "document_title": title,
                            "chunk_index": chunk_index,
                            "content": current_chunk_text,
                            "char_length": len(current_chunk_text),
                            "page_number": page_number,
                            "section": current_section,
                            "source_type": source_type
                        })
                        chunk_index += 1
                        overlap_start = max(0, len(current_chunk_text) - self.chunk_overlap)
                        overlap_text = current_chunk_text[overlap_start:].strip()
                        current_chunk_text = (overlap_text + "\n\n" + para).strip()
                    else:
                        current_chunk_text = para

        if current_chunk_text:
            chunk_id = f"{document_id}_chk_{chunk_index:03d}"
            chunks.append({
                "chunk_id": chunk_id,
                "document_id": document_id,
                "document_title": title,
                "chunk_index": chunk_index,
                "content": current_chunk_text,
                "char_length": len(current_chunk_text),
                "page_number": page_number,
                "section": current_section,
                "source_type": source_type
            })

        return chunks

