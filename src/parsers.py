import re
from langchain_community.document_loaders import PDFPlumberLoader

class ConstituitionParser:
    """
    Parser for 'The Constitution of India' PDF.
    Extracts parts, chapters, and articles using regex.
    """
    def __init__(self, raw_document, index_ends: int = 32):
        self.raw_document = raw_document
        self.index_ends = index_ends
        
        # Regex Patterns
        self.part_match = re.compile(r'^PART\s+[A-Z]+')
        self.chapter_match = re.compile(r'^CHAPTER\s+[IVXLCDM]+\.')
        self.article_match = re.compile(r'^\d+[A-Z]?\.\s+[A-Z]')
        self.the_heading = re.compile(r'^\d+\s+THE CONSTITUTION OF INDIA')
        self.footnote = re.compile(r'[_]{3,}[\w\W]*', re.DOTALL)
        
        self.chunks = []

    def preprocessing(self):
        active = self.raw_document[self.index_ends:]
        for page in active:
            page.page_content = self.footnote.sub('', page.page_content)
        return active

    def parser(self):
        cleaned_pages = self.preprocessing()
        buffer = []
        current_part = "None"
        current_chapter = "None"
        current_article = "None"

        for page in cleaned_pages:
            for line in page.page_content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Remove: THE CONSTITUTION OF INDIA header
                if self.the_heading.match(line):
                    line = self.the_heading.sub('', line)
                    continue
                
                # Part match
                if self.part_match.match(line):
                    # Save current article if buffer exists
                    if current_article != "None" and buffer:
                        self.chunks.append({
                            "text": ' '.join(buffer),
                            "metadata": {
                                "document": "The Constitution of India",
                                "part": current_part,
                                "chapter": current_chapter,
                                "article": current_article,
                            }
                        })
                    current_part = line
                    current_chapter = "None"
                    current_article = "None"
                    buffer = []
                    continue
                
                # Chapter match
                elif self.chapter_match.match(line):
                    current_chapter = line
                    continue
                
                # Article match
                elif self.article_match.match(line):
                    if current_article != "None" and buffer:
                        self.chunks.append({
                            "text": ' '.join(buffer),
                            "metadata": {
                                "document": "The Constitution of India",
                                "part": current_part,
                                "chapter": current_chapter,
                                "article": current_article,
                            }
                        })
                    current_article = line
                    buffer = [line]
                    continue
                
                else:
                    buffer.append(line)

        if buffer:
            self.chunks.append({
                "text": ' '.join(buffer),
                "metadata": {
                    "document": "The Constitution of India",
                    "part": current_part,
                    "chapter": current_chapter,
                    "article": current_article,
                }
            })
        return self.chunks


class BaseLegalParser:
    """
    Parser for regular Act PDFs (BNS, BNSS, BSA, etc.).
    Extracts chapters and sections.
    """
    def __init__(self, document_path, document_title):
        self.document_path = document_path
        self.document_title = document_title

        self.chapter = re.compile(r"CHAPTER\s+[IVX]+")
        self.section = re.compile(r"^(\d+)\.\s*(.*)$")

    def document_load(self):
        loader = PDFPlumberLoader(self.document_path)
        return loader.load()

    def preprocess(self):
        raw_docs = self.document_load()
        if self.document_title == 'bns':
            return raw_docs[15:112]
        elif self.document_title == 'bnss':
            return raw_docs[15:173]
        elif self.document_title == 'bsa':
            return raw_docs[9:52]
        elif self.document_title == 'motor':
            return raw_docs[8:100]
        elif self.document_title == 'info_tech':
            return raw_docs[4:36]
        elif self.document_title == 'posh':
            return raw_docs[2:]
        else:
            return raw_docs

    def parser(self):
        current_chapter = "None"
        current_section = "None"
        chunks = list()
        buffer = list()
        clean = self.preprocess()

        for page in clean:
            page_text = page.page_content
            for line in page_text.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if self.chapter.match(line):
                    current_chapter = line
                    continue

                elif self.section.match(line):
                    if current_section != "None" and buffer:
                        chunks.append({
                            "text": " ".join(buffer),
                            "metadata": {
                                "document": self.document_title + ' act',
                                "chapter": current_chapter,
                                "section": current_section
                            }
                        })
                    current_section = self.section.match(line).group(1)
                    buffer = [line]
                    continue

                else:
                    buffer.append(line)

        if buffer:
            chunks.append({
                "text": " ".join(buffer),
                "metadata": {
                    "document": self.document_title + ' act',
                    "chapter": current_chapter,
                    "section": current_section
                }
            })

        return chunks


class IncomeParser:
    """
    Parser for 'Income Tax Act' PDF.
    Extracts chapters, chapter titles, section numbers, section titles, and bodies.
    Uses monotonicity and title layout heuristics to filter noise.
    """
    def __init__(self, document_path, document_title="income"):
        self.document_path = document_path
        self.document_title = document_title
        self.chapter_re = re.compile(r'^CHAPTER\s+[IVXLCDM]+')
        self.section_re = re.compile(r'^(\d+[A-Z]?)\.\s+([A-Z“"\'\(].*)$')
        self.sub_re = re.compile(r'^\(\d+\)|^\([a-z]\)')

    def get_numeric_val(self, sec_str):
        match = re.match(r'^(\d+)', sec_str)
        return int(match.group(1)) if match else 0

    def is_valid_section_title(self, title):
        if not title or title == "None":
            return False
        first_char = title[0]
        if not (first_char.isupper() or first_char in ['“', '"', "'"]):
            return False
        if title.endswith(';') or title.endswith(','):
            return False
        if re.match(r'^\d+\.', title):
            return False
        words = title.split()
        if words and words[0].islower():
            return False
        return True

    def parser(self):
        loader = PDFPlumberLoader(self.document_path)
        pages = loader.load()
        
        lines = []
        for p_idx, p in enumerate(pages):
            text = p.page_content
            if text:
                for line in text.split("\n"):
                    lines.append((p_idx + 1, line.strip()))
        
        sections = []
        current_chapter_num = "None"
        current_chapter_title = "None"
        expect_chapter_title = False
        
        last_chapter_line_idx = -1
        max_sec_val = 0
        raw_elements = []
        
        for line_idx, (page_num, line) in enumerate(lines):
            if not line:
                continue
            
            # Check for chapter
            if self.chapter_re.match(line):
                current_chapter_num = line
                expect_chapter_title = True
                last_chapter_line_idx = line_idx
                continue
            
            if expect_chapter_title:
                current_chapter_title = line
                expect_chapter_title = False
                last_chapter_line_idx = line_idx
                continue
            
            # Check if it's a section start
            sec_match = self.section_re.match(line)
            if sec_match:
                sec_num = sec_match.group(1)
                sec_val = self.get_numeric_val(sec_num)
                
                is_valid_seq = False
                if sec_val > max_sec_val:
                    if max_sec_val == 0 or sec_val <= max_sec_val + 15:
                        is_valid_seq = True
                        
                if is_valid_seq:
                    # Extract section title from preceding lines
                    collected_lines = []
                    back_idx = len(raw_elements) - 1
                    current_back_line_idx = line_idx - 1
                    
                    while back_idx >= 0 and current_back_line_idx > last_chapter_line_idx and len(collected_lines) < 2:
                        prev_line = raw_elements[back_idx]
                        if not prev_line:
                            break
                        if self.sub_re.match(prev_line) or self.section_re.match(prev_line):
                            break
                        if prev_line.endswith(';') or prev_line.endswith(','):
                            break
                        collected_lines.insert(0, prev_line)
                        back_idx -= 1
                        current_back_line_idx -= 1
                    
                    sec_title = "None"
                    title_lines_to_remove = 0
                    
                    if len(collected_lines) == 2:
                        combined = " ".join(collected_lines)
                        if combined[0].isupper() or combined[0] in ['“', '"', "'"]:
                            sec_title = combined
                            title_lines_to_remove = 2
                        elif collected_lines[1][0].isupper() or collected_lines[1][0] in ['“', '"', "'"]:
                            sec_title = collected_lines[1]
                            title_lines_to_remove = 1
                    elif len(collected_lines) == 1:
                        if collected_lines[0][0].isupper() or collected_lines[0][0] in ['“', '"', "'"]:
                            sec_title = collected_lines[0]
                            title_lines_to_remove = 1
                    
                    if self.is_valid_section_title(sec_title):
                        if title_lines_to_remove > 0:
                            raw_elements = raw_elements[:-title_lines_to_remove]
                        
                        if sections:
                            sections[-1]["text"] = " ".join(raw_elements)
                            raw_elements = []
                            
                        sections.append({
                            "num": sec_num,
                            "title": sec_title,
                            "chapter_num": current_chapter_num,
                            "chapter_title": current_chapter_title,
                            "text": ""
                        })
                        max_sec_val = sec_val
                        raw_elements = [line]
                        continue
            
            raw_elements.append(line)
            
        if sections and raw_elements:
            sections[-1]["text"] = " ".join(raw_elements)
            
        chunks = []
        for s in sections:
            full_text = f"Section Title: {s['title']}\n{s['text']}"
            chunks.append({
                "text": full_text,
                "metadata": {
                    "document": "income tax act",
                    "chapter": f"{s['chapter_num']}: {s['chapter_title']}",
                    "section": s['num']
                }
            })
        return chunks
