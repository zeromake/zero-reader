import { h, findDOMNode } from "react-import";
import AbcLayout, { IabcState } from "./abc-layout";
import styl from "@/css/layout.styl";
import BookToolsBar from "@/components/book-tools-bar";
import BottomBar from "@/components/bottom-bar";
import { addStyle } from "@/utils";
import Toc from "@/components/toc";
import Animate from "preact-animate";
import throttle from "lodash.throttle";
import { IPdfMeta } from "../types/index";

interface IZoom {
    select: string;
    attribute: string;
    size: number;
    unit: string;
    media_print: boolean;
}

interface IBookState extends IabcState {
    offset: number;
    theme?: string;
    toc_open: boolean;
    zoom: number;
}

export default class PdfLayout extends AbcLayout<IBookState, IPdfMeta> {
    private page: any;
    private zoom?: IZoom[];
    private width?: number;
    private height?: number;
    public tocs: any[];
    private load: boolean;

    constructor(props, content) {
        super(props, content);
        this.state.offset = 20;
        this.load = false;
    }

    public resize = throttle(() => {
        this.setZoom();
    });

    public scroll = throttle((event) => {
        let res: Promise<void>;
        let pageNum: number;
        if (!this.load) {
            this.load = true;
            if (event.detail > 0) {
                pageNum = this.state.page + 1;
            } else if (event.detail < 0) {
                pageNum = this.state.page - 1;
            }
            if (pageNum >= this.pageNum || pageNum < 0) {
                res = Promise.resolve();
            } else {
                res = this.setPage(pageNum);
            }
            res.then(() => {
                this.load = false;
            });
        }
    }, 20);
    public componentDidMount() {
        this.lozadOptions = {
            ...this.lozadOptions,
            target: this.page || document,
        };
        this.init().then(({ pageHtml, page }) => {
            if (this.props.meta.zoom) {
                this.getZoom(this.props.meta.zoom).then((zoom: number) => {
                    this.setState({
                        pageHtml,
                        page,
                    });
                });
                window.addEventListener("resize", this.resize as any);
            }
        });
    }

    protected  renderHeader() {
        const state = this.state;
        // const tocClass = styl.toc_layout + (state.theme ? " " + styl[state.theme] : "");
        return <BookToolsBar options={ { showToc: () => {this.setState({ toc_open: !state.toc_open }); } } }/>;
    }
    protected  renderFooter() {
        return <BottomBar/>;
    }
    protected  renderContent() {
        const state = this.state;
        console.log("render ", state);
        return <div ref={((vdom: any) => this.page = findDOMNode(vdom))}><div
                className={`${styl.pageHtml} w0 ${styl.view} ${styl[state.bg]}`}
                dangerouslySetInnerHTML={{__html: state.pageHtml}}
            >
            </div></div>;
    }
    private getZoom(zoom: string) {
        return this.library.json(zoom).then((data) => {
            this.zoom = data.css;
            this.width = data.width;
            this.height = data.height;
            return this.setZoom(true);
        });
    }
    private setZoom(flag?) {
        if (this.page) {
            const clientWidth = this.page.clientWidth;
            let offset = this.state.offset;
            if (flag) {
                offset += 15;
            }
            const zoom = (clientWidth - offset) / this.width;
            this.addZoom(zoom);
            return Promise.resolve(zoom);
        }
    }
    private addZoom(zoom: number) {
        if (this.zoom && this.zoom.length > 0) {
            const css = [];
            this.zoom.forEach((pZoom: IZoom) => {
                css.push(`${pZoom.select}{`);
                css.push(`  ${pZoom.attribute}: ${pZoom.size * zoom}${pZoom.unit};`);
                css.push("}");
            });
            const cssText = css.join("\n");
            const cssId = "zoom_style";
            this.mountCss.push(cssId);
            addStyle(cssId, cssText);
        }
    }
}
