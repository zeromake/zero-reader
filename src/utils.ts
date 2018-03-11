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
        AndroidFullScreen.isSupported(function _() {
            // console.log("--------", show);
            if (show) {
                AndroidFullScreen.showSystemUI();
            } else {
                AndroidFullScreen.immersiveMode();
            }
        });
    }
}

function _updateForm(component: Component<any, any>, attName: string) {
    // form.account
    return function updateForm(e: any) {
        const attrsArr = attName.split(".");
        const updateData = {};
        let state = component.state;
        let data = updateData;
        const value = (e.target as HTMLInputElement).value;
        for (let i = 0, len = attrsArr.length; i < len; i ++) {
            const attr = attrsArr[i];
            if (attr && attr !== "") {
                let old: any = null;
                if (state) {
                    old = state[attr];
                    state = old;
                }
                if (i === len - 1) {
                    data[attr] = value;
                } else {
                    if (old) {
                        data = data[attr] = {...old};
                    } else {
                        data = data[attr] = {};
                    }
                }
            }
        }
        // const old = component.state[formName] || {};
        component.setState(updateData);
    };
}

export function updateFormFunction(component: Component<any, any>, attName: string) {
    let $formUpdate: {[name: string]: any} = (component as any).$formUpdate;
    let updateFun: ((e: any) => void) | null | undefined = null;
    const attrsArr = attName.split(".");
    if (!$formUpdate) {
        $formUpdate = (component as any).$formUpdate = {};
    }
    let $form: {[attName: string]: any} | null = $formUpdate;

    for (let i = 0, len = attrsArr.length; i < len; i ++) {
        const attr = attrsArr[i];
        if (attr && attr !== "") {
            if (i === len - 1) {
                updateFun = $form[attr];
                if (!updateFun) {
                    updateFun = _updateForm(component, attName);
                    $form[attr] = updateFun;
                }
            } else {
                let temp = $form[attr];
                if (!temp) {
                    temp = $form[attr] = {};
                }
                $form = temp;
            }
        }
    }
    return updateFun;
}

function getDeepValue(obj: {[name: string]: any}, attName: string): any {
    const attrsArr = attName.split(".");
    let tempObj = obj;
    let value: any;
    for (let i = 0, len = attrsArr.length; i < len; i ++) {
        const attr = attrsArr[i];
        if (tempObj && attr in tempObj) {
            if (i === len - 1) {
                value = tempObj[attr];
            } else {
                tempObj = tempObj[attr];
            }
        } else {
            break;
        }
    }
    return value;
}

interface IForm {
    type: string;
    pattern: string;
    title: string;
    required: boolean;
    placeholder: string;
}
function createObject(proto: any = null): any {
    const obj = {};
    (obj as any).__proto__ = null;
    return obj
}
const FormList = [
    "type",
    "pattern",
    "title",
    "required",
    "placeholder",
];

export function bindUpdateForm(component: Component<any, any>, formConfig: {[name: string]: IForm}, formName?: string) {
    return (attName: string) =>  {
        let attr = attName;
        if (formName && formName !== "") {
            attr = formName + "." + attName;
        }
        const deep = createObject();
        const form = formConfig[attName];
        if (form != null) {
            for(const name of FormList) {
                if (name in form) {
                    deep[name] = form[name];
                }
            }
        }
        
        return {
            value: getDeepValue(component.state, attr),
            onChange: updateFormFunction(component, attr),
            // onInvalid: console.log,
            ...deep
        };
    };
}

export function deepForm() {

}
