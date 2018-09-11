import PdfLayout from "./pdf-layout";
import EpubLayout from "./epub-layout";
import { h, Component, Children } from "react-import";
import { libraryData } from "../http/index";
import { IAbcMeta } from "../types/index";
import styl from "../css/layout.styl";
import Animate from "preact-animate";

const bookLayout = {
    pdf: PdfLayout,
    epub: EpubLayout,
};

export default class BookLayout extends Component<any, any> {
    private baseUrl: string;
    private library: any;
    constructor(p, c) {
        super(p, c);
        this.library = libraryData(p.params.base64, p.location, p.navigate);
        this.state = {
            layoutType: null,
            meta: null,
        };
    }
    public componentDidMount() {
        return this.getMeta();
    }
    private async getMeta() {
        const meta = await this.library.json("meta.json");
        this.setState({
            layoutType: meta.type,
            meta,
        });
    }
    public render(): any {
        let layout: any = <div >loading!</div>;
        const newProps = Animate.filterProps(this.props, {className: `animated ${styl.animate_content}`});
        if (this.state.layoutType) {
            const selectLayout: any = bookLayout[this.state.layoutType];
            if (selectLayout) {
                layout = h(selectLayout, { ...this.props, meta: this.state.meta, library: this.library });
            }
        }
        // return <h1>loading</h1>;
        return <div {...newProps}>{layout}</div>;
    }
}
