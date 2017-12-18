import BookLayout from "./components/book-layout";
import Library from "./components/library";
// import { createElement as h } from "react";
// import { BrowserRouter as Router, Route} from "react-router-dom";
import { h, Router, Route } from "react-import";
import Animate from "preact-animate";

const MainRouter = () => (
    <Animate
                component={null}
                transitionEnter={true}
                transitionLeave={true}
                transitionName= {{ enter: "fadeInLeft", leave: "fadeOutLeft" }}
            >
        <Router>
                <Route path="/" component={Library} />
                <Route component={BookLayout} path="/library/:sha/"/>
        </Router>
    </Animate>
);
export default MainRouter;
