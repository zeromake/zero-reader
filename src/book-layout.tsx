import { h, Component, findDOMNode } from "zreact";
import Toc from "@/components/toc";
import styl from "@/css/layout.styl";
import BookToolsBar from "@/components/book-tools-bar";
import Animate from "preact-animate";
import throttle from "lodash.throttle";
import { addLinkCss, addStyle, removeHead } from "./utils";

declare interface IZoom {
    select: string;
    attribute: string;
    size: number;
    unit: string;
    media_print: boolean;
}

export default class Layout extends Component<any, any> {
    public tocs: any[];
    public zoom: any[];
    private page: any;
    constructor(p: any, c: any) {
        super(p, c);
        this.state = {
            theme: undefined,
            tocs: undefined,
            meta: undefined,
            container: undefined,
            page: 0,
            pageHtml: "",
            zoom: undefined,
            pageWidth: 0,
        };
        this.tocClick = this.tocClick.bind(this);
        this.showToc = this.showToc.bind(this);
    }
    public resize = throttle(() => {
        this.setZoom();
    }, 15);
    public componentDidMount() {
        addLinkCss(`/library/${this.props.sha}/style.css`, "base_css_id");
        addLinkCss(`/library/${this.props.sha}/bg.css`, "bg_css_id");
        this.getContainer().then(() => {
            this.getZoom();
            return this.getPage(0);
        });
        window.addEventListener("resize", this.resize);
    }
    public componentWillUnmount() {
        removeHead("base_css_id");
        removeHead("bg_css_id");
        removeHead("zoom_style");
        window.removeEventListener("resize", this.resize);
    }
    private tocClick(toc) {
        const page = +toc.page;
        if (!isNaN(page) && page !== this.state.page) {
            this.getPage(page);
        }
    }
    private getContainer() {
        return fetch(`/library/${this.props.sha}/container.json`).then((res) => res.json()).then((data) => {
            this.state.container = data;
            // this.setState({container: data});
        });
    }
    private getPage(num: number) {
        const pageName = this.state.container[num]["data-page-url"];
        return fetch(`/library/${this.props.sha}/${pageName}`).then((res) => res.text()).then((data) => {
            this.setState({
                pageHtml: data,
                page: num,
            });
        });
    }
    private getZoom() {
        return fetch(`/library/${this.props.sha}/zoom.json`).then((res) => res.json()).then((data) => {
            this.state.zoom = data;
            for (const item of data) {
                if (item.select === ".w0" && !item.media_print) {
                    this.state.pageWidth = item.size;
                    break;
                }
            }
            this.setZoom();
        });
    }
    private setZoom() {
        if (this.page) {
            const clientWidth = this.page.clientWidth;
            console.log(clientWidth, this.state.pageWidth);
            const zoom = (clientWidth - 10) / this.state.pageWidth;
            // console.log(zoom);
            this.addZoom(zoom);
        }
    }
    private addZoom(zoom: number) {
        if (this.state.zoom && this.state.zoom.length > 0) {
            const css = [];
            // let flag = false;
            this.state.zoom.forEach((pZoom: IZoom) => {
                // if (pZoom.media_print && !flag) {
                //     flag = true;
                //     css.push("@media print {");
                // }
                // if (!pZoom.media_print && flag) {
                //     flag = false;
                //     css.push("}");
                // }
                css.push(`${pZoom.select}{`);
                css.push(`  ${pZoom.attribute}: ${pZoom.size * zoom}${pZoom.unit};`);
                css.push("}");
            });
            // if (flag) {
            //     flag = false;
            //     css.push("}");
            // }
            const cssText = css.join("\n");
            addStyle("zoom_style", cssText);
        }
    }
    private showToc() {
        if (this.tocs) {
            this.setState((state: any) => {
                state.toc_open = !state.toc_open;
            });
        } else {
            return fetch(`/library/${this.props.sha}/toc.json`).then((res) => res.json()).then((data) => {
                this.tocs = data;
                this.setState((state: any) => {
                    state.toc_open = true;
                });
            });
        }
    }
    public render(props: any, state: any): any {
        const tocClass = styl.toc_layout + (state.theme ? " " + styl[state.theme] : "");
        return (
            <div class={styl.content}>
                <Animate
                    component={null}
                    transitionEnter={true}
                    transitionLeave={true}
                    transitionName = {{
                        enter: "fadeInLeft",
                        leave: "fadeInRight",
                    }}>
                    { state.toc_open ? <div class={tocClass + " animated"}>
                        <div class={styl.toc_content}>
                            <Toc tocs={ this.tocs } onclick={this.tocClick} theme={state.theme}></Toc>
                        </div>
                    </div> : null}
                </Animate>
                <BookToolsBar options={ { showToc: this.showToc } }/>
                <div ref={(vdom: any) => this.page = findDOMNode(vdom)} class={styl.pageHtml}>
                    <div class={styl.view + " w0 h0"} dangerouslySetInnerHTML={{__html: state.pageHtml}}>
                    </div>
                </div>
            </div>
        );
    }
}
