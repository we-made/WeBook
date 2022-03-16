import { FullCalendarEvent, FullCalendarResource } from "./commonLib";

_FC_EVENT = Symbol('EVENT')
_NATIVE_ARRANGEMENT = Symbol("NATIVE_ARRANGEMENT")


class PlannerCalendar {

    constructor( { calendarElement, eventsSrcUrl } = {}) {
        this._fcCalendar = undefined;
        this._calendarElement = calendarElement;
        this._eventsSrcUrl = eventsSrcUrl; /*"{% url 'arrangement:arrangement_events' %}"*/

        this._ARRANGEMENT_STORE = this.ArrangementStore();
        this._initCalendar();
    }

    /**
     * Stores, fetches, and provides an easy interface from which to retrieve arrangements
     */
    ArrangementStore = class ArrangementStore {
        constructor () {
            this._store = new Map();
            this._refreshStore();
        }

        /**
         * Refresh the store. 
         */
        _refreshStore(start, end) {
            this._flushStore();
            fetch(`/arrangement/planner?start=${start}&end=${end}`)
                .then(response => response.json())
                .then(obj => { obj.forEach((arrangement) => {
                    this._store.set(arrangement.slug, arrangement);
                })});
        }

        /**
         * Flush the store
         */
        _flushStore() {
            this._store = new Map();
        }

        /**
         * Converts a 'native' arrangement to a fullcalendar event
         * @param {*} arrangement 
         * @returns 
         */
        _mapArrangementToFullCalendarEvent(arrangement) {
            return new FullCalendarEvent({
                title: arrangement.name,
                start: arrangement.starts,
                end: arrangement.ends,
            })
        }

        /**
         * Get arrangement by the given slug
         * @param {*} slug 
         */
        get(slug, get_as) {
            if (this._store.has(slug) === false) {
                console.error(`Can not get arrangement with slug '${slug}' as slug is not known.`)
                return;
            }

            var arrangement = this._store.get(slug);

            if (get_as === _FC_EVENT) {
                return this._mapArrangementToFullCalendarEvent(arrangement);
            }
            else if (get_as === _NATIVE_ARRANGEMENT) {
                return arrangement;
            }
        }

        /**
         * Remove arrangement from the local store. Does not affect upstream.
         * @param {*} slug 
         */
        remove(slug) {
            if (this._store.has(slug)) {

            }
            else {
                console.error(`Can not remove arrangement with slug '${slug}', as slug is not known.`)
            }
        }
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
            events: (start, end, startStr, endStr, timezone) => {
                this._ARRANGEMENT_STORE._refreshStore(start, end);
            },
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