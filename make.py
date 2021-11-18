from collections import defaultdict
from typing import List, Dict, Union
from utils import Database, Parser, FileManager
from exceptions import TargetNotFoundError, MakefileNotFoundError
import os, sys


class MakeItem:
    """Класс, представляющий мейк цель"""

    def __init__(self, name: str, code: List[str]):
        self.name = name
        self.code = code

    def execute(self) -> None:
        for codeUnit in self.code:
            os.system(codeUnit)



class Graph:
    """Граф с вершинами MakeItem"""

    def __init__(self):
        self.graph = defaultdict(list)
        self.indexTable = {}
        self.size = 0

    def _add_to_indexTable(self, edge: MakeItem) -> None:
        if edge not in self.indexTable:
            self.indexTable[edge] = self.size
        self.size += 1

    def add(self, u: MakeItem, v: MakeItem) -> None:
        self.graph[u].append(v)
        self._add_to_indexTable(u)
        self._add_to_indexTable(v)

    def _topological_sort(self, u: MakeItem, visited: List[int], 
                                  stack: List[MakeItem]) -> None:
        index = self.indexTable[u]
        if visited[index]:
            return
    
        visited[index] = True

        if u in self.graph:
            for edge in self.graph[u]:
                if not visited[self.indexTable[edge]]:
                    self._topological_sort(edge, visited, stack)

        stack.insert(0, u)

    def topological_sort(self) -> List[MakeItem]:
        visited = [False] * self.size
        stack = []

        for edge in self.graph:
            self._topological_sort(edge, visited, stack)

        return stack



class Make:
    """Предоставляет средства обработки мейк файла"""

    def __init__(self):
        self.graph = Graph()
        self.database = Database()
        self.parser = Parser()
        self.makeItems = {}


    def _is_target_changed(self, target: str) -> bool:
        return target not in self.database or \
            self.makeItems[target]['hash'] != self.database[target]


    def _fill_makeItems(self, data: List[Dict[str, Union[str, List[str]]]]) -> None:
        """Заполнение словаря makeItems"""

        for item in data:
            target = item['target']
            code = item['code']
            deps = item['deps']

            self._add_to_makeItems(target, code=code, deps=deps)

        # Множество зависимостей - поиск мейк-объектов, которых еще нет в self.makeItems
        missingDeps = set()

        for item in self.makeItems:
            for dep in self.makeItems[item]['deps']:
                if dep not in self.makeItems:
                    missingDeps.add(dep)

        for dep in missingDeps:
            # Добавить узлы, которые не отмечены как цели, в строгом режиме
            #   вызывать исключение на узлах, которые не являются файлами
            self._add_to_makeItems(dep, strict_mode=True)
 

    def _add_to_makeItems(self, target: str, **kwargs) -> None:
        if target not in self.makeItems:
            self.makeItems[target] = self._create_makeItem(target, **kwargs)
        else:
            self.makeItems[target] = self._create_makeItem(
                target, hash=self.makeItems[target]['hash'], **kwargs
            )
    

    def _create_makeItem(self, target: str, **kwargs) -> Dict[str, Union[MakeItem, List[str], str, None]]:
        deps        = kwargs.get('deps', [])
        code        = kwargs.get('code', [])
        targetHash  = kwargs.get('hash', None)
        strictMode  = kwargs.get('strict_mode', False)

        if targetHash is None:
            targetHash = FileManager.get_hash_file(target)
            if targetHash is None and strictMode:
                raise TargetNotFoundError(target)
        
        return {
            'item': MakeItem(target, code),
            'deps': deps,
            'hash': targetHash
        }


    def _fill_graph(self, target: str) -> None:
        """Рекурсивное заполнение графа целей"""

        item = self.makeItems[target]
        for dep in item['deps']:
            depItem = self.makeItems[dep]
            self.graph.add(item['item'], depItem['item'])
            self._fill_graph(dep)

    
    def _check_execute(self, target: str) -> bool:
        """Проверка на необходимость выполнения цели"""

        deps = self.makeItems[target]['deps']

        # Нет зависимостей - проверка самого узла на изменение
        if not deps:
            return self._is_target_changed(target)

        # Зависимости есть - проверка на изменение хотя бы одной из них
        mappingFlags = map(lambda item: self._is_target_changed(item), deps)
        return any(mappingFlags)


    def make(self) -> None:
        """Запуск сборки согласно параметрам командной строки sys.argv"""

        if (len(sys.argv) < 2):
            raise TypeError("File not specified")

        data = self.read_makefile(sys.argv[1])
        if data is None:
            raise MakefileNotFoundError()
        
        # Цель - через командную строку или первая в списке
        mainTarget = sys.argv[2] if len(sys.argv) > 2 else data[0]['target']
        
        self._fill_makeItems(data)
        self._fill_graph(mainTarget)

        makeItemsStack = self.graph.topological_sort()

        for makeItem in makeItemsStack:
            if self._check_execute(makeItem.name):
                makeItem.execute()

        self._save_database()
   

    def _save_database(self) -> None:
        """Запись в БД"""

        dataToSave = {item: self.makeItems[item]['hash'] for item in self.makeItems \
            if self.makeItems[item]['hash'] is not None}
        self.database.save(dataToSave)


    def read_makefile(self, filename: str) -> List[Dict[str, Union[str, List[str]]]]:
        """Получение ответа от парсера make-файла"""

        makefileContent = FileManager.read(filename)
        return self.parser.parse(makefileContent)



if __name__ == "__main__":
    make = Make()
    make.make()
    # print(make.makeItems)
    # print()
    # print(make.graph.graph)