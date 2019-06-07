import { createElement as h, Component } from "react";

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
interface IAdmin {
    account: string;
    email: string;
    password: string;
    re_password: string;
}

interface IProject {
    sign_up: boolean;
    sign_up_code: boolean;
    admin: IAdmin;
}

interface IInstallConfig {
    db: DbSelect;
    dbConfig: string | IDbConfig;
    project: IProject;
}

enum PageEnum {
    DB = 0,
    ENV = 1,
    PROJECT = 2,
}

interface IInstallState {
    page: PageEnum;
    installConfig: IInstallConfig;
}

export default class Install extends Component<any, IInstallState> {
    constructor(p, c) {
        super(p, c);
        this.state = {
            page: PageEnum.DB,
            installConfig: {
                db: DbSelect.sqlite,
                dbConfig: "sqlite.db",
                project: {
                    sign_up: true,
                    sign_up_code: false,
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
        return null;
    }
}
