# api doc

model 自动化转 restful

## get 参数说明

``` text
/api/admin/user?where={}&keys=field1,field2&skip=0&limit=10&order=field1,field2
```

### where示例

select 参数在 `query_string` 中的 `where` 字段，为json字符串,具体可见 [whereData](#model-whereData)

---
**==**

值为基本数据类型 为sql的普通匹配

``` text
/api/admin/user?where={"id": 1}
```

-> sql

``` sql
select * from user where id=1
```

---
**!=**

``` text
/api/admin/user?where={"id": {"opt": "$ne","val": 1}}
```

-> sql

``` sql
select * from user where id != 1
```

---
**in**

值为数组默认为 `in`

``` text
/api/admin/user?where={"id": [1,2]}
```

-> sql

``` sql
select * from user where id in (1,2)
```

---
**opt说明**

<table>
    <thead>
        <tr>
        <th>关键字</th>
        <th>说明</th>
        <th>值类型</th>
        <th>值说明</th>
        </tr>
    </thead>
    <tbody>
    <tr>
        <td><span>$</span>ne</td>
        <td>不等于</td>
        <td>any</td>
        <td>不为字典和列表的任意值</td>
    </tr>
    <tr>
        <td><span>$</span>te</td>
        <td>等于</td>
        <td>any</td>
        <td>同上</td>
    </tr>
    <tr>
        <td><span>$</span>lt</td>
        <td>小于</td>
        <td>number|date</td>
        <td>sql支持大小比较的值</td>
    </tr>
    <tr>
        <td><span>$</span>lte</td>
        <td>小于等于</td>
        <td>number|date</td>
        <td>同上</td>
    </tr>
    <tr>
        <td><span>$</span>gt</td>
        <td>大于</td>
        <td>number|date</td>
        <td>同上</td>
    </tr>
    <tr>
        <td><span>$</span>gte</td>
        <td>大于等于</td>
        <td>number|date</td>
        <td>同上</td>
    </tr>
    <tr>
        <td><span>$</span>like</td>
        <td>sql like</td>
        <td>string</td>
        <td>like 用字符串</td>
    </tr>
    <tr>
        <td><span>$</span>in</td>
        <td>sql in</td>
        <td>[]any</td>
        <td>任意值数组</td>
    </tr>
    <tr>
        <td><span>$</span>nin</td>
        <td>sql not in</td>
        <td>[]any</td>
        <td>任意值数组</td>
    </tr>
    <tr>
        <td><span>$</span>bind</td>
        <td>sql占位</td>
        <td>{"val": string, "opt": string}</td>
        <td>val为绑定的key, opt为任意比较(sqlalchemy不支持in/nin占位)</td>
    </tr>
    </tbody>
</table>


## post 参数说明

## delete 参数说明

## put/patch 参数说明
