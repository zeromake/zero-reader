import { h, Component } from "zreact";
import styl from "@/css/library.styl";
import { Link } from "preact-router";

export default class Library extends Component<any, any> {
    constructor(p, c) {
        super(p, c);
        this.state = {
            library: [],
        };
    }
    public componentDidMount() {
        fetch("library/db.json").then((res) => res.json()).then((data: any) => {
            this.setState({ library: data });
        });
    }
    public render(props: any, state: any) {
        return (
            <div class={styl.library}>
                {
                    state.library.map((book) => {
                        return (
                            <div class={styl.center_book}>
                                <Link href={"/library/" + book.sha + "/"}>
                                <div class={styl.book_image}>
                                    <img src={"/library/" + book.sha + "/img/bg1.png"} alt={book.title} title={book.title}/>
                                </div>
                                </Link>
                                {book.title}
                            </div>
                        );
                    })
                }
            </div>
        );
    }
}
