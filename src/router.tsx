import Router from "preact-router";
import BookLayout from "./book-layout";
import Library from "./components/library";
import { render, h } from "zreact";

const Home = (props: any) => (
    <div>
        <h1>主页1</h1>
        <nav>
            <a href="/library/d66d7f8982411628163d95ee978ad9166849e16072b67995309406c6cbcbba41">自制编译器</a>
        </nav>
    </div>
);

const MainRouter = () => (
    <Router>
        <Library  path="/"/>
        {h(BookLayout, {path : "/library/:sha/"})}
    </Router>
);
export default MainRouter;
