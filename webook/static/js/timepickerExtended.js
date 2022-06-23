
/**
 * Extension class to wrap around the mdb timepicker and inject our own functionality
 */
export class ExtendedTimepicker {
    constructor({ timepickerWrapperElement, timepickerInputElement, mdbOptions } = {}) {
        this.timepickerWrapperElement = timepickerWrapperElement;
        this.timepickerInputElement = timepickerInputElement;
        this.mdbOptions = mdbOptions;

        this.#mdbInit();
        this.#listenForInputChange();
    }

    /**
     * Initialize the mdb timepicker
     */
    #mdbInit() {
        this.mdbTimepickerInstance = new mdb.Timepicker(this.timepickerWrapperElement, this.mdbOptions);
    }

    /**
     * Listen for the input event to be triggered on the timepickers input element, 
     * meaning that the user has added or removed from the input.
     */
    #listenForInputChange() {
        $(this.timepickerInputElement).on('input', (event) => {
            if (event.currentTarget.value.length === 4 && /^[0-9]+$/.test(event.currentTarget.value.length)) {
                /**
                 * Add a : character in between when we have 4 characters, and all the characters are digits.
                 * So you could type 1500 and it would automatically be converted to 15:00.
                 */
                $(event.currentTarget)
                    .val([event.currentTarget.value.slice(0, 2), ":", event.currentTarget.value.slice(2,4)].join(''))
                    .change();
            }
        })
    }
}