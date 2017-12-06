import { h, Component } from "react-import";
import styl from "@/css/toc.styl";
import Animate from "preact-animate";

export default class TocItem extends Component<any, any> {
    constructor(p: any, c: any) {
        super(p, c);
        this.state = { ...p.toc };
        this.itemClick = this.itemClick.bind(this);
        this.itemToggler = this.itemToggler.bind(this);
    }
    public shouldComponentUpdate(nextProps: any, nextState: any, nextContext: any): boolean {
        return this.state.disable !== nextState.disable;
    }
    private itemClick() {
        this.props.onclick(this.state);
    }
    private itemToggler() {
        this.setState((state: any) => {
            state.disable = !state.disable;
        });
    }
    public render(props: any, state: any): any {
        const propsClick = props.onclick;
        const toc = state;
        return <div className={ styl.tocItem }>
            {
                toc.children ? (<div className={styl.tocItemToggler} onClick={this.itemToggler}><i className={"fa" + (toc.disable ? " fa-chevron-down " + styl.none : " fa-chevron-right")}>
                    </i></div>) : null
            }
            <a className={styl.toc_text} href={"#" + toc.page} onClick={this.itemClick}>{toc.text}</a>
            { toc.children ? <Animate
                    showProp="data-show"
                    component={null}
                    transitionEnter={true}
                    transitionLeave={true}
                    transitionName = {{
                        enter: "fadeInRight",
                        leave: "fadeOutRight",
                    }}>
                <div  data-show={!toc.disable} className={ styl.tocItems + " animated"}>
                {
                    toc.children.map((item: any) => <TocItem onclick={props.onclick} toc={item}/>)
                }
                </div>
            </Animate> : null }
        </div>;
    }
}
