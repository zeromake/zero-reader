import { h, findDOMNode, route } from "react-import";
import AbcLayout, { IabcState } from "./abc-layout";
import styl from "@/css/layout.styl";
import BookToolsBar from "@/components/book-tools-bar";
import BottomBar from "@/components/bottom-bar";
import { addStyle, buildBlock } from "@/utils";
import Toc from "@/components/toc";
import throttle from "lodash.throttle";
import { IPdfMeta } from "../types/index";
import PdfContent from "./pdf-content";

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

// const PdfContent = propsDiffComponent("div");

export default class PdfLayout extends AbcLayout<IBookState, IPdfMeta> {
    private zoom?: IZoom[];
    private width?: number;
    private height?: number;
    public tocs: any[];
    protected isBlock: (x: number, y: number) => number;

    constructor(props, content) {
        super(props, content);
        // console.log("props: ", props);
        this.state.offset = 0;
        this.load = false;
    }

    public resize = throttle(() => {
        const callback = () => this.setZoom().then((zoom: number) => {
            if (zoom !== this.state.zoom) {
                this.setState({ zoom });
            }
        });
        if (typeof requestAnimationFrame !== "undefined") {
            requestAnimationFrame(callback);
        } else {
            setTimeout(callback());
        }
    }, 100);

    public componentDidMount() {
        this.init().then(({ pageHtml, page }) => {
            if (this.props.meta.zoom) {
                this.getZoom(this.props.meta.zoom).then((zoom: number) => {
                    this.setState({
                        pageHtml,
                        page,
                        zoom,
                    }, () => window.addEventListener("resize", this.resize as any));
                });
            }
        });
    }
    protected  renderHeader() {
        // const state = this.state;
        // const tocClass = styl.toc_layout + (state.theme ? " " + styl[state.theme] : "");
        // return <BookToolsBar options={ { showToc: () => {this.setState({ toc_open: !state.toc_open }); } } }/>;
    }
    protected  renderFooter() {
        return <BottomBar data-show={this.state.barShow}/>;
    }
    protected  renderContent() {
        const state = this.state;
        return <div className={styl.pageHtml}>
                {/* <PdfContent
                    className={`${styl.view} ${styl[state.bg]}`}
                    dangerouslySetInnerHTML={{__html: state.pageHtml}}
                    style={{ width: this.width * state.zoom }}>
                </PdfContent>; */}
                <PdfContent
                    view={styl.view}
                    bg={styl[state.bg]}
                    pageHtml={state.pageHtml}
                    width={this.width * state.zoom}
                ></PdfContent>
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
            const clientHeight = this.page.clientHeight;
            this.isBlock = buildBlock(clientWidth, clientHeight, 1 / 3);
            const offset = this.state.offset;
            const zoom = (clientHeight - offset) / this.height;
            if (this.state.zoom !== zoom) {
                this.addZoom(zoom);
            }
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
