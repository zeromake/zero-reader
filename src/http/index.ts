/**
 * 获取json对象
 * @param url
 */
export function get_json(url: string) {
    return fetch(url).then((res: Response) => res.json());
}
/**
 * 获取文本
 * @param url
 */
export function get_text(url: string) {
    return fetch(url).then((res: Response) => res.text());
}
