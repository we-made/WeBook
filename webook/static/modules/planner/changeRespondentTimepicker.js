/**
 * changeRespondentTimepicker.js
 * 
 * A "supercharged" version of the MDBOOTSTRAP timepicker, with the added functionality of re-initializing 
 * the timepicker should the value of the input be updated
 */

export class ChangeRespondentTimepicker {
    constructor({ pickerWrapperElement, inputElement, mdbTimepickerOptions} = {}) {
        this.pickerWrapperElement = pickerWrapperElement;
        this.inputElement = inputElement;
        this.mdbTimepickerOptions = mdbTimepickerOptions;

        this.#listenForInputElementUpdate();
        this.#mdbInit();
    }

    /**
     * Add event listener to the timepickers input element, and on change
     * re-initialize the timepicker.
     */
    #listenForInputElementUpdate() {
        $(this.inputElement).on('change', (event) => {
            this.#mdbInit();
        })
    }

    /**
     * Initialize the mdbootstrap timepicker
     */
    #mdbInit() {
        this.mdbTimepicker = new mdb.Timepicker(this.pickerWrapperElement, this.mdbTimepickerOptions);
    }
}