import { h, Component } from "zreact";
import { addLinkCss, addStyle, removeHead } from "@/utils";
import styl from "@/css/layout.styl";
import { IAbcMeta, IAbcToc } from "../types/index";
import lozad from "../assets/lozad";

interface IabcProps<AbcMeta> {
    path: string;
    sha?: string;
    url?: string;
    meta: AbcMeta;
    library: any;
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
    pageHtml?: string;
    page?: number;
    bg: string;
    // [key: string]: string;
}

export default abstract class AbcLayout<AbcState extends IabcState, AbcMeta extends IAbcMeta> extends Component<IabcProps<AbcMeta>, AbcState> {
    /**
     * 被挂载的css
     */
    protected mountCss: string[] = [];
    protected pageNum: number;
    protected library: any;
    protected observer: any;
    protected lozadOptions: {};
    protected container: Icontainer[];
    // protected baseUrl: string;
    constructor(p: IabcProps<AbcMeta>, c: any) {
        super(p, c);
        // this.baseUrl = `/library/${p.meta.sha}/`;
        this.library = p.library;
        this.lozadOptions = {
            load: (element) => {
                if (element.getAttribute("data-src")) {
                    element.src = this.library.image(element.getAttribute("data-src"));
                }
            },
        };
        this.state = {
            bg: "blue",
        } as AbcState;
    }
    protected async init() {
        const meta = this.props.meta;
        meta.page_style.forEach((cssUrl: string, index: number) => {
            const cssId = `css_id_${index}`;
            this.mountCss.push(cssId);
            addLinkCss(this.library.css(cssUrl), cssId);
        });
        this.container = await this.library.json(meta.container);
        this.pageNum = this.container.length;
        const pageHtml = await this.getPage(0);
        return Promise.resolve({
            pageHtml,
            page: 0,
        });
        // await this.setPage(0);
    }
    protected bindObserver() {
        if (!this.observer) {
            this.observer = lozad(".lozad", this.lozadOptions);
            this.observer.observe();
        } else {
            this.observer.unobserve();
            this.observer.update();
        }
    }
    protected setPage(num: number) {
        return this.getPage(num).then((text) => {
            this.setState({
                pageHtml: text,
                page: num,
            });
        });
    }
    public componentDidUpdate(previousProps: IabcProps<AbcMeta>, previousState: AbcState, previousContext: any) {
        if (this.state.pageHtml) {
            setTimeout(() => this.bindObserver(), 1000);
        }
    }
    private getPage(num: number) {
        const pageName = this.container[num]["data-page-url"];
        return this.library.text(pageName);
    }
    protected getToc(tocName: string) {
        return this.library.json(tocName);
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
