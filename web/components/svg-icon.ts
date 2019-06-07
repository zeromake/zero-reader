import { createElement as h, PureComponent } from "react";

export interface ISvgIconProps {
    name: string;
    className?: string;
    children?: any;
    [name: string]: any;
}

export default class SvgIcon extends PureComponent<ISvgIconProps, any> {
    public render() {
        const props = this.props;
        const { name, children, ...newProps } = props;
        const className = newProps.className ? `svg_icon ${newProps.className}` : "svg_icon";
        return h("svg", {
            ...newProps,
            className,
        }, h("use", {xlinkHref: `#${name}`}));
    }
}
