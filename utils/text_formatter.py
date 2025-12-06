import re

class TextFormatter:
    
    def __init__(self):
        self.vietnamese_upper_map = {
            'à': 'À', 'á': 'Á', 'ả': 'Ả', 'ã': 'Ã', 'ạ': 'Ạ',
            'ầ': 'Ầ', 'ấ': 'Ấ', 'ẩ': 'Ẩ', 'ẫ': 'Ẫ', 'ậ': 'Ậ',
            'ằ': 'Ằ', 'ắ': 'Ắ', 'ẳ': 'Ẳ', 'ẵ': 'Ẵ', 'ặ': 'Ặ',
            'è': 'È', 'é': 'É', 'ẻ': 'Ẻ', 'ẽ': 'Ẽ', 'ẹ': 'Ẹ',
            'ề': 'Ề', 'ế': 'Ế', 'ể': 'Ể', 'ễ': 'Ễ', 'ệ': 'Ệ',
            'ì': 'Ì', 'í': 'Í', 'ỉ': 'Ỉ', 'ĩ': 'Ĩ', 'ị': 'Ị',
            'ò': 'Ò', 'ó': 'Ó', 'ỏ': 'Ỏ', 'õ': 'Õ', 'ọ': 'Ọ',
            'ồ': 'Ồ', 'ố': 'Ố', 'ổ': 'Ổ', 'ỗ': 'Ỗ', 'ộ': 'Ộ',
            'ờ': 'Ờ', 'ớ': 'Ớ', 'ở': 'Ở', 'ỡ': 'Ỡ', 'ợ': 'Ợ',
            'ù': 'Ù', 'ú': 'Ú', 'ủ': 'Ủ', 'ũ': 'Ũ', 'ụ': 'Ụ',
            'ừ': 'Ừ', 'ứ': 'Ứ', 'ử': 'Ử', 'ữ': 'Ữ', 'ự': 'Ự',
            'ỳ': 'Ỳ', 'ý': 'Ý', 'ỷ': 'Ỷ', 'ỹ': 'Ỹ', 'ỵ': 'Ỵ',
            'đ': 'Đ', 'ă': 'Ă', 'â': 'Â', 'ê': 'Ê', 'ô': 'Ô', 'ơ': 'Ơ', 'ư': 'Ư'
        }
        
        self.company_special_words = ['tnhh', 'mtv', 'cn', 'kcn', 'nsg']
        
        self.address_special_words = ['cn', 'kcn', 'ttcn']
    
    def _fix_vietnamese_diacritics(self, text: str) -> str:
        replacements = [
            (r'òa', 'oà'), (r'ÒA', 'OÀ'), (r'Òa', 'Oà'),
            (r'óa', 'oá'), (r'ÓA', 'OÁ'), (r'Óa', 'Oá'),
            (r'ỏa', 'oả'), (r'ỎA', 'OẢ'), (r'Ỏa', 'Oả'),
            (r'õa', 'oã'), (r'ÕA', 'OÃ'), (r'Õa', 'Oã'),
            (r'ọa', 'oạ'), (r'ỌA', 'OẠ'), (r'Ọa', 'Oạ'),
        ]
        for old, new in replacements:
            text = re.sub(old, new, text)
        return text
    
    def _capitalize_first_letter(self, word: str) -> str:
        first_alpha_idx = -1
        for i, char in enumerate(word):
            if char.isalpha():
                first_alpha_idx = i
                break
        
        if first_alpha_idx >= 0:
            char = word[first_alpha_idx]
            upper_char = self.vietnamese_upper_map.get(char, char.upper())
            return word[:first_alpha_idx] + upper_char + word[first_alpha_idx+1:]
        else:
            return word
    
    def format_text(self, text: str, is_company_name: bool = False) -> str:
        if not text:
            return text
        
        text = self._fix_vietnamese_diacritics(text)
        
        text = text.lower()
        
        words = re.findall(r'\S+', text)
        formatted_words = []
        
        if is_company_name:
            special_words_upper = self.company_special_words
        else:
            special_words_upper = self.address_special_words
        
        for word in words:
            word_lower = word.lower()
            
            if word_lower in special_words_upper:
                formatted_words.append(word_lower.upper())
            else:
                formatted_word = self._capitalize_first_letter(word)
                formatted_words.append(formatted_word)
        
        result = ' '.join(formatted_words)
        
        return result
