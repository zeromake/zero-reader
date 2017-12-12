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
    private zoom?: IZoom[];
    private width?: number;
    private height?: number;
    public tocs: any[];
    private load: boolean;

    constructor(props, content) {
        super(props, content);
        console.log("props: ", props);
        this.state.offset = 20;
        this.load = false;
    }

    public resize = throttle(() => {
        const callback = () => this.setZoom().then((zoom: number) => this.setState({ zoom }));
        if (typeof requestAnimationFrame !== "undefined") {
            requestAnimationFrame(callback);
        } else {
            setTimeout(callback());
        }
    }, 100);
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
                        zoom,
                    });
                });
                window.addEventListener("resize", this.resize as any);
            }
        });
    }
    private nextPage = () => {
        this.setPage(this.state.page + 1);
        this.page.scrollTo(0, 0);
    }

    private pageClick = (event: MouseEvent) => {
        const page = this.page;
        console.log("pageClick", event.clientX, event.clientY, page.clientWidth, page.clientHeight);
    }
    protected  renderHeader() {
        const state = this.state;
        // const tocClass = styl.toc_layout + (state.theme ? " " + styl[state.theme] : "");
        return <BookToolsBar options={ { showToc: () => {this.setState({ toc_open: !state.toc_open }); } } }/>;
    }
    protected  renderFooter() {
        // return <BottomBar/>;
    }
    protected  renderContent() {
        const state = this.state;
        return <div
                    onClick={this.pageClick}
                    className={styl.pageHtml}
                    >
                <div
                    className={`${styl.view} ${styl[state.bg]}`}
                    dangerouslySetInnerHTML={{__html: state.pageHtml}}
                    style={{ width: this.width * state.zoom }}
                    >
                </div>
                {/* { state.page < this.pageNum ? <div onClick={ this.nextPage }>下一页</div> : null } */}
            </div>;
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
