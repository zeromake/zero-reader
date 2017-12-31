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

    constructor(props, content) {
        super(props, content);
        this.resize = throttle(this.resize.bind(this), 100);
        this.tocClick = this.tocClick.bind(this);
        this.bottomBarClick = this.bottomBarClick.bind(this);
        this.htmlOffsetPage = 0;
    }

    public componentDidMount() {
        this.init().then(({ pageHtml, page, callback }) => {
            this.setState({
                pageHtml,
                page,
            }, () => {
                callback && callback();
                this.resize();
            });
        });
    }

    private setHtmlDom = (dom) => {
        if (dom) {
            const lastChild = dom.lastElementChild;
            this.htmlPage = lastChild.offsetLeft / (lastChild.offsetWidth + 45);
        }
        this.htmlDom = dom;
    }

    protected resize() {
        if (this.page) {
            const clientWidth = this.page.clientWidth;
            const clientHeight = this.page.clientHeight;
            this.isBlock = buildBlock(clientWidth, clientHeight, 1 / 3);
        }
        this.setHtmlPage();
    }

    protected setHtmlPage() {
        if (this.htmlDom) {
            const lastChild = this.htmlDom.lastElementChild;
            this.htmlPage = lastChild.offsetLeft / (lastChild.offsetWidth + 45);
        }
    }

    protected tocClick(toc) {

    }
    protected bottomBarClick(type: number) {

    }

    protected offsetPage() {
        if (this.htmlDom) {
            const offset = 100 * this.htmlOffsetPage;
            const offsetGap = 45 * this.htmlOffsetPage; 
            this.htmlDom.style.left = `calc(-${offset}% - ${offsetGap}px)`;
            const num = this.state.page;
            const pathname = this.props.history ? this.props.history.location.pathname : location.pathname;
            route(`${pathname}?page=${num}&offset=${this.htmlOffsetPage}`, true);
        }
    }

    protected nextPage(raw: boolean = false) {
        if (raw || this.htmlOffsetPage >= this.htmlPage) {
            this.htmlOffsetPage = 0;
            return super.nextPage();
        }
        this.htmlOffsetPage += 1;
        this.offsetPage();
    }
    protected previousPage(raw: boolean = false) {
        if (raw || this.htmlOffsetPage <= 0) {
            const res = super.previousPage();
            if (res) {
                res.then(() => {
                    this.htmlOffsetPage = this.htmlPage;
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
            },
        );
    }
}
