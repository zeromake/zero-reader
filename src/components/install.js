"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
exports.__esModule = true;
var react_import_1 = require("react-import");
var DbSelect;
(function (DbSelect) {
    DbSelect["sqlite"] = "sqlite";
    DbSelect["mysql"] = "mysql";
    DbSelect["postgresql"] = "postgresql";
})(DbSelect || (DbSelect = {}));
var PageEnum;
(function (PageEnum) {
    PageEnum[PageEnum["DB"] = 0] = "DB";
    PageEnum[PageEnum["ENV"] = 1] = "ENV";
    PageEnum[PageEnum["PROJECT"] = 2] = "PROJECT";
})(PageEnum || (PageEnum = {}));
var Install = /** @class */ (function (_super) {
    __extends(Install, _super);
    function Install(p, c) {
        var _this = _super.call(this, p, c) || this;
        _this.state = {
            page: PageEnum.DB,
            installConfig: {
                db: DbSelect.sqlite,
                dbConfig: "sqlite.db",
                project: {
                    signUp: true,
                    signUpCode: false,
                    admin: {
                        account: "",
                        email: "",
                        password: "",
                        re_password: ""
                    }
                }
            }
        };
        return _this;
    }
    Install.prototype.envRender = function () {
        return React.createElement("div", null);
    };
    Install.prototype.DbRender = function () {
        return React.createElement("div", null);
    };
    Install.prototype.render = function () {
    };
    return Install;
}(react_import_1.Component));
exports["default"] = Install;
