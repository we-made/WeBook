/**
 * Plugin for automatically syncing the values of the dialog data into the manager context
 */

class SyncDialogDataToManagerContextPlugin extends DialogPluginBase {
    constructor(dialog, args) {
        super(dialog, args);
        this._dialog = dialog;
        this._setProxy();
    }

    _setProxy() {
        let dialog = this._dialog;

        const handler = {
            set(target, prop, value) {
                document.dispatchEvent(new CustomEvent(
                    `${dialog.managerName}.dataUpdate`, {
                        detail: {
                            dialog: dialog.dialogId,
                            prop: prop,
                            propValue: value,
                        }
                    }
                ))

                return Reflect.set(...arguments);
            }
        }
        this._dialog._data = this.dialog.data;
        this._proxy = new Proxy(this._dialog._data, handler);
        this._dialog.data = this._proxy;
    }
}
