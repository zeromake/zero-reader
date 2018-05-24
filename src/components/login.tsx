import { h, Component, Link } from "react-import";

class LoginView extends Component<any, any> {
    constructor(p: any, c: any) {
        super(p, c);
        this.state = {
            form: {
                password: "",
                account: "",
                rememberme: false,
            },
        };
    }
}
