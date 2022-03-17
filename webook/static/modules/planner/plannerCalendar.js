import { FullCalendarEvent, FullCalendarResource } from "./commonLib.js";

var _FC_EVENT = Symbol('EVENT');
var _NATIVE_ARRANGEMENT = Symbol("NATIVE_ARRANGEMENT");


export class PlannerCalendar {

    constructor( { calendarElement, eventsSrcUrl, colorProviders=[], initialColorProvider="" } = {}) {
        this._fcCalendar = undefined;
        this._calendarElement = calendarElement;
        this._eventsSrcUrl = eventsSrcUrl; /*"{% url 'arrangement:arrangement_events' %}"*/

        this._colorProviders = new Map();
        this._colorProviders.set("DEFAULT", new this.StandardColorProvider())
        colorProviders.forEach( (bundle) => {
            this._colorProviders.set(bundle.key, bundle.provider)
        })
        this.activeColorProvider = initialColorProvider !== undefined && this._colorProviders.has(initialColorProvider) ? initialColorProvider : "DEFAULT";

        console.log(">> Active Color Provider: " + this.activeColorProvider)
        console.log(this._colorProviders)

        this._ARRANGEMENT_STORE = new this.ArrangementStore(this);
        this._initCalendar();
    }

    refresh() {
        this._initCalendar();
    }

    StandardColorProvider = class StandardColorProvider {
        getColor(arrangement) {
            return "green";
        }
    }

    setActiveColorProvider(key) {
        if (this._colorProviders.has(key)) {
            this.activeColorProvider = key;
        }
        else {
            console.error(`Color provider with the given key: '${this.key}' does not exist.`)
        }
    }

    _getColorProvider() {
        return this._colorProviders.get(this.activeColorProvider);
    }

    /**
     * Stores, fetches, and provides an easy interface from which to retrieve arrangements
     */
    ArrangementStore = class ArrangementStore {
        constructor (plannerCalendar) {
            this._store = new Map();
            this._refreshStore();
            this.plannerCalendar = plannerCalendar;
        }

        /**
         * Refreshes the store and returns this so you can chain in a get.
         */
        _refreshStore(start, end) {
            this._flushStore();
            return fetch(`/arrangement/planner/arrangements_in_period?start=${start}&end=${end}`)
                .then(response => response.json())
                .then(obj => { obj.forEach((arrangement) => {
                    console.log(arrangement)
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
            let _this = this;
            return new FullCalendarEvent({
                title: arrangement.name,
                start: arrangement.starts,
                end: arrangement.ends,
                color: _this.plannerCalendar._getColorProvider().getColor(arrangement),
                classNames: [ `slug:${arrangement.slug}` ],
                extendedProps: { 
                    icon: arrangement.audience_icon, 
                    starts: arrangement.starts, 
                    ends: arrangement.ends,
                    arrangementType: arrangement.arrangement_type
                },
            });
        }

        /**
         * Get arrangement by the given slug
         * @param {*} slug 
         */
        get({ slug, get_as } = {}) {
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

        get_all({ get_as } = {}) {
            console.log(this._store);
            var arrangements = Array.from(this._store.values());

            if (get_as === _FC_EVENT) {
                // var mappedEvents = arrangements.map( (arrangement) => { this._mapArrangementToFullCalendarEvent(arrangement) });
                var mappedEvents = [];
                arrangements.forEach( (arrangement) => {
                    mappedEvents.push( this._mapArrangementToFullCalendarEvent(arrangement) );
                });
                return mappedEvents;
            }
            else if (get_as === _NATIVE_ARRANGEMENT) {
                return arrangements;
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

        return slug;
    }

    /**
     * Bind popover with arrangement info to elementToBindWith
     * @param {*} elementToBindWith 
     */
    _bindPopover (elementToBindWith) {
        var slug = this._findSlugFromEl(elementToBindWith);        
        var arrangement = this._ARRANGEMENT_STORE.get({
            slug: slug,
            get_as: _NATIVE_ARRANGEMENT
        });

        new mdb.Popover(elementToBindWith, {
            trigger: "hover focus",
            content: `
                <span class='badge badge-lg badge-info'>
                    <i class='${arrangement.audience_icon}'></i>&nbsp;
                    ${arrangement.audience}
                </span>
                <span class='badge h6 badge-success'>
                    ${arrangement.mainPlannerName}
                </span>
                <h5 class='mb-0 mt-2'>${arrangement.name}</h5>
                <em class='small'>${arrangement.starts} - ${arrangement.ends}</em>
                `,
            html: true,
        })
    }

    /**
     * First-time initialize the calendar
     */
    async _initCalendar () {
        let _this = this;
        this._fcCalendar = new FullCalendar.Calendar(this._calendarElement, {
            initialView: 'dayGridMonth',
            events: async (start, end, startStr, endStr, timezone) => {
                var events = await _this._ARRANGEMENT_STORE._refreshStore(start, end)
                        .then(a => _this._ARRANGEMENT_STORE.get_all({ get_as: _FC_EVENT }));
                console.log(events);
                return events;
            },
            eventContent: (arg) => {
                var icon_class = arg.event.extendedProps.icon;
                let html = `<span class="h6"
                                    data-toggle='tooltip'
                                    title='Right click me to get options'>
  
                                <span class='text-white ms-2'>
                                    <i class='${icon_class}'></i>
                                </span>
                                <em class='small'>${arg.event.extendedProps.starts} - ${arg.event.extendedProps.ends}</em>
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
                            name: "Open",
                            isHtmlName: false,
                            callback: (key, opt) => {
                                location.href = "/arrangement/arrangement/" + this._findSlugFromEl(opt.$trigger[0]);
                            }
                        },
                        edit: {
                            name: "Edit",
                            isHtmlName: false,
                            callback: (key, opt) => {
                                location.href = "/arrangement/arrangement/edit/" + this._findSlugFromEl(opt.$trigger[0]);
                            }
                        },
                    }
                });
            }
        });

        this._fcCalendar.render();
    }
}