import { h, Component } from "module-react";
import { subscribers, getCurrentUrl, Link as StaticLink } from "./index";

export class Match extends Component<any, any> {
    public nextUrl: string;
    public static Link = null;
    public update = (url: string) => {
        this.nextUrl = url;
        this.setState({});
    }
    public componentDidMount() {
        subscribers.push(this.update);
    }
    public componentWillUnmount() {
        subscribers.splice(subscribers.indexOf(this.update) >>> 0, 1);
    }
    public render(props) {
        const url = this.nextUrl || getCurrentUrl();
        const path = url.replace(/\?.+$/, "");
        this.nextUrl = null;
        return props.children[0] && props.children[0]({
            url,
            path,
            matches: path === props.path,
        });
    }
}
export const Link = ({ activeClassName, path, ...props }) => (
    h(
        Match,
        { path: path || props.href },
        ({ matches }) => (
            h(
                StaticLink,
                {
                    ...props,
                    class: [
                        props.class || props.className,
                        matches && activeClassName,
                    ].filter(Boolean).join(" "),
                },
            )
        ),
    )
);
Match.Link = Link;

export default Match;
