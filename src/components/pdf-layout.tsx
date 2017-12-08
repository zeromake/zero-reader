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
}

export default class PdfLayout extends AbcLayout<IBookState, IPdfMeta> {
    private page: any;
    private zoom?: IZoom[];
    private width?: number;
    private height?: number;
    public tocs: any[];

    constructor(props, content) {
        super(props, content);
        this.state.offset = 20;
    }

    public resize = throttle(() => {
        this.setZoom();
    }, 15);

    public componentDidMount() {
        this.lozadOptions = {
            ...this.lozadOptions,
            target: this.page || document,
        };
        this.init().then(() => {
            if (this.props.meta.zoom) {
                this.getZoom(this.props.meta.zoom);
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
        return <div ref={((vdom: any) => this.page = findDOMNode(vdom))} className={styl.pageHtml}>
                <div className={styl.view + " w0 h0 " + styl[state.bg]} dangerouslySetInnerHTML={{__html: state.pageHtml}}>
                </div>
            </div>;
    }
    private getZoom(zoom: string) {
        return this.library.json(zoom).then((data) => {
            this.zoom = data.css;
            this.width = data.width;
            this.height = data.height;
            this.setZoom(true);
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
