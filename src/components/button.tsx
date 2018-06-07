import { h, Component } from "react-import";
import style from "../css/button.styl";

export default class Button extends Component<any, any> {
    public static defaultProps: any = {
        classPrefix: style.btn,
        componentClass: "button",
    };
    public state: any;
    public props: any;
    constructor(p: any, c: any) {
        super(p, c);
    }
    public render() {
        const { children, className, classPrefix, componentClass, ...props } = this.props;
        return h(componentClass, {...props, className: [className, classPrefix].join(" ")}, children);
    }
}
