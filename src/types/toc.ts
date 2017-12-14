export interface IAbcToc {
    /**
     * 深度
     */
    level: number;
    /**
     * 标题
     */
    text: string;
    /**
     * page在containe中的下标
     */
    index: number;
    /**
     * page的序号
     */
    page: number;
    /**
     * page的相对url
     */
    page_url: string;
    /**
     * 子目录
     */
    children?: IAbcToc[];
    /**
     * 显示子目录
     */
    disable?: boolean;
}

/**
 * epub toc
 */
export interface IEpubToc extends IAbcToc {
    /**
     * 原始数据id
     */
    id: string;
    /**
     * toc顺序
     */
    play_order: string;
    /**
     * 锚点
     */
    hash?: string;
    /**
     * query字符串
     */
    query?: string;
}

export interface IPdfToc extends IAbcToc {
    /**
     * 与container对应的id
     */
    href: string;
    /**
     * 原始类名
     */
    class: string;
    /**
     * pdf2htmlEx的目录锚点座标
     */
    "data-dest-detail": [number, string, number, number, null];
}
