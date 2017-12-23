import BookLayout from "./components/book-layout";
import Library from "./components/library";
import { h, Router, Route } from "react-import";
import Animate from "preact-animate";

const MainRouter = () => (
    <Router>
        <Animate component="div" componentProps={{className: "main"}} transitionEnter={true} transitionLeave={true} transitionName={null}>
            <Route key="1" component={Library}  path="/" transitionName={{ enter: "fadeInLeft", leave: "fadeOutLeft" }}/>
            <Route key="2" component={BookLayout} path="/library/:sha/" transitionName={{ enter: "fadeInRight", leave: "fadeOutRight" }}/>
        </Animate>
    </Router>
);
export default MainRouter;
