import { h, Component } from "react-import";
import styl from "@/css/layout.styl";
import SvgIcon from "./svg-icon";

interface DialogProps {
    title: string;
    close: () => void;
}

export default class Dialog extends Component<DialogProps, any> {
    public render() {
        const props = this.props;
        return <div
            className={`${styl.toc_layout} animated`}
            onClick={(event) => event.stopPropagation()}>
            <div className={styl.toc_title}>
                <p>{props.title}</p>
                {h(SvgIcon, { name: "icon-close_light", className: styl.toc_close, onClick: props.close })}
            </div>
            {props.children}
        </div>
    }
}
