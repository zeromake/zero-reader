import { h, Component } from "zreact";
import Toc from "@/components/toc";
import styl from "@/css/layout.styl";
import BookToolsBar from "@/components/book-tools-bar";

export default class Layout extends Component<any, any> {
    public tocs: any[];
    constructor(p: any, c: any) {
        super(p, c);
        this.state = {
            theme: undefined
        }
        this.tocClick = this.tocClick.bind(this);
        this.showToc = this.showToc.bind(this);
    }
    tocClick() {

    }
    showToc() {
        if (this.tocs) {
            this.setState(state => {
                state.toc_open = !state.toc_open
            })
        } else {
            fetch(`/library/${this.props.sha}/toc.json`).then(res => res.json()).then(data => {
                this.tocs = data
                this.setState(state => {
                    state.toc_open = true
                })
            })
        }
    }
    render(props: any, state: any) {
      console.log(props)
        const toc_class = styl.toc_layout + (state.theme ? " " + styl[state.theme]: "")
        return (
            <div class={styl.content}>
                { state.toc_open ? <div class={toc_class}>
                    <div class={styl.toc_content}>
                        <Toc tocs={ this.tocs } onclick={this.tocClick} theme={state.theme}></Toc>
                    </div>
                </div>: null}
                <BookToolsBar options={ { showToc: this.showToc } }/>
            </div>
        );
    }
} 