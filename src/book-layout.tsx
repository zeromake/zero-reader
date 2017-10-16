import { h, Component } from "zreact";
import Toc from "@/components/toc";
import styl from "@/css/layout.styl";
import BookToolsBar from "@/components/book-tools-bar";
import Animate from "preact-animate";
import { addLinkCss, removeLinkCss } from "./utils";

export default class Layout extends Component<any, any> {
    public tocs: any[];
    public zoom: any[];
    constructor(p: any, c: any) {
        super(p, c);
        this.state = {
            theme: undefined,
            tocs: undefined,
            meta: undefined,
            container: undefined,
            page: 0,
            pageHtml: "",
        };
        this.tocClick = this.tocClick.bind(this);
        this.showToc = this.showToc.bind(this);
    }
    public componentDidMount() {
        addLinkCss(`/library/${this.props.sha}/style.css`, "base_css_id");
        addLinkCss(`/library/${this.props.sha}/bg.css`, "bg_css_id");
        this.getContainer().then(() => {
            return this.getPage(0);
        });
    }
    public componentWillUnmount() {
        removeLinkCss("base_css_id");
        removeLinkCss("bg_css_id");
    }
    private tocClick(toc) {
        const page = +toc.page;
        if (!isNaN(page) && page !== this.state.page) {
            this.getPage(page);
        }
    }
    private getContainer() {
        return fetch(`/library/${this.props.sha}/container.json`).then((res) => res.json()).then((data) => {
            this.setState({container: data});
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
            // this.zoom =
        });
    }
    private addZoom(zoom: number) {

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
                <div class={styl.pageHtml}>
                    <div class={styl.view + " w0 h0"} dangerouslySetInnerHTML={{__html: state.pageHtml}}>
                    </div>
                </div>
            </div>
        );
    }
}
