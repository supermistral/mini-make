import json, hashlib, re, sys
from typing import List, Dict, Union, Any, Optional


class FileManager:
    """Набор инструментов для работы с файлами"""

    CHUNK = 65536

    @staticmethod
    def read(filename: str) -> Optional[str]:
        try:
            f = open(filename, 'r')   
        except OSError as e:
            return None

        content = f.read()
        f.close()

        return content

    @staticmethod
    def read_json(filename: str) -> Any:
        try:
            f = open(filename, 'r', encoding="utf-8")
        except OSError as e:
            return None
        
        try:
            data = json.load(f)
        except ValueError as e:
            return None

        f.close()

        return data

    @staticmethod
    def write(filename: str, content: str, addFlag: bool = False) -> None:
        with open(filename, 'w+' if addFlag else 'w') as f:
            f.write(content)

    @staticmethod
    def write_json(filename: str, content: Any) -> None:
        with open(filename, 'w', encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

    @staticmethod
    def get_hash_file(filename: str) -> Optional[str]:
        fileHash = hashlib.md5()

        try:
            f = open(filename, 'rb')
        except OSError as e:
            return None

        content = f.read(FileManager.CHUNK)
        while (len(content) > 0):
            fileHash.update(content)
            content = f.read(FileManager.CHUNK)

        f.close()

        return fileHash.hexdigest()



class Database:
    """База данных - инструмент для чтения соответствующего файла"""

    fileName = "database"
    fileExtension = "json"
    files = {}

    def __init__(self):
        self.filename = f"{self.fileName}.{self.fileExtension}"
        self.read()

    def __getitem__(self, key: str) -> str:
        return self.files[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.files[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.files
    
    def save(self, data: Any) -> None:
        for k, v in data.items():
            self.files[k] = v

        FileManager.write_json(self.filename, self.files)

    def read(self) -> None:
        data = FileManager.read_json(self.filename)

        if not isinstance(data, dict):
            return

        for k, v in data.items():
            if isinstance(k, str) and isinstance(v, str):
                self.files[k] = v
