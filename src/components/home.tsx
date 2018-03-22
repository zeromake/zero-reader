import { h, Component, findDOMNode, route } from "react-import";
import styl from "@/css/login.styl";
import { $ajax } from "../http/index";
import { bindUpdateForm, IFormProps } from "../utils";
import AlertZero from "./alert-zero";
import LoginForm from "@/../form/login.json";
import RegisterForm from "@/../form/register.json";

interface ILoginProps {
    matches: {[name: string]: string};
}
interface ILoginState {
    verifyImgUrl: string;
    isLogin: boolean;
    form?: {
        password: string;
        account: string;
        rememberme: boolean;
        // verify: string;
    };
    message: string | null;
}
enum Matche {
    ERROR = "error",
    HREF = "href",
}
const verifyImgUrl = "/api/verify_code";

export default class Home extends Component<ILoginProps, ILoginState> {
    private bindUpdateForm: (attrName: string) => IFormProps;
    private bindUpdateRegisterForm: (attrName: string) => IFormProps;
    private $alert: null | any;
    constructor(props, content) {
        super(props, content);
        this.state = {
            verifyImgUrl: verifyImgUrl + "?_=" + new Date().getTime(),
            isLogin: true,
            form: {
                password: "",
                account: "",
                rememberme: false,
                // verify: "",
            },
            message: null,
        };
        this.refreshCode = this.refreshCode.bind(this);
        this.switch = this.switch.bind(this);
        this.bindUpdateForm = bindUpdateForm(this, LoginForm, "form", true);
        this.bindUpdateRegisterForm = bindUpdateForm(this, RegisterForm, "form", true);
        this.submitEvent = this.submitEvent.bind(this);
        this.$alert = null;
        if (props && props.matches && props.matches[Matche.ERROR]) {
            const message = props.matches[Matche.ERROR];
            // console.warn("route to login page is error: ", message);
            this.togglerAlert(message);
        }
    }
    private refreshCode() {
        this.setState({
            verifyImgUrl: verifyImgUrl + "?_=" + new Date().getTime(),
        });
    }
    private submitEvent(e: Event) {
        e.preventDefault();
        if (this.state.isLogin) {
            this.login();
        } else {
            this.register();
        }
    }

    private async login() {
        let jsonObj: any = null;
        let res: void | Response = null;
        try {
            res = await $ajax.post("/api/login", this.state.form);
            jsonObj = res && await res.json();
        } catch (e) {
            // console.error(e);
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

    private async register() {
        const res = await $ajax.post("/api/sign_up", this.state.form);
        const jsonObj = res && await res.json();
        this.togglerAlert(jsonObj.message);
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

    public renderBase(bindUpdateFormObj: (attrName: string) => IFormProps) {
        return [
            <div className={styl.form_item} key="1">
                <input className={styl.input} autofocus={true} {...bindUpdateFormObj("account")}/>
            </div>,
            <div className={styl.form_item} key="2">
                <input className={styl.input} {...bindUpdateFormObj("password")}/>
            </div>,
        ];
    }

    public renderRegister() {
        const bindUpdateFormObj: (attrName: string) => IFormProps = this.bindUpdateRegisterForm;
        return [
            <div className={styl.form_item} key="6">
                <input className={styl.input} {...bindUpdateFormObj("re_password")}/>
            </div>,
            <div className={styl.form_item} key="7">
                <input className={styl.input} {...bindUpdateFormObj("role_name")}/>
            </div>,
            <div className={styl.form_item} key="8">
                <input className={styl.input} {...bindUpdateFormObj("code")}/>
            </div>,
            <div className={styl.form_item} key="9">
                <input className={styl.input} {...bindUpdateFormObj("email")}/>
            </div>,
        ];
    }

    private switch(isLogin: boolean) {
        this.setState({isLogin: !isLogin});
    }

    public render() {
        const isLogin: boolean = this.state.isLogin;
        const bindUpdateFormObj = isLogin ? this.bindUpdateForm : this.bindUpdateRegisterForm;
        return (
            <div className={styl.content + " animated"}>
                { h(AlertZero, {ref: (c: any) => this.$alert = c, message: this.state.message, level: 1}) }
                <div className={styl.form}>
                    <form action="post" onSubmit={this.submitEvent}>
                    <div className={styl.title} key="title">
                        <h1>{isLogin ? "登录" : "注册"}</h1>
                    </div>
                    {...this.renderBase(bindUpdateFormObj)}
                    { isLogin ? <div className={styl.form_item + " " + styl.form_item_back} key="3">
                        <div className={styl.rememberme}>
                            <input id="rememberme" {...bindUpdateFormObj("rememberme")} className={styl.rememberme_check}/>
                            <label for="rememberme" className={styl.rememberme_label}>记住我</label>
                        </div>
                        <div className={styl.back}>
                            <a href="javascript:void(0);">忘记密码</a>
                        </div>
                    </div> : this.renderRegister()}
                    <div className={styl.form_item} key="4">
                        <button className={styl.button} type="submit">{isLogin ? "登录" : "注册"}</button>
                    </div>
                    <div className={styl.form_item} key="5">
                        <a href="javascript:void(0);" onClick={this.switch}>{isLogin ? "注册" : "登录"}</a>
                    </div>
                    </form>
                </div>
            </div>
        );
    }
}
