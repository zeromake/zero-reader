package typing

import "time"

// Toc epub toc
type Toc struct {
	// 目录标题
	Name string
	// 资源页
	Src string
	// 目录深度
	Level uint
	// 锚点
	Anchor string
	// 子目录
	Children []Toc
}

// Rating 评分
type Rating struct {
	// 最大评分
	Min float64 `json:"min"`
	// 最小评分
	Max float64 `json:"max"`
	// 平均评分
	Average float64 `json:"average"`
	// 评分数
	NumRaters uint64 `json:"num_raters"`
}

// Tag 标签
type Tag struct {
	// 标签名
	Name string `json:"name"`
	// 标签设置数量
	Count uint64 `json:"count"`
}

type BaseMeta struct {
	// 书籍标题
	Title string `json:"title"`
	// Author 作者
	Author []string `json:"author"`
	// 书籍文件类型
	FileType string `json:"file_type"`
	// 元信息类型
	MetaType string `json:"meta_type"`
	// 文件 hash 值
	Hash map[string]string `json:"hash"`
	// 文件名
	FileName string `json:"file_name"`
	// 创建方
	Contributor string `json:"contributor"`
	// 发布方
	Publisher string `json:"publisher"`
}

// Meta 书籍元信息
type Meta struct {
	BaseMeta
	// Code isbn id
	Identifier map[string]string `json:"identifier"`
	// 书籍副标题
	SubTitle string `json:"sub_title"`
	// 原始标题
	OriginTitle string `json:"origin_title"`
	// 书籍简介
	Summary string `json:"summary"`
	// 发布时间
	PubDate time.Time `json:"pub_date"`
	// 翻译者
	Translator []string `json:"translator"`
	// 订装方式
	Binding string `json:"binding"`
	// 作者信息
	AuthorIntro string `json:"author_intro"`
	// 书籍评分
	Rating *Rating `json:"rating"`
	// 书籍标签
	Tags []Tag `json:"tags"`
	// 书籍价格
	Price float32 `json:"price"`
	// 书籍页数
	Pages uint64 `json:"pages"`
	Language string
}

type ContentData struct {
	Pages []string
}
