import { h, Component, findDOMNode, route } from "react-import";
import styl from "@/css/login.styl";
import { $ajax } from "../http/index";
import { bindUpdateForm } from "../utils";
import AlertZero from "./alert-zero";
import LoginForm from "@/../form/login.json";

interface ILoginProps {
    matches: {[name: string]: string};
}
interface ILoginState {
    verifyImgUrl: string;
    form?: {
        password: string;
        account: string;
        // verify: string;
    };
    message: string | null;
}
enum Matche {
    ERROR = "error",
    HREF = "href",
}
const verifyImgUrl = "/api/verify_code";

export default class Login extends Component<ILoginProps, ILoginState> {
    private bindUpdateForm: (attrName: string) => {value: any, onChange: (e: any) => void};
    private $alert: null | any;
    constructor(props, content) {
        super(props, content);
        console.log(LoginForm);
        this.state = {
            verifyImgUrl: verifyImgUrl + "?_=" + new Date().getTime(),
            form: {
                password: "",
                account: "",
                // verify: "",
            },
            message: null,
        };
        this.refreshCode = this.refreshCode.bind(this);
        this.bindUpdateForm = bindUpdateForm(this, LoginForm, "form");
        this.login = this.login.bind(this);
        this.$alert = null;
        if (props && props.matches && props.matches[Matche.ERROR]) {
            const message = props.matches[Matche.ERROR];
            console.warn("route to login page is error: ", message);
            this.togglerAlert(message);
        }
    }
    private refreshCode() {
        this.setState({
            verifyImgUrl: verifyImgUrl + "?_=" + new Date().getTime(),
        });
    }
    private async login() {
        let jsonObj: any = null;
        let res: any = null;
        try {
            res = await $ajax.post("/api/login", this.state.form);
            jsonObj = res && await res.json();
        } catch (e) {
            console.error(e);
            this.togglerAlert((res && res.statusText) + ": " + e.message);
            return;
        }
        if (jsonObj && jsonObj.status === 200) {
            for (const name in jsonObj.data) {
                localStorage.setItem(name, jsonObj.data[name]);
            }
            const url = (this.props.matches && this.props.matches[Matche.HREF]) || "/library";
            route(url);
        } else {
            this.togglerAlert(jsonObj.message);
        }
    }

    public togglerAlert(message: string) {
        this.setState({message}, () => {
            if (this.$alert) {
                const show = this.$alert.isShow();
                this.$alert.toggler().then(() => {
                    if (show) {
                        this.$alert.toggler();
                    }
                });
            }
        });
    }
    public render() {
        return (
            <div className={styl.content + " bg animated"}>
                { h(AlertZero, {ref: (c: any) => this.$alert = c, message: this.state.message, level: 1}) }
                <div className={styl.form}>
                    <form action="post">
                    <div className={styl.title}>
                        <h1>登录</h1>
                    </div>
                    <div className={styl.form_item}>
                        <input className={styl.input} {...this.bindUpdateForm("account")}  onInvalid={console.log}/>
                    </div>
                    <div className={styl.form_item}>
                        <input className={styl.input} {...this.bindUpdateForm("password")}/>
                    </div>
                    <div className={styl.form_item}>
                        <div className={styl.button_item}>
                            <button className={styl.button} type="submit" onClick={this.login}>登录</button>
                        </div>
                        <div className={styl.button_void}></div>
                        <div className={styl.button_item}>
                            <button className={styl.button} type="submit">注册</button>
                        </div>
                    </div>
                    </form>
                </div>
            </div>
        );
    }
}
