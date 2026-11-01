import pytest
from app.graph.entity_resolution import EntityResolver
from app.ingestion.chunker import TextChunker
from app.ingestion.metadata_extractor import MetadataExtractor

def test_entity_resolver_aliases():
    # Resolves VESIT alias
    cid, cname, etype = EntityResolver.resolve_entity("vesit green campus")
    assert cid == "VESIT"
    assert etype == "Institution"

    # Resolves Academic Block A alias
    cid, cname, etype = EntityResolver.resolve_entity("block a")
    assert cid == "BLD_ACA"
    assert etype == "Building"

    # Resolves SDG 13 alias
    cid, cname, etype = EntityResolver.resolve_entity("sdg 13")
    assert cid == "SDG_13"
    assert etype == "SDG"

def test_text_chunker_provenance():
    chunker = TextChunker(chunk_size=300, chunk_overlap=50)
    sample_text = (
        "1. VISION AND MANDATE\n\n"
        "VESIT Green Campus commits to carbon neutrality by 2040. "
        "The institution recognises the imperative of evidence-based environmental stewardship. "
        "Energy efficiency will be prioritized across all seven academic buildings."
    )
    chunks = chunker.chunk_document(
        document_id="DOC_TEST",
        text=sample_text,
        title="Test Document",
        source_type="SYNTHETIC",
        page_number=1,
        section="Mandate"
    )
    assert len(chunks) >= 1
    first = chunks[0]
    assert first["document_id"] == "DOC_TEST"
    assert first["document_title"] == "Test Document"
    assert first["chunk_id"].startswith("DOC_TEST_chk_")
    assert "source_type" in first

def test_metadata_extractor_hash():
    text = "Campus sustainability content."
    meta = MetadataExtractor.extract_metadata(
        document_id="DOC_H",
        title="Hash Test",
        content=text
    )
    assert len(meta["file_hash"]) == 64
    assert meta["file_size"] == len(text)

