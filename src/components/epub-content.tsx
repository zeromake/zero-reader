import { h, findDOMNode, Component } from "react-import";
import { shallowDiffers } from "@/utils";
import lozad from "@/assets/lozad";
import styl from "../css/epub-layout.styl";

// const PdfContent = propsDiffComponent(function _(props) {
//     return <div
//         className={`${props.bg}`}
//         dangerouslySetInnerHTML={{__html: props.pageHtml}}>
//     </div>;
// });
// export default PdfContent;
export default class EpubContent extends Component<any, any> {
    private observer: any;
    private flag: boolean;
    public componentWillUnmount() {
        if (this.props.pageRef) {
            this.props.pageRef(null);
        }
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
        if (this.props.pageRef) {
            this.props.pageRef(document.querySelector(`.${styl.content}>div`));
        }
        Array.prototype.forEach.call(findDOMNode(this).querySelectorAll("img.lozad"), (element: HTMLImageElement) => {
            const dataSrc = element.getAttribute("data-src");
            if (dataSrc) {
                element.src = this.props.library.image(dataSrc);
            }
        })
        Array.prototype.forEach.call(findDOMNode(this).querySelectorAll("image.lozad"), (element: SVGImageElement) => {
            const nameSpace = "http://www.w3.org/1999/xlink";
            const dataSrc = element.getAttribute("data-src");
            if (dataSrc) {
                element.setAttributeNS(nameSpace, "xlink:href", this.props.library.image(dataSrc));
            }
        })
        // if (!this.observer) {
        //     this.observer = lozad("img.lozad", {
        //         target: findDOMNode(this),
        //         load: (element: HTMLImageElement) => {
        //             const dataSrc = element.getAttribute("data-src");
        //             if (dataSrc) {
        //                 element.src = this.props.library.image(dataSrc);
        //             }
        //         },
        //     });
        //     this.observer.observe();
        // } else {
        //     this.observer.unobserve();
        //     this.observer.update();
        // }
    }
    public shouldComponentUpdate(props: any, state: any): boolean {
        // props只要一个不同就返回true
        const flag = shallowDiffers(this.props, props);
        return flag;
    }

    public render() {
        const props = this.props;
        return <div className={styl.content + " " + (this.props.not ? styl.content_not : "")}
            dangerouslySetInnerHTML={{__html: props.pageHtml}}>
        </div>;
    }
}
