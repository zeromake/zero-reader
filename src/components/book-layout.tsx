import PdfLayout from "./pdf-layout";
import EpubLayout from "./epub-layout";
import { h, Component } from "react-import";
import { libraryData } from "@/http/index";
import { IAbcMeta } from "../types/index";

const bookLayout = {
    pdf: PdfLayout,
    epub: EpubLayout,
};

export default class BookLayout extends Component<any, any> {
    private baseUrl: string;
    private library: any;
    constructor(p, c) {
        super(p, c);
        this.library = libraryData(p.sha);
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
        if (this.state.layoutType) {
            const selectLayout: any = bookLayout[this.state.layoutType];
            if (selectLayout) {
                return h(selectLayout, { meta: this.state.meta, library: this.library, ...this.props });
            }
        }
    }
}
