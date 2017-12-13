import { h, findDOMNode, Component } from "react-import";
import styl from "@/css/layout.styl";
import { shallowDiffers } from "@/utils";

export default class PdfContent extends Component<any, any> {
    public shouldComponentUpdate(props: any, state: any): boolean {
        // props只要一个不同就返回true
        // this.props.children = undefined;
        // props.children = undefined;
        const flag = shallowDiffers(this.props, props);
        return flag;
    }
    public render() {
        const props = this.props;
        return <div
            className={`${props.view} ${props.bg}`}
            dangerouslySetInnerHTML={{__html: props.pageHtml}}
            style={{ width: props.width }}>
        </div>;
    }
}
