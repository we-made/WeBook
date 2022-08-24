
export default {
    /**
     * Close the current dialog
     */
    close(managerName, dialogName) {
        document.dispatchEvent(
            new CustomEvent(
                `${managerName}.closeDialog`,
                {
                    'detail': { 'dialog': dialogName }
                }
            )
        )
    },

    /**
     * Closes all dialogs on the manager of this dialog
     */
    closeAll(managerName) {
        document.dispatchEvent(
            new CustomEvent(
                `${managerName}.close`,
                {
                    'detail': {  }
                }
            )
        )
    },

    /**
     * Submit the current dialog
     */
    submit() {
        throw Error("NotImplemented")
    },
}