import BookLayout from "@/components/book-layout";
import Library from "@/components/library";
import { h, Router, Route } from "react-import";
import Animate from "preact-animate";
import { togglerFullScreen } from "./utils";
// import AsyncRoute from "./assets/router/async-route";
import createHashHistory from "history/createHashHistory";

let tmpHistory = null;
if (process.env.platform === "cordova") {
    // const createHashHistory = require("history/createHashHistory").default;
    tmpHistory = createHashHistory();
}

// const Library = () => import("./components/library").then((modul) => modul.default);

// const BookLayout = () => import("./components/book-layout").then((modul) => modul.default);
let onAfterEnter = null;
if (process.env.platform === "cordova") {
    onAfterEnter = function _(component) {
        if (component && component.props) {
            let flag = null;
            if (component.props.rawKey === "2") {
                flag = false;
            } else if (component.props.rawKey === "1") {
                flag = true;
            }
            requestAnimationFrame(() => togglerFullScreen(flag));
        }
    };
}

const text = (props) => {
    return <h1>Text</h1>;
};

const MainRouter = () => (
    <Router history={tmpHistory}>
        <Animate
            component="div"
            componentProps={{className: "main"}}
            onAfterEnter={onAfterEnter}
            >
            <Route
                key="1"
                component={Library}
                path="/"
                transitionName={{ enter: "fadeInLeft", leave: "fadeOutLeft" }}
            >
            </Route>
            <Route
                key="2"
                component={BookLayout}
                path="/library/:sha/"
                transitionName={{ enter: "fadeInRight", leave: "fadeOutRight" }}
            >
                <div>loading!</div>
            </Route>
        </Animate>
    </Router>
);
export default MainRouter;
