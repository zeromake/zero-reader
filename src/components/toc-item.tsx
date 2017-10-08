import { h, Component } from "zreact";
import styl from "@/css/toc.styl";

export default class TocItem extends Component<any, any>{
    constructor(p: any, c: any) {
        super(p, c);
        this.state = { ...p.toc };
        this.itemClick = this.itemClick.bind(this);
        this.itemToggler = this.itemToggler.bind(this);
    }
    public shouldComponentUpdate(nextProps: any, nextState: any, nextContext: any): boolean {
        return this.state.disable != nextState.disable;
    }
    itemClick() {
        this.props.onclick(this.state)
    }
    itemToggler() {
        this.setState((state: any)=> {
            state.disable = !state.disable
        })
    }
    render(props: any, state: any) {
        const propsClick = props.onclick;
        const toc = state;
        return <div class={ styl.tocItem }>
            {
                toc.children ? (<div class={styl.tocItemToggler + (!toc.disable ? " " + styl.none : "")} onClick={this.itemToggler}>
                    </div>) : null
            }
            <a href={'#' + toc.page} onClick={this.itemClick}>{toc.text}</a>
            {
                toc.children ? <div class={ styl.tocItems}>
                {
                    toc.children.map((item: any) => <TocItem onclick={props.onclick} toc={item}/>)
                }
                </div> : null
            }
        </div>
    }
}