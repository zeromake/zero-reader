import { h, Component, Link } from "react-import";
import LoginForm from "../../form/login.json";
import { bindUpdateForm, IFormProps } from "../utils";
import { $ajax } from "../http/index";
import styl from "../css/login.styl";
import Button from "./button";
import { Alert } from "./notification/index";
// import { FormEvent } from "react";

enum Matche {
    ERROR = "error",
    HREF = "href",
}

const AlertKey = "login_alert";

export default class LoginView extends Component<any, any> {
    private bindUpdateForm: (attrName: string) => IFormProps;
    public refs: any;
    constructor(p: any, c: any) {
        super(p, c);
        this.state = {
            form: {
                password: "",
                account: "",
                rememberme: false,
            },
        };
        const params: URLSearchParams = p.location.searchParams;
        if (params && params.has(Matche.ERROR)) {
            Alert.error({
                content: params.get(Matche.ERROR),
                // type: "error",
                duration: 0,
                key: AlertKey,
            });
        }
        this.bindUpdateForm = bindUpdateForm(this, LoginForm, "form", true);
        this.loginEvent = this.loginEvent.bind(this);
    }
    private loginEvent(e: any) {
        e.preventDefault();
        this.login();
    }
    private async login() {
        let jsonObj: any = null;
        let res: void | Response = null;
        try {
            res = await $ajax.post("/api/login", this.state.form);
            jsonObj = res && await res.json();
        } catch (e) {
            Alert.error((res && res.statusText) + ": " + e.message, 0, null, AlertKey);
            return;
        }
        if (jsonObj && jsonObj.status === 200) {
            for (const name in jsonObj.data) {
                localStorage.setItem(name, jsonObj.data[name]);
            }
            const params: URLSearchParams = this.props.location.searchParams;
            const url = (params && params.has(Matche.HREF) && params.get(Matche.HREF)) || "/librarys";
            Alert.success("登录成功!");
            this.props.navigate(url);
        } else {
            Alert.error(jsonObj.message, 0, null, AlertKey);
        }
    }

    public render() {
        return <div className={styl.form}>
            <form action="post" onSubmit={this.loginEvent}>
            <div className={styl.title} key="title">
                <h1>登录</h1>
            </div>
            <div className={styl.form_item} key="1">
                <input className={styl.input} autofocus={true} {...this.bindUpdateForm("account")}/>
            </div>
            <div className={styl.form_item} key="2">
                <input className={styl.input} {...this.bindUpdateForm("password")}/>
            </div>
            <div className={styl.form_item + " " + styl.form_item_back} key="3">
                <div className={styl.rememberme}>
                    <input id="rememberme" {...this.bindUpdateForm("rememberme")} className={styl.rememberme_check}/>
                    <label for="rememberme" className={styl.rememberme_label}>记住我</label>
                </div>
                <div className={styl.back}>
                    <Link href="/home/forgotpwd">忘记密码</Link>
                </div>
            </div>
            <div className={styl.form_item} key="4">
                <Button appearance="primary" block type="submit">登录</Button>
            </div>
            <div className={styl.form_item} key="5">
                <Link href="/home/register">注册</Link>
            </div>
            </form>
        </div>;
    }
}
