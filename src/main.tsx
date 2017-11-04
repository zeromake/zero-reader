import "unfetch/polyfill";
import { render, h } from "zreact";
// import { initDevTools } from "zreact/dist/devtools";
import MainRouter from "./router";
// import BookLayout from "./book-layout";
import "./css/main.styl";
import "./css/base.css";
import "font-awesome/css/font-awesome.min.css";

render(<MainRouter/>, document.getElementById("main"));
// initDevTools();
