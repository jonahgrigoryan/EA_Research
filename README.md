# PDF Text Compression Tools

Two approaches to compress PDF text content to fit within token limits.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Compression (`compress_pdf.py`)
Fast compression using cleaning, deduplication, and abbreviations:

```bash
python compress_pdf.py Trading-R1.pdf
python compress_pdf.py Trading-R1.pdf output.txt 100000
```

### Advanced Compression (`compress_pdf_advanced.py`)
Semantic compression that preserves important sentences:

```bash
python compress_pdf_advanced.py Trading-R1.pdf
python compress_pdf_advanced.py Trading-R1.pdf output.txt 100000
```

## Techniques Used

**Basic Compression:**
- Whitespace normalization
- Redundancy removal
- Common abbreviations
- Intelligent truncation

**Advanced Compression:**
- Extractive summarization
- Sentence importance scoring
- Word frequency analysis
- Semantic preservation

## Token Estimation

Both tools use a rough estimate: **1 token ≈ 4 characters**

Adjust `max_tokens` parameter based on your needs (default: 100,000).
