import { h, Component } from "react-import";
import style from "../css/button.styl";

export default class Button extends Component<any, any> {
    public static defaultProps: any = {
        classPrefix: style.btn,
        componentClass: "button",
        appearance: "default",
        color: null,
        block: false,
    };
    public state: any;
    public props: any;
    public refs: any;
    constructor(p: any, c: any) {
        super(p, c);
    }
    public render() {
        const { children, className, classPrefix, componentClass, appearance, color, block, ...props } = this.props;
        const appearanceClass = "btn-" + appearance;
        const classArr: string[] = [classPrefix, style[appearanceClass]];
        if (color) {
            classArr.push(style["btn-" + color]);
        }
        if (block) {
            classArr.push(style["btn-block"]);
        }
        if (className) {
            classArr.push(className);
        }
        return h(componentClass, {...props, className: classArr.join(" ")}, children);
    }
}
