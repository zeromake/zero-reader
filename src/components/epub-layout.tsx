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
    private htmlContent: EpubContent| undefined;
    private offsetWidth: number;

    constructor(props, content) {
        super(props, content);
        this.resize = throttle(this.resize.bind(this), 100);
        this.tocClick = this.tocClick.bind(this);
        this.bottomBarClick = this.bottomBarClick.bind(this);
    }

    public componentDidMount() {
        this.init().then(({ pageHtml, page, callback }) => {
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
                const propsLocation = (this.props.history && this.props.history.location) || location;
                if (propsLocation) {
                    const hash = propsLocation.hash;
                    this.scrollHash(hash);
                }
            });
        });
    }

    private setHtmlPage = (count: number) => {
        this.htmlPage = count;
    }

    private scrollHash(hash) {
        if (hash && this.htmlContent) {
            const offset = this.htmlContent.scrollHash(hash);
            if (this.state.columnCount !== 0) {
                this.setState({
                    columnOffset: offset || 0,
                });
            }
        }
    }

    protected resize(event, flag?: boolean) {
        if (this.page) {
            const clientWidth = this.page.clientWidth;
            const clientHeight = this.page.clientHeight;
            this.isBlock = buildBlock(clientWidth, clientHeight, 1 / 3);
            if (this.state.columnCount !== 0 && this.htmlContent && this.htmlContent.setHtmlPage) {
                if (this.state.columnOffset !== 0) {
                    this.setState({columnOffset: 0}, () => this.htmlContent.setHtmlPage());
                } else {
                    this.htmlContent.setHtmlPage();
                }
            }
        }
    }

    protected tocClick(toc) {
        this.setPage(toc.index).then(() => {
            let href = `?page=${toc.index}`;
            const pathname = this.props.history ? this.props.history.location.pathname : location.pathname;
            if (toc.hash) {
                href += "#" + toc.hash;
                this.scrollHash("#" + toc.hash);
            }
            route(`${pathname}${href}`, true);
            this.tocToggler(false);
        });
    }

    protected bottomBarClick(type: number) {
        if (type === 1) {
            if (this.tocs) {
                this.barToggler(false);
                this.tocToggler(true);
            } else {
                this.getToc().then((tocs) => {
                    this.tocs = tocs;
                    this.barToggler(false);
                    this.tocToggler(true);
                });
            }
        } else if (type === 2) {
            const columnCount = this.state.columnCount;
            const state: {[name: string]: any} = {};
            if (columnCount === 2 || columnCount === 0) {
                state.isScroll = !this.state.isScroll;
            }
            state.columnCount = columnCount === 2 ? 0 : this.state.columnCount + 1;
            state.columnOffset = 0;
            this.setState(state);
        }
    }

    protected clickPageUrl(event: MouseEvent) {
        const target = event.target as HTMLLinkElement;
        const href = target.getAttribute("href");
        const dataHref = target.getAttribute("data-href");
        if (href) {
            if (dataHref) {
                event.preventDefault();
                const pageData = JSON.parse(dataHref);
                this.setPage(pageData.page).then(() => {
                    const pathname = this.props.history ? this.props.history.location.pathname : location.pathname;
                    route(`${pathname}${href}`, true);
                    this.scrollHash("#" + pageData.hash);
                });
            } else {
                console.log("out link", href);
            }
        } else {
            event.preventDefault();
            event.stopPropagation();
        }
    }

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
                    this.setState({columnOffset: this.htmlPage === 0 ? 0 : this.htmlPage - 1});
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
