import BookLayout from "./components/book-layout";
import Library from "./components/library";
import Home from "./components/home";
import LoginView from "~/components/login";
import RegisterView from "~/components/register";
import { h, Router, Route, Link, Component, Redirect, LocationProvider, Location } from "react-import";
import Animate from "preact-animate";
import { togglerFullScreen } from "./utils";
import { history } from "router-history";

import { rawVerifyToken } from "./http/index";
// import AsyncRoute from "./assets/router/async-route";
// import createHashHistory from "history/createHashHistory";
// import { Alert } from "rsuite-notification";

// const source = createHashSource();
// const tmpHistory = createHistory(source);
// if (process.env.platform === "cordova") {
//     // const createHashHistory = require("history/createHashHistory").default;
//     tmpHistory = createHashHistory();
// }

// const Library = () => import("@/components/library").then((modul) => modul.default);
// const BookLayout = () => import("@/components/book-layout").then((modul) => modul.default);
// const Login = () => import("@/components/login").then((modul) => modul.default);

// let onAfterEnter = null;
// if (process.env.platform === "cordova") {
//     onAfterEnter = function _(component) {
//         if (component && component.props) {
//             let flag = true;
//             if (component.props.rawKey !== "3") {
//                 flag = false;
//             }
//             requestAnimationFrame(() => togglerFullScreen(flag));
//         }
//     };
// }

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

const MainRouter = () => {
    const verifyToken = rawVerifyToken();
    const routes = [
        <Redirect
            key="redirect"
            from="/"
            to={verifyToken ? "/librarys" : "/home/login"}
            noThrow={true}
        />,
        <Route
            key="1"
            component={Home}
            path="/home"
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
            <Route
                key="1-3"
                component={() => {
                    return (<div>
                        <h3>404</h3>
                        <Link href="/">回到首页</Link>
                    </div>);
                }}
                default={true}
            >
            </Route>
        </Route>,
    ];
    if (verifyToken) {
        routes.push(
            <Route
                key="2"
                component={Library}
                path="/librarys"
            >
            </Route>,
            <Route
                key="3"
                component={BookLayout}
                path="/library/:base64"
            >
            </Route>,
        );
    }
    routes.push(
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
        </Route>,
    );
    return (
        <LocationProvider history={history}>
            <Router>
                <Animate
                    component="div"
                    componentProps={{className: "reader-main"}}
                    // onAfterEnter={onAfterEnter}
                    transitionEnter={true}
                    transitionLeave={true}
                    transitionName={{ enter: "fadeIn", leave: "fadeOut" }}
                    isRender={false}
                    >
                    {...routes}
                </Animate>
            </Router>;
        </LocationProvider>
    );
};
export default MainRouter;
