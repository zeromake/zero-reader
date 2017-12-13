import { h, Component, findDOMNode } from "react-import";
import { addLinkCss, addStyle, removeHead } from "@/utils";
import styl from "@/css/layout.styl";
import { IAbcMeta, IAbcToc } from "../types/index";
import lozad from "../assets/lozad";
import Animate from "preact-animate";

interface IabcProps<AbcMeta> {
    path: string;
    sha?: string;
    url?: string;
    meta: AbcMeta;
    library: any;
    page?: string;
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
    barShow: boolean;
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
    protected page: Element;
    protected load: boolean;
    protected abstract isBlock: (x, y) => number;
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
            barShow: false,
        } as AbcState;
    }
    protected async init() {
        this.lozadOptions = {
            ...this.lozadOptions,
            target: this.page || document,
        };
        const meta = this.props.meta;
        meta.page_style.forEach((cssUrl: string, index: number) => {
            const cssId = `css_id_${index}`;
            this.mountCss.push(cssId);
            addLinkCss(this.library.css(cssUrl), cssId);
        });
        this.container = await this.library.json(meta.container);
        this.pageNum = this.container.length;
        const page = Number(this.props.page) || 0;
        const pageHtml = await this.getPage(page);
        return Promise.resolve({
            pageHtml,
            page,
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
        }, () => this.page.scrollTo(0, 0));
    }
    public componentDidUpdate(previousProps: IabcProps<AbcMeta>, previousState: AbcState, previousContext: any) {
        if (this.state.pageHtml) {
            this.bindObserver();
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

    protected nextPage() {
        const page = this.state.page + 1;
        if (page > this.pageNum) {
            return;
        }
        this.setPage(page).then(() => this.load = false);
        // this.page.scrollTo(0, 0);
    }

    protected previousPage() {
        const page = this.state.page - 1;
        if (page < 0) {
            return;
        }
        this.setPage(page).then(() => this.load = false);
        // this.page.scrollTo(0, 0);
    }

    private pageClick = (event: MouseEvent) => {
        if (this.load) {
            return;
        }
        const clickType = this.isBlock(event.clientX, event.clientY);
        let flag = false;
        if (this.state.barShow) {
            this.setState({
                barShow: false,
            });
            flag = true;
        }
        this.load = true;
        if (clickType === 1) {
            this.previousPage();
        } else if (clickType === 2) {
            this.nextPage();
        } else if (clickType === 0) {
            this.load = false;
            if (!flag) {
                const barShow = !this.state.barShow;
                this.setState({
                    barShow,
                });
            }
        }

    }

    public render() {
        return <div  onClick={this.pageClick} ref={((vdom: any) => this.page = findDOMNode(vdom))} className={styl.content}>
            <Animate
                component={null}
                transitionEnter={true}
                transitionLeave={true}
                showProp="data-show"
                transitionName= {{ enter: "fadeInLeft", leave: "fadeOutDown" }}
            >
                { this.renderHeader() }
            </Animate>
            { this.renderContent() }
            <Animate
                component={null}
                transitionEnter={true}
                transitionLeave={true}
                showProp="data-show"
                transitionName= {{ enter: "fadeInUp", leave: "fadeOutDown" }}
            >
                { this.renderFooter() }
            </Animate>
        </div>;
    }
}
