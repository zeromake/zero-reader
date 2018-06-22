import { h, findDOMNode, Component } from "react-import";
import { shallowDiffers } from "../utils";
import lozad from "../assets/lozad";
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
    private offsetWidth: number;

    public componentWillUnmount() {
        if (this.props.pageRef) {
            this.props.pageRef(null);
        }
        if (this.observer) {
            this.observer.unobserve();
            this.observer = null;
        }
        this.setHtmlPage();
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
        this.setHtmlPage();
    }

    /**
     * 计算当前页面翻页数
     */
    public setHtmlPage() {
        if (this.props.setHtmlPage && this.props.columnCount !== 0) {
            const base = findDOMNode(this);
            let lastChild: HTMLElement = base.lastElementChild as HTMLElement;
            const offsetLeft = lastChild.offsetLeft;
            const offsetWidth = (lastChild.offsetWidth + 45) * this.props.columnCount;
            this.offsetWidth = offsetWidth;
            let pageNum = 0;
            if (offsetLeft > offsetWidth) {
                pageNum = offsetLeft / offsetWidth;
            }
            if (pageNum === 0) {
                // lastChild = lastChild.lastElementChild as HTMLElement;
                while (true) {
                    const lastElementChild = lastChild.lastElementChild as HTMLElement;
                    if (lastElementChild && lastElementChild.offsetLeft) {
                        lastChild = lastElementChild;
                    } else {
                        break;
                    }
                }
                pageNum = lastChild.offsetLeft / offsetWidth;
            }
            let htmlPage = 0;
            if (pageNum % 1) {
                htmlPage = ~~(pageNum) + 1;
            } else {
                htmlPage = pageNum;
            }
            // console.log("----setHtmlPage---", htmlPage);
            this.props.setHtmlPage(htmlPage);
        }
    }
    protected bindObserver() {
        // Array.prototype.forEach.call(findDOMNode(this).querySelectorAll("img.lozad"), (element: HTMLImageElement) => {
        //     const dataSrc = element.getAttribute("data-src");
        //     if (dataSrc) {
        //         element.src = this.props.library.image(dataSrc);
        //     }
        // });
        Array.prototype.forEach.call(findDOMNode(this).querySelectorAll("image"), (element: SVGImageElement) => {
            const nameSpace = "http://www.w3.org/1999/xlink";
            const dataSrc = element.getAttribute("data-src");
            if (dataSrc) {
                element.setAttributeNS(nameSpace, "xlink:href", this.props.library.image(dataSrc));
            }
        });
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

    /**
     * 滚动到锚点
     * @param hash 需要滚动到id
     */
    public scrollHash(hash: string) {
        const idHash = decodeURI(hash);
        const base = findDOMNode(this);
        const scrollView = document.getElementById(idHash) || base.querySelector(`[name='${idHash}']`);
        if (scrollView) {
            if (this.props.columnCount === 0) {
                scrollView.scrollIntoView();
            } else {
                const offsetLeft = (scrollView as HTMLElement).offsetLeft;
                const pageNum = offsetLeft / this.offsetWidth;
                const htmlPage = pageNum % 1 ? ~~(pageNum) + 1 : pageNum;
                return htmlPage;
            }
        }
    }

    public render() {
        const props = this.props;
        const style: any = {};
        let className = styl.content + " reader-content";
        if (this.props.columnCount !== 0) {
            className += " " + styl.content_not;
            style.columns = `auto ${this.props.columnCount}`;
        }
        if (this.props.columnOffset !== 0 && this.offsetWidth) {
            const offset = this.offsetWidth * this.props.columnOffset;
            style.left = `-${offset}px`;
        }
        return <div
            className={className}
            dangerouslySetInnerHTML={{__html: props.pageHtml}}
            style={style}
        >
        </div>;
    }
}
