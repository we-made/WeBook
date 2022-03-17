export const _FC_EVENT = Symbol('EVENT');
export const _NATIVE_ARRANGEMENT = Symbol("NATIVE_ARRANGEMENT");

export class FullCalendarEvent {
    constructor ({title,
                 start,
                 end,
                 color="",
                 classNames=[],
                 extendedProps={}} = {}) 
    {
        this.title = title;
        this.start = start;
        this.end = end;
        this.color = color;
        this.classNames = classNames;
        this.extendedProps = extendedProps;
    }
}

export class FullCalendarResource {
    constructor () {
        
    }
}

export class CalendarDataStore {
    _refresh()  {}
    _flush()    {}
    get()       {}
    getAll()    {}
    remove()    {}
}


export class LocationStore {
    constructor (calendarBase) {
        this._store = new Map();
        this._refreshStore();
        this._calendar = calendarBase;
    }

    _refreshStore(start, end) {
        this._flushStore();
        return fetch("/arrangement/location/calendar_resources")
            .then(response => response.json())
            .then(obj => { obj.forEach((location) => {
                this._store.set(location.slug, location);
            })});
    }

    _flushStore() {
        this._store = new Map();
    }

    getAll() {
        var resources = Array.from(this._store.values());
        console.log(resources);
        return resources;
    }
}

/**
 * Stores, fetches, and provides an easy interface from which to retrieve arrangements
 */
export class ArrangementStore {
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
        let slugClass = writeSlugClass(arrangement.slug);
        return new FullCalendarEvent({
            title: arrangement.name,
            start: arrangement.starts,
            end: arrangement.ends,
            color: _this.plannerCalendar._getColorProvider().getColor(arrangement),
            classNames: [ slugClass ],
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

    /**
     * Get all arrangements in the form designated by get_as param.
     * @param {*} param0 
     * @returns An array of arrangements, whose form depends on get_as param.
     */
    get_all({ get_as } = {}) {
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

export class FullCalendarBased {

    constructor () {
    }

    _findSlugFromEl(el) { 
        var slug = undefined;

        el.classList.forEach((classToEvaluate) => {
            var classSplit = classToEvaluate.split(":");
        
            if (classSplit.length > 1 && classSplit[0] == "slug") {
                slug = classSplit[1];
            }
        });

        if (slug === undefined) {
            console.error("Element does not have a valid slug.")
            console.error(el);
            return undefined;
        }

        return slug;
    }

    refresh() { 
        this.init();
    }

    teardown() { }
    init() { }

}

export function writeSlugClass(slug) {
    return `slug:${slug}`;
}