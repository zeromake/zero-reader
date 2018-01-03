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
    private htmlPage: number = 0;
    private htmlContent: any;
    // private initPage: boolean;
    // private columnCount: number = 0;

    constructor(props, content) {
        super(props, content);
        this.resize = throttle(this.resize.bind(this), 100);
        this.tocClick = this.tocClick.bind(this);
        this.bottomBarClick = this.bottomBarClick.bind(this);
    }

    public componentDidMount() {
        this.init().then(({ pageHtml, page, callback }) => {
            // this.initPage = true;
            this.setState({
                pageHtml,
                page,
                columnCount: 0,
                columnOffset: 0,
            }, () => {
                if (callback) {
                    callback();
                }
                this.resize(null, true);
                // this.offsetPage();
            });
        });
    }

    private setHtmlPage = (count: number) => {
        this.htmlPage = count;
    }

    // private setHtmlDom = (dom) => {
    //     this.htmlDom = findDOMNode(dom);
    //     if (dom && this.columnCount !== 0) {
    //         const lastChild = dom.lastElementChild;
    //         this.htmlPage = lastChild.offsetLeft / (lastChild.offsetWidth + 45);
    //         dom.style.columns = `auto ${this.columnCount}`;
    //     }
    //     if (this.initPage) {
    //         this.initPage = false;
    //         this.resize(null, true);
    //         if (this.columnCount !== 0) {
    //             this.offsetPage();
    //         }
    //     }
    // }

    protected resize(event, flag?: boolean) {
        if (this.page) {
            const clientWidth = this.page.clientWidth;
            const clientHeight = this.page.clientHeight;
            this.isBlock = buildBlock(clientWidth, clientHeight, 1 / 3);
            if (this.state.columnCount !== 0 && this.htmlContent && this.htmlContent.setHtmlPage) {
                this.htmlContent.setHtmlPage();
            }
        }
        // if (this.columnCount !== 0) {
        //     this.setHtmlPage();
        //     if (!flag) {
        //         this.htmlOffsetPage = 0;
        //         this.offsetPage();
        //     }
        // }
    }

    // protected setHtmlPage() {
    //     if (this.htmlDom) {
    //         const lastChild = this.htmlDom.lastElementChild;
    //         const pageNum = lastChild.offsetLeft / ((lastChild.offsetWidth + 45) * this.columnCount);
    //         if (pageNum % 1) {
    //             this.htmlPage = ~~(pageNum) + 1;
    //         } else {
    //             this.htmlPage = pageNum;
    //         }
    //     }
    // }

    protected tocClick(toc) {

    }
    protected bottomBarClick(type: number) {
        if (type === 2) {
            this.setState({
                columnCount: this.state.columnCount === 2 ? 0 : this.state.columnCount + 1,
            });
        }
    }

    // protected offsetPage() {
    //     if (this.htmlDom) {
    //         if (this.htmlOffsetPage >= this.htmlPage) {
    //             this.htmlOffsetPage = 0;
    //         }
    //         const offset = 100 * this.htmlOffsetPage;
    //         const offsetGap = 45 * this.htmlOffsetPage;
    //         this.htmlDom.style.left = `calc(-${offset}% - ${offsetGap}px)`;
    //         const num = this.state.page;
    //         const pathname = this.props.history ? this.props.history.location.pathname : location.pathname;
    //         route(`${pathname}?page=${num}&offset=${this.htmlOffsetPage}`, true);
    //     }
    // }

    private refContent = (content) => {
        this.htmlContent = content;
    }

    protected nextPage(event = null, raw: boolean = false) {
        if (raw || this.state.columnCount === 0 || this.state.columnOffset >= this.htmlPage - 1) {
            const res = super.nextPage();
            if (res) {
                res.then(() => {
                    this.setState({columnOffset: 0});
                });
            }
            return res;
        }
        this.setState({columnOffset: this.state.columnOffset + 1});
    }
    protected previousPage(event= null, raw: boolean = false) {
        if (raw || this.state.columnCount === 0 || this.state.columnOffset <= 0) {
            const res = super.previousPage();
            if (res) {
                res.then(() => {
                    this.setState({columnOffset: 0});
                });
            }
            return res;
        }
        this.setState({columnOffset: this.state.columnOffset - 1});
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
                columnCount: this.state.columnCount,
                columnOffset: this.state.columnOffset,
                setHtmlPage: this.setHtmlPage,
                ref: this.refContent,
            },
        );
    }
}
