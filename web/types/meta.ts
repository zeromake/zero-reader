export enum FileType {
    PDF = "pdf",
    EPUB = "epub",
    MOBI = "mobi",
}
export enum MetaType {
    PDF = "pdf",
    DOUBAN = "douban",
    OPF = "opf",
}
export interface IAbcMeta {
    /**
     * 文件的类型
     */
    type: FileType;
    /**
     * 元数据类型
     */
    meta_type: MetaType;
    /**
     * sha256值
     */
    sha: string;
    /**
     * 书籍名称
     */
    title: string;
    /**
     * 装换前的文件名
     */
    file_name: string;
    /**
     * 内容索引列表的url
     */
    container: string;
    /**
     * 目录url
     */
    toc?: string;
    /**
     * 页面的css
     */
    page_style?: string[];
    /**
     * 封面url
     */
    cover?: string;
}

export interface Identifier {
    /**
     * 豆瓣号
     */
    douban?: string;
    /**
     * 国际书号
     */
    isbn?: string;
}

export interface IOpfMeta extends IAbcMeta {
    /**
     * 评分只有整数部分
     */
    // rating?: number;
    /**
     * 作者国家map
     */
    author_link_map?: string;
    /**
     * 排序标题
     */
    title_sort?: string;
    /**
     * 时间戳
     */
    timestamp?: string;
    /**
     * 语种
     */
    language?: string;
    /**
     * 简介
     */
    description?: string;
    /**
     * 书号
     */
    identifier?: Identifier;
    /**
     * 创建工具
     */
    contributor?: string;
    /**
     * 创建时间
     */
    date?: string;
    /**
     * 版权所有
     */
    rights?: string;
    /**
     * 出版社
     */
    publisher?: string;
    /**
     * 创建者
     */
    creator?: string;
}

/**
 * 豆瓣评分
 */
export interface IDouBanRating {
    /**
     * 最大评分
     */
    max: number;
    /**
     * 评分人数
     */
    numRaters: number;
    /**
     * 平均评分
     */
    average: string;
    /**
     * 最小评分
     */
    min: number;
}
/**
 * 豆瓣的书籍tag
 */
export interface IDouBanTag {
    /**
     * 标记数量
     */
    count: number;
    /**
     * tag名
     */
    name: string;
    /**
     * tag标题
     */
    title: string;
}
/**
 * 豆瓣封面
 */
export interface IDouBanImages {
    /**
     * 小
     */
    small: string;
    /**
     * 大
     */
    large: string;
    /**
     * 中
     */
    medium: string;
}

export interface IDouBanMeta extends IAbcMeta {
    /**
     * 豆瓣书籍页面
     */
    alt: string;
    /**
     * 豆瓣号
     */
    id: number;
    /**
     * isbn10
     */
    isbn10: string;
    /**
     * isbn13
     */
    isbn13: string;
    /**
     * 缺省标题
     */
    alt_title: string;
    /**
     * 评分
     */
    rating?: IDouBanRating;
    /**
     * 副标题
     */
    subtitle?: string;
    /**
     * 作者
     */
    author?: string[];
    /**
     * 出版日期
     */
    pubdate?: string;
    /**
     * 数据标签
     */
    tags?: IDouBanTag[];
    /**
     * 书籍原名
     */
    origin_title?: string;
    /**
     * 封面或介绍图url
     */
    image?: string;
    /**
     * 装订方式
     */
    binding?: string;
    /**
     * 翻译者们
     */
    translator?: string[];
    /**
     * 目录
     */
    catalog?: string;
    /**
     * 书籍页数
     */
    pages?: number;
    /**
     * 各个大小图片url
     */
    images?: IDouBanImages;
    /**
     * 出版社
     */
    publisher?: string;
    /**
     * 作者介绍
     */
    author_intro?: string;
    /**
     * 概要
     */
    summary?: string;
    /**
     * 售价
     */
    price?: string;
}

export interface IPdfMeta extends IDouBanMeta {
    /**
     * page的高宽样式数据url用于缩放
     */
    zoom: string;
    /**
     * 修改时间
     */
    mod_date?: string;
    /**
     * 创建时间
     */
    creation_date?: string;
    /**
     * 创建者
     */
    creator?: string;
    /**
     * 创建工具
     */
    producer?: string;
}

export interface IEpubMeta extends IDouBanMeta, IOpfMeta {
}
