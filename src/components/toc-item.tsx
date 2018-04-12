import { h, Component } from "react-import";
import styl from "@/css/toc.styl";
import Animate from "preact-animate";
import { IAbcToc, IEpubToc, IPdfToc } from "@/types/index";
import { shallowDiffers } from "@/utils";
import SvgIcon from "./svg-icon";

interface ITocProps {
    key: string;
    toc: IAbcToc;
    level: number;
    onclick?: (tocs: IAbcToc) => void;
}

export default class TocItem extends Component<ITocProps, IAbcToc> {
    public static getDerivedStateFromProps?(nextProps: ITocProps, previousState: IAbcToc): IAbcToc {
        return { ...nextProps.toc};
    }
    public base;
    constructor(p: ITocProps, c: any) {
        super(p, c);
        this.state = { ...p.toc };
        this.itemClick = this.itemClick.bind(this);
        this.itemToggler = this.itemToggler.bind(this);
    }
    public componentWillReceiveProps(props: ITocProps, context: any) {
        this.setState(TocItem.getDerivedStateFromProps(props, this.state));
    }

    public shouldComponentUpdate(nextProps: ITocProps, nextState: IAbcToc, nextContext: any): boolean {
        const flag = shallowDiffers(this.state, nextState);
        return flag;
    }

    private itemClick(event) {
        event.stopPropagation();
        event.preventDefault();
        if (this.props.onclick) {
            this.props.onclick(this.state);
        }
    }
    private itemToggler(event) {
        event.stopPropagation();
        this.setState({
            disable: !this.state.disable,
        });
    }
    public render(): any {
        // const propsClick = this.props.onclick;
        const props = this.props;
        const toc = this.state;
        return <div className={ styl.tocItem }>
            {
                toc.children ? (
                <div className={styl.tocItemToggler} onClick={this.itemToggler}>
                    {h(SvgIcon, {className: styl.icon, name: toc.disable ? "icon-expand_less" : "icon-expand_more" })}
                    {/* <i className={"fa" + (toc.disable ? " fa-chevron-down " + styl.none : " fa-chevron-right")}>
                    </i> */}
                </div>) : null
            }
            <a className={styl.toc_text} title={String(toc.page)} onClick={this.itemClick}>{toc.text}
            </a>
            { toc.children ? <Animate
                    showProp="data-show"
                    component={null}
                    transitionEnter={true}
                    transitionLeave={true}
                    transitionName = {{
                        enter: "fadeInDown",
                        leave: "fadeOutUp",
                    }}
                    isRender={true}>
                <div data-show={toc.disable} className={ styl.tocItems + " animated"}>
                {
                    toc.children.map((item: IAbcToc, index: number) => (
                        h(
                            TocItem,
                            {
                                onclick: props.onclick,
                                key: `${props.level}_${index}_${item.index}`,
                                toc: item,
                                level: props.level + 1,
                            },
                        )
                    ))
                }
                </div> </Animate> : null }
        </div>;
    }
}
