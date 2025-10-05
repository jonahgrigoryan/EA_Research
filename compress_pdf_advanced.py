#!/usr/bin/env python3
"""
Advanced PDF Text Compression with Semantic Chunking
Uses extractive summarization to preserve key information.
"""

import re
from pathlib import Path
from collections import Counter
import PyPDF2


class AdvancedPDFCompressor:
    def __init__(self, max_tokens: int = 100000, compression_ratio: float = 0.5):
        """
        Initialize advanced PDF compressor.
        
        Args:
            max_tokens: Maximum token limit
            compression_ratio: Target compression (0.5 = 50% of original)
        """
        self.max_tokens = max_tokens
        self.compression_ratio = compression_ratio
        self.max_chars = max_tokens * 4
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF."""
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count."""
        return len(text) // 4
    
    def sentence_tokenize(self, text: str) -> list:
        """Split text into sentences."""
        # Simple sentence splitter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def calculate_sentence_scores(self, sentences: list) -> dict:
        """
        Score sentences by importance using word frequency.
        Higher scores = more important sentences.
        """
        # Build word frequency table
        words = []
        for sentence in sentences:
            words.extend(re.findall(r'\b\w+\b', sentence.lower()))
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                     'to', 'for', 'of', 'with', 'by', 'from', 'is', 'was', 
                     'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had'}
        words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Calculate word frequencies
        word_freq = Counter(words)
        max_freq = max(word_freq.values()) if word_freq else 1
        
        # Normalize frequencies
        for word in word_freq:
            word_freq[word] = word_freq[word] / max_freq
        
        # Score sentences
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            score = 0
            words_in_sentence = re.findall(r'\b\w+\b', sentence.lower())
            for word in words_in_sentence:
                if word in word_freq:
                    score += word_freq[word]
            
            # Bonus for first/last sentences (often important)
            if i < 3 or i >= len(sentences) - 3:
                score *= 1.2
            
            # Bonus for sentences with numbers (often contain data)
            if re.search(r'\d', sentence):
                score *= 1.1
            
            sentence_scores[i] = score
        
        return sentence_scores
    
    def extractive_summarize(self, text: str, target_ratio: float) -> str:
        """
        Perform extractive summarization by selecting top sentences.
        
        Args:
            text: Input text
            target_ratio: Fraction of sentences to keep (0.0 to 1.0)
        """
        sentences = self.sentence_tokenize(text)
        if not sentences:
            return text
        
        # Score sentences
        scores = self.calculate_sentence_scores(sentences)
        
        # Select top N sentences
        num_sentences = max(1, int(len(sentences) * target_ratio))
        top_indices = sorted(scores, key=scores.get, reverse=True)[:num_sentences]
        
        # Maintain original order
        top_indices.sort()
        
        # Reconstruct text
        summary = ' '.join(sentences[i] for i in top_indices)
        return summary
    
    def compress(self, pdf_path: str, output_path: str = None) -> str:
        """Compress PDF with semantic preservation."""
        print(f"Extracting text from {pdf_path}...")
        text = self.extract_text(pdf_path)
        original_tokens = self.estimate_tokens(text)
        print(f"Original: ~{original_tokens:,} tokens")
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'(.)\1{4,}', r'\1\1', text)
        
        # Calculate target size
        target_tokens = min(self.max_tokens, int(original_tokens * self.compression_ratio))
        
        if original_tokens <= self.max_tokens:
            print("PDF already fits within token limit!")
            compressed = text
        else:
            # Apply extractive summarization
            ratio = target_tokens / original_tokens
            print(f"Applying extractive summarization (keeping {ratio*100:.1f}% of content)...")
            compressed = self.extractive_summarize(text, ratio)
        
        final_tokens = self.estimate_tokens(compressed)
        print(f"Final: ~{final_tokens:,} tokens ({(final_tokens/original_tokens)*100:.1f}% of original)")
        
        if output_path:
            Path(output_path).write_text(compressed, encoding='utf-8')
            print(f"Saved to {output_path}")
        
        return compressed


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python compress_pdf_advanced.py <pdf_file> [output_file] [max_tokens]")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"{Path(pdf_file).stem}_compressed.txt"
    max_tokens = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
    
    compressor = AdvancedPDFCompressor(max_tokens=max_tokens)
    compressor.compress(pdf_file, output_file)


if __name__ == "__main__":
    main()
