export const _FC_EVENT = Symbol('EVENT');
export const _FC_RESOURCE = Symbol("RESOURCE");
export const _NATIVE_ARRANGEMENT = Symbol("NATIVE_ARRANGEMENT");
export const _NATIVE_LOCATION = Symbol("NATIVE_LOCATION");
export const _NATIVE_PERSON = Symbol("NATIVE_PERSON");



/**
 * The standard calendar color provider
 */
export class StandardColorProvider {
    getColor(arrangement) {
        return "green";
    }
}

export class FullCalendarEvent {
    constructor ({title,
                 start,
                 end,
                 resourceIds=[],
                 color="",
                 display="",
                 textColor="",
                 classNames=[],
                 extendedProps={}} = {}) 
    {
        this.title = title;
        this.start = start;
        this.end = end;
        this.color = color;
        this.display = display;
        this.resourceIds = resourceIds;
        this.textColor = textColor;
        this.classNames = classNames;
        this.extendedProps = extendedProps;
    }
}

export class FullCalendarResource {
    constructor ({ title,
                   id,
                   slug,
                   parentId,
                   extendedProps,
                   children = []}) {
        this.title = title;
        this.id = id;
        this.parentId = parentId;
        this.extendedProps = extendedProps;
        this.extendedProps.slug = slug;
    }
}

export class CalendarDataStore {
    _refresh()  {}
    _flush()    {}
    get()       {}
    getAll()    {}
    remove()    {}
}


class BaseStore {
    constructor () {
        this._store = new Map();
    }
    _getStoreAsArray() {
        return Array.from(this._store.values());
    }
}

export class LocationStore extends BaseStore {
    constructor (calendarBase) {
        super();

        this._store = new Map();
        this._refreshStore();
        this._calendar = calendarBase;
    }

    async _refreshStore() {
        this._flushStore();
        return await fetch("/arrangement/location/calendar_resources")
            .then(response => response.json())
            .then(obj => { obj.forEach((location) => {
                this._store.set(location.slug, location);
            })});
    }

    _mapToFullCalendarResource (nativeLocation) {
        return new FullCalendarResource({
            title: nativeLocation.title,
            id: nativeLocation.id,
            slug: nativeLocation.slug,
            children: nativeLocation.children,
            parentId: nativeLocation.parentId,
            extendedProps: nativeLocation.extendedProps,
        });
    }

    _flushStore() {
        this._store = new Map();
    }
    
    getAll({ get_as } = {}) {
        var resources = this._getStoreAsArray();
        if (get_as === _FC_RESOURCE) {
            let fcResources = [];
            for (let i = 0; i < resources.length; i++) {
                fcResources.push(this._mapToFullCalendarResource(resources[i]));
            }
            return fcResources;
        }
        else if (get_as === _NATIVE_LOCATION) {
            return resources;
        }
    }
}

export class PersonStore extends BaseStore {
    constructor (calendarBase) {
        super();

        this._store = new Map();
        this._refreshStore();
        this._calendar = calendarBase;
    }

    async _refreshStore() {
        this._flushStore();
        return await fetch("/arrangement/person/calendar_resources")
            .then(response => response.json())
            .then(obj => { obj.forEach((person) => {
                this._store.set(person.slug, person);
            })});
    }

    _mapToFullCalendarResource (nativePerson) {
        return new FullCalendarResource({
            title: nativePerson.title,
            id: nativePerson.id,
            slug: nativePerson.slug,
            children: nativePerson.children,
            parentId: nativePerson.parentId,
            extendedProps: nativePerson.extendedProps,
        });
    }

    _flushStore() {
        this._store = new Map();
    }

    getAll({ get_as } = {}) {
        var resources = this._getStoreAsArray();
        if (get_as === _FC_RESOURCE) {
            let fcResources = [];
            for (let i = 0; i < resources.length; i++) {
                fcResources.push(this._mapToFullCalendarResource(resources[i]));
            }
            return fcResources;
        }
        else if (get_as === _NATIVE_LOCATION) {
            return resources;
        }
    }
}


/**
 * Stores, fetches, and provides an easy interface from which to retrieve arrangements
 */
export class ArrangementStore extends BaseStore {
    constructor (colorProvider) {
        super();

        this._store = new Map(); 
        this._refreshStore();
        this.colorProvider = colorProvider;
    }

    /**
     * Refreshes the store and returns this so you can chain in a get.
     */
    _refreshStore(time, end) {
        this._flushStore();

        var query_string = "";
        if (time !== undefined) {
            query_string = `?start=${time.startStr}&end=${time.endStr}`;
        }

        return fetch(`/arrangement/planner/arrangements_in_period${query_string}`)
            .then(response => response.json())
            .then(obj => { obj.forEach((arrangement) => {
                this._store.set(arrangement.event_pk, arrangement);
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
        let pkClass = "pk:" + arrangement.event_pk;
        return new FullCalendarEvent({
            title: arrangement.name,
            start: arrangement.starts,
            resourceIds: arrangement.slug_list,
            end: arrangement.ends,
            color: this.colorProvider.getColor(arrangement),
            classNames: [ slugClass, pkClass ],
            extendedProps: {
                location_name: arrangement.location,
                location_slug: arrangement.location_slug,
                icon: arrangement.audience_icon, 
                starts: arrangement.starts, 
                ends: arrangement.ends,
                arrangementType: arrangement.arrangement_type,
            },
        });
    }

    /**
     * Get arrangement by the given slug
     * @param {*} slug 
     */
    get({pk, get_as } = {}) {
        if (this._store.has(parseInt(pk)) === false) {
            console.error(`Can not get arrangement with pk '${pk}' as pk is not known.`)
            return;
        }

        var arrangement = this._store.get(parseInt(pk));
        
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
    get_all({ get_as, locations=undefined, arrangement_types=undefined, audience_types=undefined, filterSet=undefined } = {}) {
        var arrangements = this._getStoreAsArray();
        var filteredArrangements = [];

        var slugsConvert = filterSet.slugs.map( function (slug) { return { id: slug, name: "" } });

        var filterMap = new Map();
        if (slugsConvert !== undefined) {
            slugsConvert.forEach( (slug) => {
                filterMap.set(slug.id, true);
            } )
        }

        var arrangementTypesMap =   arrangement_types !== undefined && arrangement_types.length > 0 ? new Map(arrangement_types.map(i => [i, true])) : undefined;
        var audienceTypesMap =      audience_types !== undefined && audience_types.length > 0 ? new Map(audience_types.map(i => [i, true])) : undefined;

        arrangements.forEach ( (arrangement) => {
            var isWithinFilter =
                (arrangementTypesMap === undefined  || arrangementTypesMap.has(arrangement.arrangement_type_slug) === true) &&
                (audienceTypesMap === undefined     || audienceTypesMap.has(arrangement.audience_slug) === true)


            console.log(arrangement)

            if (filterSet.showOnlyEventsWithNoRooms === true && arrangement.room_names.length > 0 && arrangement.room_names[0] !== null) {
                isWithinFilter = false;
            }

            arrangement.slug_list.forEach( (slug) => {
                if (filterMap.has(slug) === true) {
                    isWithinFilter = false;
                }
            })

            if (isWithinFilter === true) {
                filteredArrangements.push(arrangement);
            }
        });
        
        arrangements = filteredArrangements;

        if (get_as === _FC_EVENT) {
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
            this._store.remove(slug);
        }
        else {
            console.error(`Can not remove arrangement with slug '${slug}', as slug is not known.`)
        }
    }
}

export class FullCalendarBased {
    constructor() {
        this._listenToRefreshEvents();
    }

    _listenToRefreshEvents() {
        document.addEventListener("plannerCalendar.refreshNeeded", async () => {
            await this.init();
            /* Remove all shown popovers, if we refresh the events without doing this we'll be "pulling the rug" up from under the popovers, 
            in so far as removing the elements they are anchored/bound to. In effect this puts the popover in a stuck state, in which it can't be hidden or
            removed without refresh. Hence we do this. */
            $(".popover").popover('hide');
        });
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
            console.error("Element does not have a valid slug.", el)
            return undefined;
        }

        return slug;
    }

    _findEventPkFromEl(el) {
        var pk = undefined;

        el.classList.forEach((classToEvaluate) => {
            var classSplit = classToEvaluate.split(":");
            if (classSplit.length > 1 && classSplit[0] == "pk") {
                pk = classSplit[1];
            }
        });

        if (pk === undefined) {
            console.error("Element does not have a valid pk.", el)
            return undefined;
        }

        return pk;
    }

    refresh() { 
        this.init();
    }

    /**
     * Get the FullCalendar calendar instance
     */
    getFcCalendar() { }
    teardown() { }
    async init() { }

}

export function writeSlugClass(slug) {
    return `slug:${slug}`;
}

/**
 * Append a given array to the given formData instance
 * @param {*Array} arrayToAppend 
 * @param {*FormData} formDataToAppendTo 
 * @param {*String} key
 */
export function appendArrayToFormData(arrayToAppend, formDataToAppendTo, key) {
    arrayToAppend.forEach((item) => {
        formDataToAppendTo.append(key, item);
    });
}

export function convertObjToFormData(obj, convertArraysToList=false) {
    var formData = new FormData();

    for (var key in obj) {
        if (convertArraysToList === true && Array.isArray(obj[key])) {
            appendArrayToFormData(obj, formData, key)
            continue;
        }

        formData.append(key, obj[key]);
    }
    
    return formData;
}