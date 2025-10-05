#!/usr/bin/env python3
"""
PDF Text Compression Tool
Extracts and compresses PDF text to fit within token limits.
"""

import re
from pathlib import Path
from typing import List, Tuple
import PyPDF2


class PDFCompressor:
    def __init__(self, max_tokens: int = 100000):
        """
        Initialize PDF compressor.
        
        Args:
            max_tokens: Maximum token limit (default: 100k)
        """
        self.max_tokens = max_tokens
        # Rough estimate: 1 token ≈ 4 characters
        self.max_chars = max_tokens * 4
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        return len(text) // 4
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove repeated characters (e.g., "----" or "====")
        text = re.sub(r'(.)\1{4,}', r'\1\1', text)
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        return text.strip()
    
    def remove_redundancy(self, text: str) -> str:
        """Remove redundant sentences and phrases."""
        lines = text.split('\n')
        seen = set()
        unique_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Keep line if it's unique or significantly different
            line_key = line.lower()[:100]  # Use first 100 chars as key
            if line_key not in seen:
                seen.add(line_key)
                unique_lines.append(line)
        
        return '\n'.join(unique_lines)
    
    def compress_abbreviations(self, text: str) -> str:
        """Apply common abbreviations to reduce size."""
        replacements = {
            ' and ': ' & ',
            ' with ': ' w/ ',
            ' without ': ' w/o ',
            ' through ': ' thru ',
            ' between ': ' btwn ',
            ' approximately ': ' ~',
            ' percent ': '%',
            ' number ': '#',
            ' versus ': ' vs ',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def chunk_by_sections(self, text: str) -> List[Tuple[str, str]]:
        """Split text into logical sections."""
        # Try to identify sections by headers (all caps, numbered, etc.)
        sections = []
        current_section = ""
        current_title = "Introduction"
        
        lines = text.split('\n')
        for line in lines:
            # Detect section headers (simple heuristic)
            if (len(line) < 100 and 
                (line.isupper() or 
                 re.match(r'^\d+\.', line) or
                 re.match(r'^[A-Z][^.!?]*$', line))):
                if current_section:
                    sections.append((current_title, current_section.strip()))
                current_title = line.strip()
                current_section = ""
            else:
                current_section += line + "\n"
        
        if current_section:
            sections.append((current_title, current_section.strip()))
        
        return sections
    
    def compress(self, pdf_path: str, output_path: str = None) -> str:
        """
        Compress PDF text content.
        
        Args:
            pdf_path: Path to PDF file
            output_path: Optional path to save compressed text
            
        Returns:
            Compressed text
        """
        print(f"Extracting text from {pdf_path}...")
        text = self.extract_text(pdf_path)
        original_tokens = self.estimate_tokens(text)
        print(f"Original: ~{original_tokens:,} tokens")
        
        # Step 1: Clean text
        text = self.clean_text(text)
        tokens = self.estimate_tokens(text)
        print(f"After cleaning: ~{tokens:,} tokens")
        
        # Step 2: Remove redundancy
        text = self.remove_redundancy(text)
        tokens = self.estimate_tokens(text)
        print(f"After deduplication: ~{tokens:,} tokens")
        
        # Step 3: Apply abbreviations
        text = self.compress_abbreviations(text)
        tokens = self.estimate_tokens(text)
        print(f"After abbreviations: ~{tokens:,} tokens")
        
        # Step 4: If still too large, truncate intelligently
        if tokens > self.max_tokens:
            print(f"Still exceeds limit. Truncating to {self.max_tokens:,} tokens...")
            text = text[:self.max_chars]
            tokens = self.estimate_tokens(text)
        
        print(f"Final: ~{tokens:,} tokens ({(tokens/original_tokens)*100:.1f}% of original)")
        
        # Save to file if requested
        if output_path:
            Path(output_path).write_text(text, encoding='utf-8')
            print(f"Saved to {output_path}")
        
        return text


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python compress_pdf.py <pdf_file> [output_file] [max_tokens]")
        print("Example: python compress_pdf.py Trading-R1.pdf compressed.txt 100000")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"{Path(pdf_file).stem}_compressed.txt"
    max_tokens = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
    
    compressor = PDFCompressor(max_tokens=max_tokens)
    compressed_text = compressor.compress(pdf_file, output_file)
    
    print(f"\nCompression complete!")


if __name__ == "__main__":
    main()
