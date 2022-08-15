/* Project specific Javascript goes here. */

$.widget("ui.dialog", $.extend({}, $.ui.dialog.prototype, {
    _title: function(title) {
        if (!this.options.title ) {
            title.html("&#160;");
        } else {
            title.html(this.options.title);
        }
    }
}));

function Utils() {
}

Utils.prototype = {
    constructor: Utils,
    isElementInView: function (element, fullyInView) {
        let pageTop = $(window).scrollTop();
        let pageBottom = pageTop + $(window).height();
        let elementTop = $(element).offset().top;
        let elementBottom = elementTop + $(element).height();

        if (fullyInView === true) {
            return ((pageTop < elementTop) && (pageBottom > elementBottom));
        } else {
            return ((elementTop <= pageBottom) && (elementBottom >= pageTop));
        }
    },
    /**
     * Split a string formatted like a valid date ( with a T in the middle ) into an array of 
     * date value and time value.
     * @param {*} strToDateSplit 
     * @returns Array
     */
    splitStrDate(strToDateSplit) {
        if (!(strToDateSplit instanceof String)) {
            throw "Received strToDateSplit is not a string", strToDateSplit;
        }
        if (!strToDateSplit) {
            throw "strToDateSplit is not a valid value", strToDateSplit;
        }
        
        let date_str = strToDateSplit.split("T")[0];
        let time_str = new Date(strToDateSplit).toTimeString().split(' ')[0];

        return [ date_str, time_str ];
    },

    splitDateIntoDateAndTimeStrings(dateToSplit) {
        let str = dateToSplit.toISOString();
        let date_str = str.split("T")[0];
        let time_str = new Date(str).toTimeString().split(' ')[0];
        return [ date_str, time_str ];
    },

    convertObjToFormData(obj, convertArraysToList=false) {
        let formData = new FormData();
    
        for (let key in obj) {
            if (convertArraysToList === true && Array.isArray(obj[key])) {
                appendArrayToFormData(obj[key], formData, key)
                continue;
            }
    
            if (obj[key] instanceof Date) {
                formData.append(key, obj[key].toISOString());
                continue;
            }
    
            formData.append(key, obj[key]);
        }
        
        return formData;
    },
}

window.Utils = new Utils();