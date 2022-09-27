/**
 * showIfSelectedPlugin.js
 * A simple plugin for dialogs adding functionality to show a field if predetermined checkboxes are checked.
 * This is used primarily for the display layout text functionality, where we only want to show the display layout
 * field should one of the display layouts that allow for display text be selected.
 */

class DialogShowIfSelectedPlugin extends DialogPluginBase {
    constructor(dialog, args) {
        super(dialog, args);

        this.checkboxes = dialog.querySelectorAll(this.checkboxesSelector);

        this._do(); //respect initial state

        dialog.$(this.checkboxesSelector).on('click change', (event) => {
            this._do();
        })
    }

    /**
     * Returns either true or false indicating if the checkboxes are selected in such a manner
     * that the given element is visible
     */
    isInShowState() {
        return this._do();
    }

    _do() {
        let show = false;
        for (let i = 0; i < this.checkboxes.length; i++) {
            const checkbox = this.checkboxes[i];
            if (checkbox.checked && this.showIfAnyOfTheseValuesMap.get(checkbox.value)) {
                show = true;
                break;
            }
        }

        if (show)
            this.elementToShowOrHide.style = "display: block;";
        else
            this.elementToShowOrHide.style = "display: none;";

        return show;
    }
}