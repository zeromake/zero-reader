import { h, Component, findDOMNode, route } from "react-import";
import styl from "@/css/login.styl";
import { $ajax } from "../http/index";
import { bindUpdateForm } from "../utils";
import AlertZero from "./alert-zero";

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
    private bindUpdateForm: (attrName: string) => (e: any) => void;
    private $alert: null | AlertZero;
    constructor(props, content) {
        super(props, content);
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
        this.bindUpdateForm = bindUpdateForm(this, "form");
        this.login = this.login.bind(this);
        this.$alert = null;
        if (props && props.matches && props.matches[Matche.ERROR]) {
            this.togglerAlert(props.matches[Matche.ERROR]);
        }
    }
    private refreshCode() {
        this.setState({
            verifyImgUrl: verifyImgUrl + "?_=" + new Date().getTime(),
        });
    }
    private async login() {
        const res = await $ajax.post("/api/login", this.state.form);
        const jsonObj = res && await res.json();
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
                <AlertZero ref={(c: AlertZero) => this.$alert = c} message={this.state.message} level={1}/>
                <div className={styl.form}>
                    <div className={styl.title}>
                        <h1>登录</h1>
                    </div>
                    {/* {
                        this.props && this.props.matches && this.props.matches[Matche.ERROR] ? <div>
                            <span style={{color: "red"}}>{this.props.matches[Matche.ERROR]}</span>
                        </div> : null
                    } */}
                    <div className={styl.form_item}>
                        <input className={styl.input} type="text" name="account" placeholder="用户" onChange={this.bindUpdateForm("account")} required={true}/>
                    </div>
                    <div className={styl.form_item}>
                        <input className={styl.input} type="password" name="password" placeholder="密码" onChange={this.bindUpdateForm("password")} required={true}/>
                    </div>
                    {/* <div className={styl.form_item}>
                        <div className={styl.verify_input}>
                            <input className={styl.input} type="text" name="verify" placeholder="验证码" onChange={this.bindUpdateForm("verify")} required={true}/>
                        </div>
                        <div className={styl.verify_img}>
                            <img src={this.state.verifyImgUrl} alt="点击刷新" title="点击刷新" onClick={this.refreshCode}/>
                        </div>
                    </div> */}
                    <div className={styl.form_item}>
                        <div className={styl.button_item}>
                            <button className={styl.button} type="submit" onClick={this.login}>登录</button>
                        </div>
                        <div className={styl.button_void}></div>
                        <div className={styl.button_item}>
                            <button className={styl.button} type="submit">注册</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}
