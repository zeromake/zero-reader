import { Component } from "react-import";
import { route } from "./index";

export default class Redirect extends Component<any, any> {
    // public settime: number;
    public shouldComponentUpdate(props: any, state: any): boolean {
        return true;
    }
    // public componentDidMount() {
    //     if (this.props.redirect) {
    //                 // console.log("redirect");
    //                 // Promise.resolve().then(() => {
    //         setTimeout(() => route(this.props.redirect));
    //     }
    // }
    public render() {
        return null;
    }
}
