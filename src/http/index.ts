export function get_json(url: string) {
    return fetch(url).then((res: Response) => res.json());
}
export function get_text(url: string) {
    return fetch(url).then((res: Response) => res.text());
}
