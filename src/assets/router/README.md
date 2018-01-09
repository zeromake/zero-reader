# preact-router

copy from [preact-router](https://github.com/developit/preact-router)

## add support

1. animate support([preact-animate](https://github.com/zeromake/preact-animate))

``` jsx
import Animate from "preact-animate";
import Router, {Route} from "preact-router";
function RootRouter() {
    return <Router>
        <Animate
            component="div"
            componentProps={{className: "main"}}
            >
            <Route
                key="1"
                component={() => <h1>Home</h1>}
                path="/"
                transitionName={{ enter: "fadeInLeft", leave: "fadeOutLeft" }}
            ></Route>
            <Route
                key="1"
                component={() => <h1>Test</h1>}
                path="/test"
                transitionName={{ enter: "fadeInRight", leave: "fadeOutRight" }}
            ></Route>
        </Animate>
    </Router>;
}
```
2. child route support
3. react support