import { h, Component, findDOMNode } from "zreact";
import Toc from "@/components/toc";
import styl from "@/css/layout.styl";
import BookToolsBar from "@/components/book-tools-bar";
import BottomBar from "@/components/bottom-bar";
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
    private cssMount: string[] = [];
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
            width: 0,
            height: 0,
            offset: 0,
            toc_open: false,
        };
        this.tocClick = this.tocClick.bind(this);
        this.showToc = this.showToc.bind(this);
    }
    public resize = throttle(() => {
        this.setZoom();
    }, 15);
    public componentDidMount() {
        this.getBookMeta().then((meta) => {
            if (meta) {
                const page_style = meta.page_style;
                if (page_style && page_style.length > 0) {
                    let index = 1;
                    page_style.forEach((style: string) => {
                        const cssId = `css_id_${index}`;
                        index ++;
                        this.cssMount.push(cssId);
                        addLinkCss(`/library/${this.props.sha}/${style}`, cssId);
                    });
                }
                // addLinkCss(`/library/${this.props.sha}/bg.css`, "bg_css_id");
                this.getContainer(meta.container).then(() => {
                    return this.getPage(0, () => {
                        this.getZoom(meta.zoom);
                    });
                });
                window.addEventListener("resize", this.resize);
            }
        });
    }
    public getBookMeta() {
        return fetch(`/library/${this.props.sha}/meta.json`).then((res) => res.json()).then((data) => {
            this.state.meta = data;
            return data;
        });
    }
    public componentWillUnmount() {
        if (this.cssMount.length > 0) {
            let cssId = this.cssMount.pop();
            while (cssId) {
                removeHead(cssId);
                cssId = this.cssMount.pop();
            }
        }
        // removeHead("base_css_id");
        // removeHead("bg_css_id");
        // removeHead("zoom_style");
        window.removeEventListener("resize", this.resize);
    }
    private tocClick(toc) {
        const page = +toc.page;
        if (!isNaN(page) && page !== this.state.page) {
            this.getPage(page);
        }
    }
    private getContainer(container: string) {
        return fetch(`/library/${this.props.sha}/${container}`).then((res) => res.json()).then((data) => {
            this.state.container = data;
            // this.setState({container: data});
        });
    }
    private getPage(num: number, callback?: any) {
        const pageName = this.state.container[num]["data-page-url"];
        return fetch(`/library/${this.props.sha}/${pageName}`).then((res) => res.text()).then((data) => {
            this.setState({
                pageHtml: data,
                page: num,
            }, callback);
        });
    }
    private getZoom(zoom: string) {
        return fetch(`/library/${this.props.sha}/${zoom}`).then((res) => res.json()).then((data) => {
            this.state.zoom = data.css;
            this.state.width = data.width;
            this.state.height = data.height;
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
            const zoom = (clientWidth - offset) / this.state.width;
            // console.log(zoom);
            this.addZoom(zoom);
        }
    }
    private addZoom(zoom: number) {
        if (this.state.zoom && this.state.zoom.length > 0) {
            const css = [];
            this.state.zoom.forEach((pZoom: IZoom) => {
                css.push(`${pZoom.select}{`);
                css.push(`  ${pZoom.attribute}: ${pZoom.size * zoom}${pZoom.unit};`);
                css.push("}");
            });
            const cssText = css.join("\n");
            const cssId = "zoom_style";
            this.cssMount.push(cssId);
            addStyle(cssId, cssText);
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
    public pageClick = (event: MouseEvent) => {
        console.log(event);
    }
    public render(props: any, state: any): any {
        const tocClass = styl.toc_layout + (state.theme ? " " + styl[state.theme] : "");
        return (
            <div class={styl.content}>
                <Animate
                    showProp="data-show"
                    component={null}
                    transitionEnter={true}
                    transitionLeave={true}
                    transitionName = {{
                        enter: "fadeInLeft",
                        leave: "fadeInRight",
                    }}>
                    <div class={tocClass + " animated"} data-show={state.toc_open}>
                        <div class={styl.toc_content}>
                            {this.tocs ? <Toc tocs={ this.tocs } onclick={this.tocClick} theme={state.theme}></Toc> : null}
                        </div>
                    </div>
                </Animate>
                <BookToolsBar options={ { showToc: this.showToc } }/>
                <div ref={(vdom: any) => this.page = findDOMNode(vdom)} class={styl.pageHtml} onClick={this.pageClick}>
                    <div class={styl.view + " w0 h0"} dangerouslySetInnerHTML={{__html: state.pageHtml}}>
                    </div>
                </div>
                <BottomBar></BottomBar>
            </div>
        );
    }
}
