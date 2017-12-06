import { h, Component } from "react-import";
import { get_json, get_text } from "@/http/index";
import { addLinkCss, addStyle, removeHead } from "@/utils";
import styl from "@/css/layout.styl";

interface IabcProps {
    path: string;
    sha?: string;
    url?: string;
    matches?: {
        [key: string]: string;
    };
}

interface Icontainer {
    "data-page-url": string;
    index: number;
    ids?: string[];
    id?: string;
    class?: string;
}

export interface IabcState {
    container?: Icontainer[];
    meta?: IbookMeta;
    pageHtml?: string;
    page?: number;
    // [key: string]: string;
}

/**
 * 元数据
 */
interface IbookMeta {
    /**
     * 目录地址
     */
    toc: string;
    /**
     * 页面css
     */
    page_style: string[];
    /**
     * 内容清单
     */
    container: string;
    /**
     * 元数据类型
     */
    meta_type: string;
    /**
     * 该书籍的hash值(sha256)
     */
    sha: string;
    type: string;
    /**
     * 该书籍的封面
     */
    cover?: string;
    /**
     * pdf的缩放css数据
     */
    zoom?: string;
}

export default abstract class AbcLayout<AbcState extends IabcState> extends Component<IabcProps, AbcState> {
    /**
     * 被挂载的css
     */
    protected mountCss: string[] = [];
    constructor(p: IabcProps, c: any) {
        super(p, c);
        this.state = {
            container: null,
            meta: null,
        } as AbcState;
    }
    protected async init(sha: string) {
        const meta: IbookMeta = await get_json(`/library/${sha}/meta.json`);
        meta.page_style.forEach((cssUrl: string, index: number) => {
            const cssId = `css_id_${index}`;
            this.mountCss.push(cssId);
            addLinkCss(`/library/${sha}/${cssUrl}`, cssId);
        });
        const container: Icontainer[] = await get_json(`/library/${sha}/${meta.container}`);
        const html: string = await this.getPage(container, sha, 0);
        this.setState({
            container,
            meta,
            pageHtml: html,
            page: 0,
        });
    }

    private getPage(container: Icontainer[], sha: string, num: number) {
        const pageName = container[num]["data-page-url"];
        return get_text(`/library/${sha}/${pageName}`);
    }
    public componentWillUnmount() {
        if (this.mountCss.length > 0) {
            let cssId = this.mountCss.pop();
            while (cssId) {
                removeHead(cssId);
                cssId = this.mountCss.pop();
            }
        }
    }
    /**
     * 渲染头部
     */
    protected abstract renderHeader(): JSX.Element | JSX.Element[] | void;
    /**
     * 渲染尾部
     */
    protected abstract renderFooter(): JSX.Element | JSX.Element[] | void;
    /**
     * 渲染内容
     */
    protected abstract renderContent(): JSX.Element | JSX.Element[] | void;
    public render() {
        return <div className={styl.content}>
            { this.renderHeader() }
            { this.renderContent() }
            { this.renderFooter() }
        </div>;
    }
}
