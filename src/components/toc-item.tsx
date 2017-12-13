import { h, Component } from "react-import";
import styl from "@/css/toc.styl";
import Animate from "preact-animate";
import { IAbcToc, IEpubToc, IPdfToc } from "../types/index";

interface ITocProps {
    toc: IAbcToc;
    onclick?: (tocs: IAbcToc) => void;
}
interface ITocState {
    toc: IAbcToc;
}

export default class TocItem extends Component<ITocProps, ITocState> {
    public base;
    constructor(p: ITocProps, c: ITocState) {
        super(p, c);
        const toc: IAbcToc = { ...p.toc };
        this.state = { toc } as ITocState;
        this.itemClick = this.itemClick.bind(this);
        this.itemToggler = this.itemToggler.bind(this);
    }
    public shouldComponentUpdate(nextProps: ITocProps, nextState: ITocState, nextContext: any): boolean {
        return this.state.toc !== nextState.toc || this.state.toc.disable !== nextState.toc.disable;
    }
    private itemClick() {
        if (this.props.onclick) {
            this.props.onclick(this.state.toc);
        }
    }
    private itemToggler() {
        this.setState((state: ITocState) => {
            state.toc.disable = !state.toc.disable;
        });
    }
    public render(props: any, state: any): any {
        // const propsClick = this.props.onclick;
        const toc = this.state.toc;
        return <div className={ styl.tocItem }>
            {
                toc.children ? (
                <div className={styl.tocItemToggler} onClick={this.itemToggler}>
                    <i className={"fa" + (toc.disable ? " fa-chevron-down " + styl.none : " fa-chevron-right")}>
                    </i>
                </div>) : null
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
                    toc.children.map((item: IAbcToc) => <TocItem onclick={props.onclick} toc={item}/>)
                }
                </div>
            </Animate> : null }
        </div>;
    }
}
