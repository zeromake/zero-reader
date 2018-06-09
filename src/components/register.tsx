import { h, Component, Link, route } from "react-import";
import registerForm from "../../form/register.json";
import { bindUpdateForm, IFormProps } from "../utils";
import { $ajax } from "../http/index";
import styl from "../css/login.styl";
import Button from "./button";
// import { FormEvent } from "react";

declare const projectConfig: any;

enum Matche {
    ERROR = "error",
    HREF = "href",
}

export default class RegisterView extends Component<any, any> {
    private bindUpdateForm: (attrName: string) => IFormProps;
    public refs: any;
    constructor(p: any, c: any) {
        super(p, c);
        this.state = {
            form: {
                password: "",
                account: "",
            },
        };
        this.bindUpdateForm = bindUpdateForm(this, registerForm, "form", true);
        this.registerEvent = this.registerEvent.bind(this);
    }
    private registerEvent(e: any) {
        e.preventDefault();
        this.register();
    }
    private async register() {
        let jsonObj: any = null;
        let res: void | Response = null;
        try {
            res = await $ajax.post("/api/register", this.state.form);
            jsonObj = res && await res.json();
        } catch (e) {
            // console.error(e);
            // this.togglerAlert((res && res.statusText) + ": " + e.message);
            return;
        }
        if (jsonObj && jsonObj.status === 200) {
            route("/login");
        } else {
            // this.togglerAlert(jsonObj.message);
        }
    }

    public render() {
        return <div className={styl.form}>
            <form action="post" onSubmit={this.registerEvent}>
                <div className={styl.title} key="title">
                    <h1>注册</h1>
                </div>
                <div className={styl.form_item} key="1">
                    <input className={styl.input} autofocus={true} {...this.bindUpdateForm("account")}/>
                </div>
                <div className={styl.form_item} key="2">
                    <input className={styl.input} {...this.bindUpdateForm("password")}/>
                </div>
                <div className={styl.form_item} key="6">
                    <input className={styl.input} {...this.bindUpdateForm("re_password")}/>
                </div>
                <div className={styl.form_item} key="7">
                    <input className={styl.input} {...this.bindUpdateForm("role_name")}/>
                </div>
                { projectConfig!.sign_up_code ? <div className={styl.form_item} key="8">
                    <input className={styl.input} {...this.bindUpdateForm("code")}/>
                </div> : null }
                <div className={styl.form_item} key="9">
                    <input className={styl.input} {...this.bindUpdateForm("email")}/>
                </div>
                <div className={styl.form_item} key="4">
                    <Button appearance="primary" block type="submit">注册</Button>
                </div>
                <div className={styl.form_item} key="5">
                    <Link href="/login">登陆</Link>
                </div>
            </form>
        </div>;
    }
}
