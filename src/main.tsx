import "es6-promise/auto";
import "unfetch/polyfill";
import { h, render } from "react-import";
import "intersection-observer";
import "animate.css";
import "./css/main.styl";
import "./css/base.css";
// import "../node_modules/sweetalert2/dist/sweetalert2.min.css";
import "./assets/icons/index";
import { initDevTools } from "zreact/devtools";
import MainRouter from "./router";
// import "sakura.css";
function zero_render(vdom: JSX.Element, dom: Element) {
    const root = dom.parentElement;
    // if (dom.children.length === 0) {
    //     root.removeChild(dom);
    //     return render(vdom, root);
    // } else {
    return render(vdom, root, dom);
    // }
}

zero_render(<MainRouter/>, document.getElementById("app"));

if (process.env.NODE_ENV !== "production" && initDevTools) {
    initDevTools();
}
// import "font-awesome/css/font-awesome.min.css";

declare const process: any;

// if (process.env.NODE_ENV !== "production") {
//     import("zreact/devtools").then(({ initDevTools }) => {
//         try {
//             initDevTools();
//         } catch (e) {

//         }
//     });
// }
