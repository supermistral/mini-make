# Mini-make emulator
The task is rebuilt according to changes in the contents of the file or in the absence of the corresponding file. The shell code runs through `os.system(code)`.

### Database operation
The database is a replacement for file tracking in common make. The database stores information about file changes - hash of the content (md5). The format is json.
Each launch of a makefile overwrites the file information. 

### Makefile is described by syntax:
```
target : [dependecies] 
{
    [commands]
}
```

### Run script
`python main.py <makefile> [target]`