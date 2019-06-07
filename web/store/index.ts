import { observable, action } from "mobx";

class OptionsStore {
    @observable
    public viewMode: number = 0;

    @action
    public setViewMode(mode: number) {
        this.viewMode = mode;
    }
}
