import BookLayout from "./components/book-layout";
import Library from "./components/library";
import Home from "./components/home";
import LoginView from "~/components/login";
import RegisterView from "~/components/register";
import { h, Router, Route, Link, Component, Redirect } from "react-import";
import Animate from "preact-animate";
import { togglerFullScreen } from "./utils";
// import AsyncRoute from "./assets/router/async-route";
// import createHashHistory from "history/createHashHistory";
// import { Alert } from "rsuite-notification";

// let tmpHistory = null;
// if (process.env.platform === "cordova") {
//     // const createHashHistory = require("history/createHashHistory").default;
//     tmpHistory = createHashHistory();
// }

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

// const text = (props) => {
//     return <h1>Text</h1>;
// };

// class Redirect extends Component<any, any> {
//     public componentDidMount() {
//         setTimeout(() => {
//             if (this.props.to) {
//                 route(this.props.to, true);
//             }
//         });
//     }
//     public render() {
//         return null;
//     }
// }

const MainRouter = () => (
    <Router
        // redirect={{"/": "/login"}}
        // beforeEach={(to: string, form: string, next: (url?: string) => boolean) => {
        //     const raw = to;
        //     if (to.lastIndexOf("?") !== -1) {
        //         to = to.split("?")[0];
        //     }
        //     if (to.startsWith("/library")) {
        //         const token = localStorage.getItem("token");
        //         if (token && token !== "") {
        //             next();
        //         } else {
        //             next(`/login?href=${encodeURIComponent(raw)}&error=未登录!`);
        //         }
        //     } else {
        //         next();
        //     }
        // }}
    >
        <Animate
            component="div"
            componentProps={{className: "reader-main"}}
            onAfterEnter={onAfterEnter}
            transitionEnter={true}
            transitionLeave={true}
            transitionName={{ enter: "fadeIn", leave: "fadeOut" }}
            isRender={false}
            >
            <Redirect
                key="redirect"
                from="/"
                to="/login"
                noThrow={true}
            />
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
                    component={RegisterView}
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
                    return (<div>
                        <h3>404</h3>
                        <Link href="/">回到首页</Link>
                    </div>);
                }}
                default={true}
            >
            </Route>
        </Animate>
    </Router>
);
export default MainRouter;
