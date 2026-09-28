import pathlib
import re

from pypdf import PdfReader


class PDFReader: 
    def __init__(self, pdf_path: pathlib.Path) -> None: 
        self.reader = PdfReader(pdf_path)
        
    def get_cleaned_text(self) -> str: 
        # Extract raw text
        raw_text = self._extract_text()
        
        # Replace multiple whitespace with single space
        cleaned = re.sub(r"\s+", " ", raw_text)
        
        # Remove conrol characters
        cleaned = re.sub(r"[\x00-\x1F\x7F]", "", cleaned)
        
        # Strip leading/trailing whitespace
        return cleaned.strip() 
    
    def _extract_text(self) -> str: 
        raw_text = "" 
        for page in self.reader.pages: 
            page_text = page.extract_text()
            raw_text += page_text
        return raw_text 
    