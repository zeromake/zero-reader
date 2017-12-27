import { h, Component, findDOMNode, route } from "react-import";
import { addLinkCss, addStyle, removeHead, filterPropsComponent } from "@/utils";
import styl from "@/css/layout.styl";
import { IAbcMeta, IAbcToc } from "../types/index";
import Animate from "preact-animate";
import Toc from "./toc";
import hotkeys from "hotkeys-js";

interface IabcProps<AbcMeta> {
    path: string;
    sha?: string;
    url?: string;
    meta: AbcMeta;
    library: any;
    page?: string;
    history?: any;
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
    tocShow: boolean;
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
    protected tocs: IAbcToc[];
    protected isClickPropagation: boolean;
    protected clickState: {[name: string]: any};
    protected abstract isBlock: (x, y) => number;
    protected bscroll: any;
    protected selection: boolean;
    protected hotkey: {[keyName: string]: (event?) => void};
    // protected baseUrl: string;
    constructor(p: IabcProps<AbcMeta>, c: any) {
        super(p, c);
        // this.baseUrl = `/library/${p.meta.sha}/`;
        this.library = p.library;
        this.clickState = {};
        this.previousPage = this.previousPage.bind(this);
        this.nextPage = this.nextPage.bind(this);
        this.hotkey = {
            "left, h": this.previousPage,
            "right, l": this.nextPage,
            "shift + g": (event) => {
                if (event.key === "G") {
                    this.setPage(this.pageNum - 1);
                }
            },
            "g": (event) => {
                if (event.key === "G") {
                    this.setPage(this.pageNum - 1);
                } else {
                    this.setPage(0);
                }
            },
            "m": () => {
                this.barToggler(!this.state.barShow);
            },
            "space": (event) => {
                if (this.tocs) {
                    this.tocToggler(!this.state.tocShow);
                } else {
                    this.getToc().then((tocs) => {
                        this.tocs = tocs;
                        this.tocToggler(true);
                    });
                }
            },
        };
        this.state = {
            bg: "blue",
            barShow: false,
            tocShow: false,
        } as AbcState;
    }
    protected async init() {
        this.page = findDOMNode(this);
        for (const key in this.hotkey) {
            if (key) {
                const callback = this.hotkey[key];
                if (callback) {
                    hotkeys(key, (event) => {
                        event.preventDefault();
                        callback(event);
                    });
                }
            }
        }
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
    protected setPage(num: number, obj: any = {}) {
        if (this.load) {
            return;
        }
        this.load = true;
        return this.getPage(num).then((text) => {
            return new Promise<void>((resolve, reject) => {
                this.setState({
                    pageHtml: text,
                    page: num,
                    ...obj,
                }, () => {
                    try {
                        if (this.page && "scrollTop" in this.page) {
                            // this.bscroll.scrollTo(0, 0, 375);
                            this.page.scrollTop = 0;
                            // this.page.scroll(0, 0);
                        } else {
                            console.log("page no has scroll: ");
                        }
                        resolve();
                    } finally {
                        if (this.props.history) {
                            route(`${this.props.history.location.pathname}?page=${num}`, true);
                        }
                        this.load = false;
                    }
                });
            });
        });
    }
    private getPage(num: number) {
        const pageName = this.container[num]["data-page-url"];
        return this.library.text(pageName);
    }
    protected getToc() {
        return this.library.json(this.props.meta.toc);
    }
    public componentWillUnmount() {
        const keys = [];
        for (const key in this.hotkey) {
            if (key) {
                keys.push(key);
            }
        }
        if (keys.length > 0) {
            hotkeys.unbind(keys.join(", "));
        }
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
    protected abstract renderHeader(): JSX.Element | string | Array<JSX.Element|string>;
    /**
     * 渲染尾部
     */
    protected abstract renderFooter(): JSX.Element | string | Array<JSX.Element|string>;
    /**
     * 渲染内容
     */
    protected abstract renderContent(): JSX.Element | string | Array<JSX.Element|string>;

    protected nextPage() {
        const page = this.state.page + 1;
        if (page >= this.pageNum) {
            this.load = false;
            return;
        }
        return this.setPage(page);
    }

    protected previousPage() {
        const page = this.state.page - 1;
        if (page < 0) {
            this.load = false;
            return;
        }
        return this.setPage(page);
    }

    private pageClick = (event: MouseEvent) => {
        const selectionObj =  document.getSelection();
        const selection = selectionObj.toString();
        if (!this.selection) {
            if (selection && selection !== "") {
                this.selection = true;
                return;
            }
        } else {
            this.selection = false;
            if (selection && selection !== "") {
                selectionObj.removeAllRanges();
            }
            return;
        }
        if (this.load) {
            return;
        }
        if (this.isClickPropagation) {
            let flag = false;
            for (const name in this.clickState) {
                flag = true;
                break;
            }
            this.isClickPropagation = false;
            if (flag) {
                this.setState(this.clickState as any, () => {
                    this.clickState = {};
                });
                return;
            }
        }
        const clickType = this.isBlock(event.clientX, event.clientY);
        if (clickType === 1) {
            this.previousPage();
        } else if (clickType === 2) {
            this.nextPage();
        } else if (clickType === 0) {
            this.isClickPropagation = true;
            this.barToggler(true);
            // this.clickState.barShow = false;
            // this.setState({
            //     barShow: true,
            // });
        }

    }

    protected tocToggler = (show: boolean) => {
        if (show) {
            this.clickState.tocShow = false;
        } else {
            delete this.clickState.tocShow;
        }
        this.setState({
            tocShow: show,
        });
    }

    protected barToggler = (show: boolean) => {
        if (show) {
            this.clickState.barShow = false;
        } else {
            delete this.clickState.barShow;
        }
        this.setState({
            barShow: show,
        });
    }

    protected abstract tocClick(toc: IAbcToc): void;

    protected renderToc() {
        return <div
                className={`${styl.toc_layout} animated`}
                onClick={(event) => event.stopPropagation()}>
                <div className={styl.toc_title}>
                    <p>{["目录"]}</p>
                    <svg viewBox="0 0 24 24" className={styl.toc_close} onClick={() => this.tocToggler(false)}>
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"></path>
                        <path d="M0 0h24v24H0z" fill="none"></path>
                    </svg>
                </div>
                <div className={styl.toc_content}>
                    {this.tocs ? <Toc tocs={this.tocs} onclick={this.tocClick}/> : null}
                </div>
            </div>;
    }

    public render() {
        // <div onClick={this.pageClick} ref={((vdom: any) => this.page = findDOMNode(vdom))} className={styl.content}>

        return <Animate
                component="div"
                componentProps={{
                    onClick: this.pageClick,
                    // ref: ((vdom: any) => this.page = findDOMNode(vdom)),
                    className: styl.content,
                }}
                transitionEnter={true}
                transitionLeave={true}
                showProp="data-show"
            >
                {[
                    h(filterPropsComponent, {
                    "key": "header",
                    "transitionName": { enter: "fadeInDown", leave: "fadeOutUp" },
                    "data-show": this.state.barShow,
                    }, this.renderHeader()),
                    h(filterPropsComponent, {
                        "key": "toc",
                        "data-show": this.state.tocShow,
                        "transitionName": { enter: "fadeInLeft", leave: "fadeOutLeft" },
                        },
                        this.renderToc(),
                    ),
                    h(filterPropsComponent, { "key": "content", "data-show": true}, this.renderContent()),
                    h(filterPropsComponent, {
                        "key": "footer",
                        "transitionName": { enter: "fadeInUp", leave: "fadeOutDown" },
                        "data-show": this.state.barShow,
                    }, this.renderFooter()),
                ]}
            {/* </div>; */}
        </Animate>;
    }
}
