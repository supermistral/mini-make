from typing import List, Dict, Union
from utils import FileManager
import sys


class Parser:
    """Парсер make-файла"""

    pattern = r"((\w+)\s*:\s*([\w| |\t]*)\s*{([\S\s]*?)})"
    token_pattern = r"\w+"


    def __init__(self):
        self.regexp = re.compile(self.pattern)
        self.tokenRegexp = re.compile(self.token_pattern)


    def _split_tokens(self, string: str) -> List[str]:
        return self.tokenRegexp.findall(string)


    def _split_lines(self, string: str) -> List[str]:
        return [s.strip() for s in string.split("\n") if s]

    
    def _get_type_tokens(self, match: List[str]) -> Dict[str, Union[str, List[str]]]:
        """Получение словаря для исполнения кода"""

        return {
            "target": match[1],
            "deps": self._split_tokens(match[2]),
            "code": self._split_lines(match[3])
        }
    

    def parse(self, code: str) -> List[Dict[str, Union[str, List[str]]]]:
        """Парсинг кода make"""

        matches = self.regexp.findall(code)
        formatted_tokens = []

        for match in matches:
            formatted_tokens.append(self._get_type_tokens(match))

        return formatted_tokens



if __name__ == "__main__":
    print(Parser().parse(FileManager.read(sys.argv[1])))