import { h, findDOMNode, Component } from "react-import";
import styl from "@/css/layout.styl";
import { shallowDiffers } from "../utils";
import lozad from "../assets/lozad";

// const PdfContent = propsDiffComponent(function _(props) {
//     return <div
//         className={`${props.bg}`}
//         dangerouslySetInnerHTML={{__html: props.pageHtml}}>
//     </div>;
// });
// export default PdfContent;
export default class PdfContent extends Component<any, any> {
    private observer: any;
    private flag: boolean;
    public componentWillUnmount() {
        if (this.observer) {
            this.observer.unobserve();
            this.observer = null;
        }
    }
    public componentDidUpdate(previousProps: any, previousState: any, previousContext: any) {
        if (this.props.pageHtml) {
            if (!this.flag) {
                this.flag = true;
                setTimeout(this.bindObserver.bind(this));
            } else {
                this.bindObserver();
            }
        }
    }
    protected bindObserver() {
        if (!this.observer) {
            this.observer = lozad(".lozad", {
                target: findDOMNode(this),
                load: (element) => {
                    if (element.getAttribute("data-src")) {
                        element.src = this.props.library.image(element.getAttribute("data-src"));
                    }
                },
            });
            this.observer.observe();
        } else {
            this.observer.unobserve();
            this.observer.update();
        }
    }
    public shouldComponentUpdate(props: any, state: any): boolean {
        // props只要一个不同就返回true
        const flag = shallowDiffers(this.props, props);
        return flag;
    }
    public render() {
        const props = this.props;
        return <div
            className={`${props.bg}`}
            dangerouslySetInnerHTML={{__html: props.pageHtml}}>
        </div>;
    }
}
