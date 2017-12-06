import BookLayout from "./components/book-layout";
import Library from "./components/library";
// import { createElement as h } from "react";
// import { BrowserRouter as Router, Route} from "react-router-dom";
import { h, Router, Route } from "react-import";

const MainRouter = () => (
    <Router>
        <Route path="/" component={Library} />
        <Route component={BookLayout} path="/library/:sha/"/>
    </Router>
);
export default MainRouter;
