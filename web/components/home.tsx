import { createElement as h, Component} from "react";
import styl from "../css/login.styl";
import Animate from "preact-animate";
// import Swal from "sweetalert2";
// import Button from "material-ui/Button";

export default class Home extends Component<any, any> {
    public render() {
        return (
            <div {...Animate.filterProps(this.props, {className: styl.content + " animated"})}>
                {this.props.children}
            </div>
        );
    }
}
