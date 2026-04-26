"""
Markdown renderer for formatting chat messages.
"""

import re
import logging
from typing import Optional
from PyQt6.QtGui import QTextDocument, QFont
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt


class MarkdownRenderer:
    """Renders markdown text to formatted HTML for display in chat."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Markdown patterns
        self.patterns = {
            'bold': re.compile(r'\*\*(.*?)\*\*'),
            'italic': re.compile(r'\*(.*?)\*'),
            'code_inline': re.compile(r'`(.*?)`'),
            'code_block': re.compile(r'```(.*?)```', re.DOTALL),
            'header': re.compile(r'^(#{1,6})\s+(.*)$', re.MULTILINE),
            'list_item': re.compile(r'^\s*[-*+]\s+(.*)$', re.MULTILINE),
            'numbered_list': re.compile(r'^\s*\d+\.\s+(.*)$', re.MULTILINE),
            'link': re.compile(r'\[(.*?)\]\((.*?)\)'),
            'blockquote': re.compile(r'^>\s+(.*)$', re.MULTILINE),
            'strikethrough': re.compile(r'~~(.*?)~~'),
            'horizontal_rule': re.compile(r'^\s*[-*_]{3,}\s*$', re.MULTILINE)
        }
    
    def render_to_html(self, text: str, theme: str = "dark") -> str:
        """Convert markdown text to HTML."""
        if not text:
            return ""
        
        html = text
        
        # Escape HTML entities first
        html = self._escape_html(html)
        
        # Process code blocks first (to avoid interfering with other patterns)
        html = self._process_code_blocks(html)
        
        # Process other markdown elements
        html = self._process_headers(html)
        html = self._process_bold(html)
        html = self._process_italic(html)
        html = self._process_strikethrough(html)
        html = self._process_inline_code(html)
        html = self._process_links(html)
        html = self._process_blockquotes(html)
        html = self._process_lists(html)
        html = self._process_horizontal_rules(html)
        
        # Wrap in HTML document with theme-specific styling
        html = self._wrap_html(html, theme)
        
        return html
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML entities."""
        html_escape_table = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }
        return "".join(html_escape_table.get(c, c) for c in text)
    
    def _process_code_blocks(self, text: str) -> str:
        """Process code blocks."""
        def replace_code_block(match):
            code = match.group(1).strip()
            # Escape HTML in code blocks
            escaped_code = self._escape_html(code)
            return f'<pre><code>{escaped_code}</code></pre>'
        
        return self.patterns['code_block'].sub(replace_code_block, text)
    
    def _process_headers(self, text: str) -> str:
        """Process headers."""
        def replace_header(match):
            level = len(match.group(1))
            content = match.group(2).strip()
            return f'<h{level}>{content}</h{level}>'
        
        return self.patterns['header'].sub(replace_header, text)
    
    def _process_bold(self, text: str) -> str:
        """Process bold text."""
        return self.patterns['bold'].sub(r'<strong>\1</strong>', text)
    
    def _process_italic(self, text: str) -> str:
        """Process italic text."""
        return self.patterns['italic'].sub(r'<em>\1</em>', text)
    
    def _process_strikethrough(self, text: str) -> str:
        """Process strikethrough text."""
        return self.patterns['strikethrough'].sub(r'<del>\1</del>', text)
    
    def _process_inline_code(self, text: str) -> str:
        """Process inline code."""
        def replace_inline_code(match):
            code = match.group(1)
            escaped_code = self._escape_html(code)
            return f'<code>{escaped_code}</code>'
        
        return self.patterns['code_inline'].sub(replace_inline_code, text)
    
    def _process_links(self, text: str) -> str:
        """Process links."""
        def replace_link(match):
            text = match.group(1)
            url = match.group(2)
            return f'<a href="{url}" target="_blank">{text}</a>'
        
        return self.patterns['link'].sub(replace_link, text)
    
    def _process_blockquotes(self, text: str) -> str:
        """Process blockquotes."""
        def replace_blockquote(match):
            content = match.group(1).strip()
            return f'<blockquote>{content}</blockquote>'
        
        return self.patterns['blockquote'].sub(replace_blockquote, text)
    
    def _process_lists(self, text: str) -> str:
        """Process lists."""
        lines = text.split('\n')
        in_list = False
        list_type = None
        result = []
        
        for line in lines:
            if self.patterns['list_item'].match(line):
                if not in_list or list_type != 'ul':
                    if in_list:
                        result.append('</ul>')
                    result.append('<ul>')
                    in_list = True
                    list_type = 'ul'
                
                content = self.patterns['list_item'].sub(r'\1', line)
                result.append(f'<li>{content}</li>')
            
            elif self.patterns['numbered_list'].match(line):
                if not in_list or list_type != 'ol':
                    if in_list:
                        result.append('</ol>')
                    result.append('<ol>')
                    in_list = True
                    list_type = 'ol'
                
                content = self.patterns['numbered_list'].sub(r'\1', line)
                result.append(f'<li>{content}</li>')
            
            else:
                if in_list:
                    result.append(f'</{list_type}>')
                    in_list = False
                    list_type = None
                result.append(line)
        
        if in_list:
            result.append(f'</{list_type}>')
        
        return '\n'.join(result)
    
    def _process_horizontal_rules(self, text: str) -> str:
        """Process horizontal rules."""
        return self.patterns['horizontal_rule'].sub('<hr>', text)
    
    def _wrap_html(self, content: str, theme: str) -> str:
        """Wrap content in HTML with theme styling."""
        if theme == "dark":
            styles = """
            body {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Ubuntu Mono', monospace;
                font-size: 14px;
                line-height: 1.6;
                margin: 0;
                padding: 10px;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #7ee0ff;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            code {
                background-color: #3c3c3c;
                color: #7ee0ff;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Ubuntu Mono', monospace;
            }
            pre {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
                border-left: 3px solid #7ee0ff;
            }
            pre code {
                background-color: transparent;
                padding: 0;
                color: inherit;
            }
            blockquote {
                border-left: 3px solid #7ee0ff;
                padding-left: 15px;
                margin: 15px 0;
                color: #cccccc;
                font-style: italic;
            }
            a {
                color: #2bd9ff;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            ul, ol {
                margin: 10px 0;
                padding-left: 20px;
            }
            li {
                margin: 5px 0;
            }
            hr {
                border: none;
                border-top: 1px solid #555555;
                margin: 20px 0;
            }
            strong {
                color: #7ee0ff;
                font-weight: bold;
            }
            em {
                color: #cfe9ff;
                font-style: italic;
            }
            del {
                color: #888888;
                text-decoration: line-through;
            }
            """
        else:  # light theme
            styles = """
            body {
                background-color: #ffffff;
                color: #333333;
                font-family: 'Ubuntu Mono', monospace;
                font-size: 14px;
                line-height: 1.6;
                margin: 0;
                padding: 10px;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #0066cc;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            code {
                background-color: #f5f5f5;
                color: #d63384;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Ubuntu Mono', monospace;
            }
            pre {
                background-color: #f5f5f5;
                color: #333333;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
                border-left: 3px solid #0066cc;
            }
            pre code {
                background-color: transparent;
                padding: 0;
                color: inherit;
            }
            blockquote {
                border-left: 3px solid #0066cc;
                padding-left: 15px;
                margin: 15px 0;
                color: #666666;
                font-style: italic;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            ul, ol {
                margin: 10px 0;
                padding-left: 20px;
            }
            li {
                margin: 5px 0;
            }
            hr {
                border: none;
                border-top: 1px solid #cccccc;
                margin: 20px 0;
            }
            strong {
                color: #0066cc;
                font-weight: bold;
            }
            em {
                color: #666666;
                font-style: italic;
            }
            del {
                color: #999999;
                text-decoration: line-through;
            }
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
            {styles}
            </style>
        </head>
        <body>
        {content}
        </body>
        </html>
        """
    
    def render_markdown(self, text: str, theme: str = "dark") -> str:
        """Convert markdown text to HTML (alias for render_to_html)."""
        return self.render_to_html(text, theme)
    
    def render_to_textedit(self, text_edit: QTextEdit, markdown_text: str, theme: str = "dark") -> None:
        """Render markdown text to a QTextEdit widget."""
        html = self.render_to_html(markdown_text, theme)
        text_edit.setHtml(html)
    
    def extract_plain_text(self, markdown_text: str) -> str:
        """Extract plain text from markdown (removing formatting)."""
        if not markdown_text:
            return ""
        
        text = markdown_text
        
        # Remove code blocks
        text = self.patterns['code_block'].sub('', text)
        
        # Remove inline code
        text = self.patterns['code_inline'].sub(r'\1', text)
        
        # Remove links, keep text
        text = self.patterns['link'].sub(r'\1', text)
        
        # Remove formatting
        text = self.patterns['bold'].sub(r'\1', text)
        text = self.patterns['italic'].sub(r'\1', text)
        text = self.patterns['strikethrough'].sub(r'\1', text)
        
        # Remove headers, keep text
        text = self.patterns['header'].sub(r'\2', text)
        
        # Remove list markers
        text = self.patterns['list_item'].sub(r'\1', text)
        text = self.patterns['numbered_list'].sub(r'\1', text)
        
        # Remove blockquotes
        text = self.patterns['blockquote'].sub(r'\1', text)
        
        # Remove horizontal rules
        text = self.patterns['horizontal_rule'].sub('', text)
        
        return text.strip()
    
    def is_markdown(self, text: str) -> bool:
        """Check if text contains markdown formatting."""
        if not text:
            return False
        
        # Check for common markdown patterns
        markdown_indicators = [
            self.patterns['bold'],
            self.patterns['italic'],
            self.patterns['code_block'],
            self.patterns['code_inline'],
            self.patterns['header'],
            self.patterns['list_item'],
            self.patterns['link'],
            self.patterns['blockquote']
        ]
        
        for pattern in markdown_indicators:
            if pattern.search(text):
                return True
        
        return False
