import { render, h } from "zreact";
import { initDevTools } from "zreact/dist/devtools";
import MainRouter from "./router";
// import BookLayout from "./book-layout";
import "./css/main.styl";

render(<MainRouter/>, document.body);

initDevTools();
