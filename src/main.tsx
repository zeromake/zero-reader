import "es6-promise/auto";
import "unfetch/polyfill";
import { h, render } from "react-import";
import "intersection-observer";
import MainRouter from "./router";
import "animate.css";
import "./css/main.styl";
import "./css/base.css";
import "./assets/icons";
// import "font-awesome/css/font-awesome.min.css";

declare const process: any;

render(<MainRouter/>, document.getElementById("app"));
// if (process.env.NODE_ENV !== "production") {
//     import("zreact/devtools").then(({ initDevTools }) => {
//         try {
//             initDevTools();
//         } catch (e) {

//         }
//     });
// }
