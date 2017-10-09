import { h, Component } from "zreact";
import Toc from "@/components/toc";
import styl from "@/css/layout.styl";
import BookToolsBar from "@/components/book-tools-bar";

export default class Layout extends Component<any, any> {
    public tocs: any[];
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
        const link = document.createElement("link");
        link.setAttribute("href", `/library/${this.props.sha}/style.css`);
        link.setAttribute("rel", "stylesheet");
        link.id = "base_css_id";
        document.head.appendChild(link);

        this.getContainer().then(() => {
            return this.getPage(0);
        });
    }
    public componentWillUnmount() {
        const link = document.getElementById("base_css_id");
        if (link) {
            document.head.removeChild(link);
        }
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
    public render(props: any, state: any) {
        const tocClass = styl.toc_layout + (state.theme ? " " + styl[state.theme] : "");
        return (
            <div class={styl.content}>
                { state.toc_open ? <div class={tocClass}>
                    <div class={styl.toc_content}>
                        <Toc tocs={ this.tocs } onclick={this.tocClick} theme={state.theme}></Toc>
                    </div>
                </div> : null}
                <BookToolsBar options={ { showToc: this.showToc } }/>
                <div class={styl.pageHtml}>
                    <div class={styl.view + " w0 h0"} dangerouslySetInnerHTML={{__html: state.pageHtml}}>
                    </div>
                </div>
            </div>
        );
    }
}
