import { createHistory, createHashSource } from "zreact-router";

const source = createHashSource();
const history = createHistory(source);
export {
    history,
};
