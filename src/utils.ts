import { h, Component, Children } from "react-import";

export function addLinkCss(href, id) {
    const link = document.getElementById(id);
    if (link) {
        return;
    }
    const newlink = document.createElement("link");
    newlink.setAttribute("href", href);
    newlink.setAttribute("rel", "stylesheet");
    newlink.id = id;
    document.head.appendChild(newlink);
}

export function removeHead(id) {
    const link = document.getElementById(id);
    if (link) {
        document.head.removeChild(link);
    }
}

export function addStyle(id: string, css: string) {
    const style = document.getElementById(id);
    if (style) {
        style.innerHTML = css;
        return;
    }
    const newstyle = document.createElement("style");
    newstyle.setAttribute("type", "text/css");
    newstyle.id = id;
    newstyle.innerHTML = css;
    document.head.appendChild(newstyle);
}

export function buildBlock(x: number, y: number, scaleX: number, scaleY?: number) {
    scaleY = scaleY || scaleX;
    const X = x * scaleX;
    const X2 = X * 2;
    const Y = y * scaleY;
    const Y2 = Y * 2;
    function isBlock(clientX: number, clientY: number): number {
        let type = 0;
        if (clientX <= X) {
            type = 1;
        } else if (clientX >= X2) {
            type = 2;
        } else if (clientY <= Y) {
            type = 1;
        } else if (clientY >= Y2) {
            type = 2;
        }
        return type;
    }
    (isBlock as any).height = y;
    (isBlock as any).width = x;
    return isBlock;
}

export function shallowDiffers(a: any, b: any): boolean {
    for (const i in a) {
        if (!(i in b)) {
            return true;
        }
    }
    for (const i in b) {
        if (a[i] !== b[i]) {
            return true;
        }
    }
    return false;
}

export function propsDiffComponent(render: (props: any) => any) {
    class Content extends Component<any, any> {
        public shouldComponentUpdate(props: any, state: any): boolean {
            // props只要一个不同就返回true
            const flag = shallowDiffers(this.props, props);
            return flag;
        }
        public render() {
            const props = this.props;
            return render(props);
        }
    }
    return Content;
}

export function filterPropsComponent(props) {
    let vnode: any = "";
    if (props.children) {
        vnode = Children.only(props.children);
    }
    return vnode;
}


declare const AndroidFullScreen: any;
export function togglerFullScreen(show: boolean) {
    if (typeof AndroidFullScreen !== "undefined") {
        AndroidFullScreen.isSupported(function() {
            // console.log("--------", show);
            if (show) {
                AndroidFullScreen.showSystemUI();
            } else {
                AndroidFullScreen.immersiveMode();
            }
        });
    } 
}
