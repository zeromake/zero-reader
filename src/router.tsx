import BookLayout from "./components/book-layout";
import Library from "./components/library";
// import { createElement as h } from "react";
// import { BrowserRouter as Router, Route} from "react-router-dom";
import { h, Router, Route } from "react-import";
import Animate from "preact-animate";

const MainRouter = () => (
    <Router>
        <Animate
                component={null}
                transitionEnter={true}
                transitionLeave={true}
                transitionName= {{ enter: "fadeInLeft", leave: "fadeOutLeft" }}
            >
                <Route key="1" component={Library}  path="/"/>
                <Route key="2" component={BookLayout} path="/library/:sha/"/>
        </Animate>
    </Router>
);
export default MainRouter;
