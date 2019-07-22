# epub package design

## zip package design

**创建 zip 读取对象**

```
NewReader(name string) (*Reader, error)
```

**zip 路径 join 方法**

```
func Join(elem ...string) string
```


**打开 zip 中的文件**

```
func (r *Reader) Open(name) (io.ReadCloser, error)
```

**关闭 zip 读取对象**

```
func (r *Reader) Close() error
```

**保存 zip 中的文件到目标路径**
```
func (r *Reader) Save(source string, target string) (int, error)
```

**保存 zip 中的文件到目标流**
```
func (r *Reader) SaveFile(source string, target io.Writer) (int, error)
```




