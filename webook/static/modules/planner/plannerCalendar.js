

class PlannerCalendar {

    constructor( { calendarElement, eventsSrcUrl } = {}) {
        this._fcCalendar = undefined;
        this._calendarElement = calendarElement;
        this._eventsSrcUrl = eventsSrcUrl; /*"{% url 'arrangement:arrangement_events' %}"*/

        this._initCalendar();
    }

    /**
     * Find the slug value from the given element el
     * @param {*} el 
     * @returns A slug, or undefined if none was found
     */
    _findSlugFromEl(el) {
        var slug = undefined;

        el.classList.forEach((classToEvaluate) => {
            var classSplit = classToEvaluate.split(":");
        
            if (classSplit.length > 1 && classSplit[0] == "slug") {
                slug = classSplit[1];
            }
        });

        if (slug === undefined) {
            console.error("Tried to execute open method for arrangement but could not acquire slug.")
            return undefined;
        }

        return slug
    }

    /**
     * Bind popover with arrangement info to elementToBindWith
     * @param {*} elementToBindWith 
     */
    _bindPopover (elementToBindWith) {

        var info = {
            slug: this._findSlugFromEl(elementToBindWith)
        }

        new mdb.Popover(elementToBindWith, {
            trigger: "hover focus",
            content: `<h5>${info.slug}</h5>`,
            html: true,
        })
    }

    /**
     * First-time initialize the calendar
     */
    _initCalendar () {
        this._fcCalendar = new FullCalendar.Calendar(this._calendarElement, {
            initialView: 'dayGridMonth',
            events: this._eventsSrcUrl,
            eventContent: (arg) => {
                var icon_class = arg.event.extendedProps.icon;
                let html = `<span class="h6">
                                <span class='text-white ms-2'>
                                    <i class='${icon_class}'></i>
                                </span> 
                                ${arg.event.title}
                            </span>`
                return { html: html }
            },
            eventDidMount: (arg) => {
                this._bindPopover(arg.el)

                $.contextMenu({
                    className: "",
                    selector: ".fc-event",
                    items: {
                        open: {
                            name: "{% trans 'Open arrangement' %}",
                            isHtmlName: false,
                            callback: (key, opt) => {
                                location.href = "/arrangement/arrangement/" + this._findSlugFromEl(opt.$trigger[0]);
                            }
                        },
                    }
                });
            }
        });

        this._fcCalendar.render();
    }
}