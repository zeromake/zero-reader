import { findDOMNode, h, route, Component } from "react-import";

enum DbSelect {
    sqlite = "sqlite",
    mysql = "mysql",
    postgresql = "postgresql",
}

interface IDbConfig {
    host: string;
    db: string;
    user: string;
    password: string;
    port: number;
}
interface Iadmin {
    account: string;
    email: string;
    password: string;
    re_password: string;
}

interface IProject {
    sign_up: boolean;
    sign_up_code: boolean;
    admin: Iadmin;
}

interface InstallConfig {
    db: DbSelect;
    dbConfig: string | IDbConfig;
    project: IProject;
}

enum PageEnum {
    DB = 0,
    ENV = 1,
    PROJECT = 2,
}

interface InstallState {
    page: PageEnum;
    installConfig: InstallConfig;
}

export default class Install extends Component<any, InstallState> {
    constructor(p, c) {
        super(p, c);
        this.state = {
            page: PageEnum.DB,
            installConfig: {
                db: DbSelect.sqlite,
                dbConfig: "sqlite.db",
                project: {
                    signUp: true,
                    signUpCode: false,
                    admin: {
                        account: "",
                        email: "",
                        password: "",
                        re_password: "",
                    },
                },
            },
        };
    }
    public envRender() {
        return <div></div>;
    }
    public DbRender() {
        return <div></div>;
    }
    public render() {

    }
}
