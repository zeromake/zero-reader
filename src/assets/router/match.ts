import { h, Component } from "module-react";
import { subscribers, getCurrentUrl, Link as StaticLink } from "./index";

interface IMatchProps {
    path: string;
    render: (params: any) => any;
}

export class Match extends Component<IMatchProps, any> {
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
    public render() {
        const props = this.props;
        const url = this.nextUrl || getCurrentUrl();
        const path = url.replace(/\?.+$/, "");
        this.nextUrl = null;
        return props.render && props.render({
            url,
            path,
            matches: path === props.path,
        });
    }
}
export const Link = ({ activeClassName, path, ...props }) => (
    h(
        Match,
        { path: path || props.href, render: ({ matches }) => (
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
        )},
    )
);
Match.Link = Link;

export default Match;
