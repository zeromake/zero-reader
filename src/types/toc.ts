export interface IAbcToc<T> {
    /**
     * 深度
     */
    level: number;
    /**
     * 标题
     */
    text: string;
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
    children?: T[];
}

/**
 * epub toc
 */
export interface IEpubToc extends IAbcToc<IEpubToc> {
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

export interface IPdfToc extends IAbcToc<IPdfToc> {
    /**
     * 与container对应的id
     */
    href: string;
    /**
     * 原始类名
     */
    class: string;
    /**
     * page在containe中的下标
     */
    index: number;
    /**
     * pdf2htmlEx的目录锚点座标
     */
    "data-dest-detail": [number, string, number, number, null];
}
