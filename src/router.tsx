import BookLayout from "@/components/book-layout";
import Library from "@/components/library";
import Home from "@/components/home";
import { h, Router, Route, Link, AsyncRoute } from "react-import";
import Animate from "preact-animate";
import { togglerFullScreen } from "./utils";
// import AsyncRoute from "./assets/router/async-route";
import createHashHistory from "history/createHashHistory";

let tmpHistory = null;
if (process.env.platform === "cordova") {
    // const createHashHistory = require("history/createHashHistory").default;
    tmpHistory = createHashHistory();
}

// const Library = () => import("@/components/library").then((modul) => modul.default);
// const BookLayout = () => import("@/components/book-layout").then((modul) => modul.default);
// const Login = () => import("@/components/login").then((modul) => modul.default);

let onAfterEnter = null;
if (process.env.platform === "cordova") {
    onAfterEnter = function _(component) {
        if (component && component.props) {
            let flag = true;
            if (component.props.rawKey !== "3") {
                flag = false;
            }
            requestAnimationFrame(() => togglerFullScreen(flag));
        }
    };
}

const text = (props) => {
    return <h1>Text</h1>;
};

const MainRouter = () => (
    <Router history={tmpHistory} beforeEach={(to: string, form: string, next: (url?: string) => boolean) => {
        const raw = to;
        if (to.lastIndexOf("?") !== -1) {
            to = to.split("?")[0];
        }
        if (to !== "/") {
            const token = localStorage.getItem("token");
            if (token && token !== "") {
                next();
            } else {
                next(`/?href=${encodeURIComponent(raw)}&error=未登录!`);
            }
        } else {
            next();
        }
    }}>
        <Animate
            component="div"
            componentProps={{className: "main"}}
            onAfterEnter={onAfterEnter}
            transitionEnter={true}
            transitionLeave={true}
            transitionName={{ enter: "fadeIn", leave: "fadeOut" }}
            >
            <Route
                key="1"
                // component={AsyncRoute}
                // getComponent={Login}
                component={Home}
                path="/"
                // transitionName={{ enter: "fadeInLeft", leave: "fadeOutLeft"  }}
            >
            </Route>
            <Route
                key="2"
                // component={AsyncRoute}
                // getComponent={Library}
                component={Library}
                path="/library"
                // transitionName={{ enter: "fadeInRight", leave: "fadeOutRight" }}
            >
            </Route>
            <Route
                key="3"
                // component={AsyncRoute}
                // getComponent={BookLayout}
                component={BookLayout}
                path="/library/:sha/"
                // transitionName={{ enter: "fadeInRight", leave: "fadeOutRight" }}
            >
            </Route>
        </Animate>
    </Router>
);
export default MainRouter;
