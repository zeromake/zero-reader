import AbcLayout from "./abc-layout";
import { findDOMNode, h, route } from "react-import";
import { buildBlock } from "../utils";
import styl from "@/css/layout.styl";
import throttle from "lodash.throttle";
import TopBar from "./top-bar";
import BottomBar from "./pdf-bottom-bar";
import EpubContent from "./epub-content";

export default class EpubLayout extends AbcLayout<any, any> {
    protected isBlock;
    private htmlDom;
    private htmlPage: number;
    private htmlOffsetPage: number;
    private initPage: boolean;
    private columnCount: number = 1;

    constructor(props, content) {
        super(props, content);
        this.resize = throttle(this.resize.bind(this), 100);
        this.tocClick = this.tocClick.bind(this);
        this.bottomBarClick = this.bottomBarClick.bind(this);
        
        this.htmlOffsetPage = +props.offset || 0;
    }

    public componentDidMount() {
        this.init().then(({ pageHtml, page, callback }) => {
            this.setState({
                pageHtml,
                page,
            }, () => {
                callback && callback();
                this.initPage = true;
                // this.resize(null, true);
                // this.offsetPage();
            });
        });
    }

    private setHtmlDom = (dom) => {
        if (dom) {
            const lastChild = dom.lastElementChild;
            this.htmlPage = lastChild.offsetLeft / (lastChild.offsetWidth + 45);
            if (this.columnCount !== 0) {
                dom.style.columns = `auto ${this.columnCount}`;
            }
        }
        this.htmlDom = dom;
        if (this.initPage) {
            this.initPage = false;
            this.resize(null, true);
            this.offsetPage();
        }
    }

    protected resize(event, flag?:boolean) {
        if (this.page) {
            const clientWidth = this.page.clientWidth;
            const clientHeight = this.page.clientHeight;
            this.isBlock = buildBlock(clientWidth, clientHeight, 1 / 3);
        }
        this.setHtmlPage();
        if (!flag) {
            this.htmlOffsetPage = 0;
            this.offsetPage();
        }
    }

    protected setHtmlPage() {
        if (this.htmlDom) {
            const lastChild = this.htmlDom.lastElementChild;
            const pageNum = lastChild.offsetLeft / ((lastChild.offsetWidth + 45) * this.columnCount);
            if (pageNum % 1) {
                this.htmlPage = ~~(pageNum) + 1;
            } else {
                this.htmlPage = pageNum;
            }
        }
    }

    protected tocClick(toc) {

    }
    protected bottomBarClick(type: number) {
        if (type === 2) {
            if (this.htmlDom) {
                if (this.columnCount === 2) {
                    this.columnCount = 0;
                    // this.htmlDom.style.cssText = "";
                    this.setState({
                        not: false,
                    }, () => {
                        this.setHtmlPage();
                        this.htmlOffsetPage = 0;
                        this.offsetPage();
                    });
                    return
                }
                this.columnCount = this.columnCount === 1 ? 2 : 1;
                this.htmlDom.style.columns = `auto ${this.columnCount}`;
                this.setState({
                    not: true,
                }, () => {
                    this.setHtmlPage();
                    this.htmlOffsetPage = 0;
                    this.offsetPage();
                })
            }
        }
    }

    protected offsetPage() {
        if (this.htmlDom) {
            if (this.htmlOffsetPage >= this.htmlPage) {
                this.htmlOffsetPage = 0;
            }
            const offset = 100 * this.htmlOffsetPage;
            const offsetGap = 45 * this.htmlOffsetPage;
            if (offset === 0 && !('left' in this.htmlDom.style)) {
                return
            }
            this.htmlDom.style.left = `calc(-${offset}% - ${offsetGap}px)`;
            const num = this.state.page;
            const pathname = this.props.history ? this.props.history.location.pathname : location.pathname;
            route(`${pathname}?page=${num}&offset=${this.htmlOffsetPage}`, true);
        }
    }

    protected nextPage(event=null, raw: boolean = false) {
        if (raw || this.htmlOffsetPage >= this.htmlPage - 1 || this.columnCount == 0) {
            const res = super.nextPage();
            if (res) {
                res.then(() => {
                    this.htmlOffsetPage = 0;
                    this.setHtmlPage();
                    this.offsetPage();
                });
            }
            return res;
        }
        this.htmlOffsetPage += 1;
        this.offsetPage();
    }
    protected previousPage(event=null, raw: boolean = false) {
        if (raw || this.htmlOffsetPage <= 0 || this.columnCount == 0) {
            const res = super.previousPage();
            if (res) {
                res.then(() => {
                    this.setHtmlPage();
                    this.htmlOffsetPage = this.htmlPage === 0 ? 0 : this.htmlPage - 1;
                    this.offsetPage();
                })
            }
            return res;
        }
        this.htmlOffsetPage -= 1;
        this.offsetPage();
    }

    protected  renderHeader() {
        const meta = this.props.meta;
        return h(TopBar, {title: meta.title || meta.file_name, onBack: this.onBack});
    }
    protected  renderFooter() {
        return h(BottomBar, {click: this.bottomBarClick});
    }
    protected  renderContent() {
        const state = this.state;
        return h(
            EpubContent,
            {
                pageHtml: state.pageHtml,
                library: this.library,
                pageRef: this.setHtmlDom,
                not: this.state.not,
            },
        );
    }
}
