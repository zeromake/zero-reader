import { createElement as h, Component } from "react";
import styl from "../css/layout.styl";
import SvgIcon from "./svg-icon";
import Animate from "preact-animate";

interface IDialogProps {
    title: string;
    close: () => void;
    children?: any;
}

export default class Dialog extends Component<IDialogProps, any> {
    public render() {
        const props = this.props;
        return <div
            {...Animate.filterProps(props, {className: `${styl.toc_layout} animated`})}
            >
            <div className={styl.toc_title}>
                <p>{props.title}</p>
                <SvgIcon name="icon-close_light" className={styl.toc_close} onClick={ props.close }></SvgIcon>
            </div>
            {props.children}
        </div>;
    }
}
