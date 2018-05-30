import BookLayout from "./components/book-layout";
import Library from "./components/library";
import Home from "./components/home";
import LoginView from "~/components/login";
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
    <Router history={tmpHistory}
        redirect={{"/": "/login"}}
        beforeEach={(to: string, form: string, next: (url?: string) => boolean) => {
            const raw = to;
            if (to.lastIndexOf("?") !== -1) {
                to = to.split("?")[0];
            }
            if (to.startsWith("/library")) {
                const token = localStorage.getItem("token");
                if (token && token !== "") {
                    next();
                } else {
                    next(`/login?href=${encodeURIComponent(raw)}&error=未登录!`);
                }
            } else {
                next();
            }
        }}
    >
        <Animate
            component="div"
            componentProps={{className: "main", id: "app"}}
            onAfterEnter={onAfterEnter}
            transitionEnter={true}
            transitionLeave={true}
            transitionName={{ enter: "fadeIn", leave: "fadeOut" }}
            isRender={true}
            >
            <Route
                key="redirect"
                path="/"
                redirect="/login"
            >
            </Route>
            <Route
                key="1"
                component={Home}
                path="/"
            >
                <Route
                    key="1-1"
                    path="login"
                    component={LoginView}
                >
                </Route>
                <Route
                    key="1-2"
                    path="register"
                    component={() => {
                        return <h1>register</h1>;
                    }}
                >
                </Route>
            </Route>
            <Route
                key="2"
                component={Library}
                path="/library"
            >
            </Route>
            <Route
                key="3"
                component={BookLayout}
                path="/library/:base64/"
            >
            </Route>
            <Route
                key="4"
                component={() => {
                    return <div>
                        <h3>404</h3>
                        <Link href="/">回到首页</Link>
                    </div>;
                }}
                path="/*"
            >
            </Route>
        </Animate>
    </Router>
);
export default MainRouter;
