import { createElement as h, Component } from "react";
import { findDOMNode } from "react-dom";
import styl from "../css/layout.styl";
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
        if (this.props.pageHtml != null) {
            if (!this.flag) {
                this.flag = true;
                setTimeout(this.bindObserver);
            } else {
                this.bindObserver();
            }
        }
    }
    protected bindObserver = () => {
        // Array.prototype.forEach.call(findDOMNode(this).querySelectorAll("img.lozad"), (element: HTMLImageElement) => {
        //     const dataSrc = element.getAttribute("data-src");
        //     if (dataSrc) {
        //         element.src = this.props.library.image(dataSrc);
        //     }
        // });
        if (!this.observer) {
            this.observer = lozad("img.lozad", {
                target: findDOMNode(this),
                load: (element: HTMLImageElement) => {
                    const dataSrc = element.getAttribute("data-src");
                    if (dataSrc) {
                        element.src = this.props.library.image(dataSrc);
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
            dangerouslySetInnerHTML={{__html: props.pageHtml}}>
        </div>;
    }
}
