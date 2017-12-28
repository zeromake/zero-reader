import BookLayout from "./components/book-layout";
import Library from "./components/library";
import { h, Router, Route } from "react-import";
import Animate from "preact-animate";
// import AsyncRoute from "./assets/router/async-route";
// import createHashHistory from "history/createHashHistory";

let history = null;
if (process.env.platform === "cordova") {
    const createHashHistory = require("history/createHashHistory").default;
    history = createHashHistory();
}

// const Library = () => import("./components/library").then((modul) => modul.default);

// const BookLayout = () => import("./components/book-layout").then((modul) => modul.default);

const MainRouter = () => (
    <Router history={history}>
        <Animate component="div" componentProps={{className: "main"}} transitionEnter={true} transitionLeave={true} transitionName={null}>
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
