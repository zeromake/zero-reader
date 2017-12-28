import { h, Component, Children } from "module-react";

class AsyncRoute extends Component<any, any> {
    constructor() {
        super();
        this.state = {
            componentData: null,
        };
    }
    private loadComponent() {
        if (this.props.component && this.props.component !== AsyncRoute) {
            return this.setState({
                componentData: this.props.component,
            });
        }
        const componentData = this.props.getComponent(this.props.url, ({component}) => {
        // Named param for making callback future proof
            if (component) {
                this.setState({
                    componentData: component,
                });
            }
        }, { ...this.props, ...this.props.matches });

        // In case returned value was a promise
        if (componentData && componentData.then) {
            // IIFE to check if a later ending promise was creating a race condition
            // Check test case for more info
            ((url) => {
                componentData.then((component) => {
                    if (url === this.props.url) {
                        this.setState({
                            componentData: component,
                        });
                    }
                });
            })(this.props.url);
        }
    }
    public componentDidMount() {
        this.loadComponent();
    }
    public componentWillReceiveProps(nextProps) {
        if (this.props.url && this.props.url !== nextProps.url) {
            this.setState({
                componentData: null,
            }, () => {
                this.loadComponent();
            });
        }
    }
    public render() {
        if (this.state.componentData) {
            return h(this.state.componentData, this.props);
        } else if (this.props.loading) {
            const loadingComponent = this.props.loading();
            return loadingComponent;
        } else {
            return Children.only(this.props.children);
        }
    }
}

export default AsyncRoute;
